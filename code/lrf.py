
import sys
import serial
import time
from math import *

import cv2.cv as cv

#globals
# default, should be set when camera is initialized
CAMERA_WIDTH = 0
CAMERA_HEIGHT = 0

#camera config script
#from camera_creative_pd1170 import *
from camera_logitech_c270 import *

#options
capture_device=1
laser_controller_port='/dev/ttyACM0'
show_debug_images = True

#params
BETA = 70.568#Laser angle [degrees]
L = 6.35#Distance from focus to laser [cm]
LASER_TIME_ON=0.5# 0.2
FLIP_IMAGE = True

def dbg_image(name,image):
    if show_debug_images:
        cv.NamedWindow(name, cv.CV_WINDOW_AUTOSIZE)
        cv.ShowImage(name, image)

def capture_image(capture,mapx=None,mapy=None):
    img = cv.CloneImage(cv.QueryFrame(capture))

    #Flip
    if FLIP_IMAGE:
      img2 = cv.CloneImage(img)
      cv.Flip(img,img2,0)
      cv.Flip(img2,img,1)

    #undistort if calibration matrices were given
    if mapx!=None and mapy !=None:
        udimg = cv.CloneImage(img)
        cv.Remap(img,udimg,mapx,mapy)
        img = udimg

    return img

def init_capture_device(device=-1):
    print "init capture device"
    capture = cv.CreateCameraCapture (device)

    # check that capture device is OK
    if not capture:
        print "Error opening capture device"
        sys.exit (1)

    #call specific camera initialization
    camera_init(capture)

    #Get inital image to set parameters
    image = cv.QueryFrame(capture) #inital image

    CAMERA_WIDTH = cv.GetSize(image)[0]
    #print CAMERA_WIDTH
    CAMERA_HEIGHT = cv.GetSize(image)[1]
    #print CAMERA_HEIGHT

    #load calibration 
    intrinsics = cv.Load(INTRINSICS_FILE)
    distortion = cv.Load(DISTORTION_FILE)
    mapx = cv.CreateImage( cv.GetSize(image), cv.IPL_DEPTH_32F, 1 );
    mapy = cv.CreateImage( cv.GetSize(image), cv.IPL_DEPTH_32F, 1 );
    cv.InitUndistortMap( intrinsics, distortion, mapx, mapy );

    return capture,mapx,mapy

def setup_camera_window():
    cv.NamedWindow ('camera', cv.CV_WINDOW_AUTOSIZE)
    cv.MoveWindow ('camera', 10, 10)

def show_camera_and_wait_for_key(capture,timeout=5,mapx=None,mapy=None):
    img = capture_image(capture,mapx,mapy)
    size = cv.GetSize(img)
    centerx = size[0]/2
    centery = size[1]/2
    crosslen = 4
    cv.Line(img,(0,centery),(size[0],centery),cv.Scalar(255,255,0))
    cv.Line(img,(centerx,0),(centerx,size[1]),cv.Scalar(255,255,0))
    cv.Line(img,(centerx-crosslen,centery),(centerx+crosslen,centery),cv.Scalar(255,255,0),2)
    cv.Line(img,(centerx,centery-crosslen),(centerx,centery+crosslen),cv.Scalar(255,255,0),2)

    cv.ShowImage('camera',img)
    k = cv.WaitKey(timeout)
    return img,k

def show_camera_and_wait_until_keypressed(capture,mapx=None,mapy=None):
    cont = True
    while cont:
        img,key = show_camera_and_wait_for_key(capture,5,mapx,mapy)
        cont = key==-1

def show_camera_and_wait(capture,timeout,mapx=None,mapy=None):
    t = time.clock()+float(timeout)
    while time.clock() < t:
        show_camera_and_wait_for_key(capture,5,mapx,mapy)

def laser_off(laser_ctrl):
    laser_ctrl.write("-")

def laser_on(laser_ctrl):
    laser_ctrl.write("+")

def init_laser_controller(ctrl,baud_rate=9600):
    #inicializar arduino
    ser = serial.Serial(ctrl,baud_rate)
    if not ser:
        print "Error opening laser controller"
        sys.exit(2)

    laser_off(ser)
    return ser

#Returns the images with and without laser 
def get_images(capture,laser_ctrl,mapx=None,mapy=None):
    print "#take the first image"
    #take the first image
    img1 = capture_image(capture,mapx,mapy)

    print "#turn on laser, wait a bit to be sure the laser is on, and take the second image "
    #turn on laser, wait a bit to be sure the laser is on, and take the second image 
    laser_on(laser_ctrl)
    #can't simply sleep, frames must be processed
    #time.sleep(LASER_TIME_ON)
    t = time.clock()+LASER_TIME_ON
    while time.clock() < t:
        img2 = capture_image(capture,mapx,mapy)
        cv.WaitKey(10)

    print "#get second image"
    laser_off(laser_ctrl)
    print "ok"

    return img1,img2

#Shows the UI: camera, waits for input and retrieves on/off images
def show_camera_and_get_images(capture,laser_ctrl,mapx=None,mapy=None):
    while 1:
        img,k = show_camera_and_wait_for_key(capture,5,mapx,mapy)
        if k >= 0:
            img1, img2 = get_images(capture, laser_ctrl, mapx, mapy)
            cv.NamedWindow ('img1', cv.CV_WINDOW_AUTOSIZE)
            cv.NamedWindow ('img2', cv.CV_WINDOW_AUTOSIZE)

  	    cv.ShowImage('img1',img1)
            cv.ShowImage('img2',img2)

            cv.MoveWindow ('img1', 10, 10)
            cv.MoveWindow ('img2', 660, 10)
            return img1,img2


#smooths and convert to gray
def simplify(img):
    simg = cv.CloneImage(img)
    cv.Smooth(img,simg)
    imgg = cv.CreateImage(cv.GetSize(img), cv.IPL_DEPTH_8U, 1)
    cv.CvtColor(simg,imgg, cv.CV_RGB2GRAY)
    return imgg

#difference of simplified images. difference is smoothed, thresholded and eroded
def difference_image(img1,img2):
    print " simg1 = simplify(img1)"
    simg1 = simplify(img1)
    print " simg2 = simplify(img2)"
    simg2 = simplify(img2)

    #dbg_image('simg1',simg1)
    #dbg_image('simg2',simg2)

    #create image buffers
    img3 = cv.CreateImage(cv.GetSize(img2), cv.IPL_DEPTH_8U,1)
    simg3 = cv.CloneImage(img3)
    bitimage = cv.CreateImage(cv.GetSize(img2), cv.IPL_DEPTH_8U, 1)
    eimg3 = cv.CloneImage(bitimage)

    #process
    print " cv.AbsDiff(simg2,simg1,img3)"
    cv.AbsDiff(simg2,simg1,img3)
    print " cv.Smooth(img3,simg3)"
    cv.Smooth(img3,simg3)
    #dbg_image('simg3',simg3)
    # these threshold values must be calibrated
    #cv.Threshold(simg3,bitimage,16,255,cv.CV_THRESH_TOZERO_INV)
    print " cv.Threshold(simg3,bitimage,16,255,cv.CV_THRESH_BINARY)"
    cv.Threshold(simg3,bitimage,50,255,cv.CV_THRESH_BINARY)
    #dbg_image('bitimage',bitimage)
    print " cv.Erode(bitimage,eimg3)"
    cv.Erode(bitimage,eimg3)
    #dbg_image('eimg3',eimg3)
    return eimg3

#use moments over the difference image to get x,y of laser
def calculate_laser_position(img):
    print "calculating moments"
    moments = cv.Moments(cv.GetMat(img))
    posX = -1
    posY = -1
    area = cv.GetCentralMoment(moments,0,0)
    if area>0:
        moment10 = cv.GetSpatialMoment(moments,1,0)
        moment01 = cv.GetSpatialMoment(moments,0,1)
        posX = int(moment10/area)
        posY = int(moment01/area)

    return posX,posY,area

#vc: Position X of laser on detected image
#beta: laser/focus plane angle (this angle is internal to the config:
#  if config is Camera-Objective-Laser the angle is CLO
#L: Distance from Camera (center of lens - pinhole) to Laser
def calculate_distance(vc,beta,L):
    print "vc:"+str(vc)
    print "beta:"+str(beta)
    print "L:"+str(L)
    print "CW:"+str(CAMERA_WIDTH)
    vx =(CAMERA_WIDTH/2.0) - vc
    if vx==0: 
        vx=0.0001 #a sort of laplacian smoothing
    print "vx:"+str(vx)
     
    delta = atan(camera_corrected_fx(vc)/abs(vx))
    if vx>0:
        delta = pi-delta
    print "delta:"+str(delta)
    lambd = pi-radians(beta)-delta
    print "lambda:"+str(lambd)
    Dc = L*sin(radians(beta))/sin(lambd)
    print "Dc:"+str(Dc)
    return Dc

def measure_distance_from_images(img1,img2):
    print "differencing images"
    difimg = difference_image(img1,img2)
    print "calculating laser position"
    x,y,a = calculate_laser_position(difimg)
    #print [x,y,a]
    print "calculating distance"
    distance = calculate_distance(x,BETA,L)
    return distance,x,y,a

def result_image(img,posX,posY,distance):
    hScale=0.5;
    vScale=0.5;
    lineWidth=1;
    font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX|cv.CV_FONT_ITALIC,hScale,vScale,0,lineWidth);
    cv.PutText (img,("%0.2fcm"%distance),(10,20), font, cv.Scalar(0,255,255));
    cv.Circle(img,(posX,posY),15,cv.Scalar(0,255,0),2)
    cv.Circle(img,(posX,posY),2,cv.Scalar(0,255,0),2)
    return img

#single measure UI 
def single_measure_gui():
    #setup
    capture,mapx,mapy=init_capture_device(capture_device)
    laser_controller=init_laser_controller(laser_controller_port)
    setup_camera_window()

    #get images and calculate distance
    img1,img2 = show_camera_and_get_images(capture,laser_controller,mapx,mapy)
    distance,posX,posY,area = measure_distance_from_images(img1,img2)

    #output
    r_img = result_image(img2,posX,posY,distance)
    cv.MoveWindow ('res', 10, 10)
    cv.ShowImage ('res',r_img)
    cv.SaveImage("img1.jpg",img1)
    cv.SaveImage("img2.jpg",r_img)
    print "%0.2f,%d,%d,%d" % (distance,posX,posY,area)

    cv.WaitKey(50000)

#single measure, command line
def single_measure():
    #setup
    capture,mapx,mapy=init_capture_device(capture_device)
    laser_controller=init_laser_controller(laser_controller_port)

    #get images and calculate distance
    img1, img2 = get_images(capture, laser_controller, mapx, mapy)
    distance,posX,posY,area = measure_distance_from_images(img1,img2)

    #output
    cv.SaveImage("img2.jpg",result_image(img2,posX,posY,distance))
    print "%0.2f,%d,%d,%d" % (distance,posX,posY,area)
    
    return (distance,posX,posY,area)


#if lrf used stand alone (not as library), makes a single measure, optionally on a UI
if __name__ == '__main__':
    print sys.argv
    if len(sys.argv)>1 and sys.argv[1]=="-v":
        single_measure_gui()
    else:
        single_measure()

    
