from lrf import *


capture,mapx,mapy=init_capture_device(capture_device)
laser_controller=init_laser_controller(laser_controller_port)
setup_camera_window()

hScale=0.5;
vScale=0.5;
lineWidth=1;
font = cv.cvInitFont(cv.CV_FONT_HERSHEY_SIMPLEX|cv.CV_FONT_ITALIC,hScale,vScale,0,lineWidth);
highgui.cvNamedWindow("output", highgui.CV_WINDOW_AUTOSIZE)
highgui.cvMoveWindow("output",700,10)
  
cont = True

while cont:
    show_camera_and_wait_until_keypressed(capture)
    img1,img2 = get_images(capture,laser_controller,mapx,mapy)
    distance,posX,posY,area = measure_distance_from_images(img1,img2)

    strdist = ("%0.1fcm"%distance)
    print strdist

    cv.cvPutText (img2,strdist,cv.cvPoint(10,20), font, cv.cvScalar(0,255,255));
    cv.cvCircle(img2,cv.cvPoint(posX,posY),15,cv.cvScalar(0,255,255),2)
    cv.cvCircle(img2,cv.cvPoint(posX,posY),2,cv.cvScalar(0,255,255),2)
    highgui.cvShowImage ('output', img2)


