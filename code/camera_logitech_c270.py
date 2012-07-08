import cv2.cv as cv
#Camera configuration

INTRINSICS_FILE = "Intrinsics.c270.xml"
DISTORTION_FILE = "Distortion.c270.xml"
C270_CAMERA_WIDTH = 1280
C270_CAMERA_HEIGHT = 720
CAMERA_WIDTH = C270_CAMERA_WIDTH
CAMERA_HEIGHT = C270_CAMERA_HEIGHT

def camera_init(capture):
    cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_WIDTH, C270_CAMERA_WIDTH)
    cv.SetCaptureProperty(capture,cv.CV_CAP_PROP_FRAME_HEIGHT, C270_CAMERA_HEIGHT)

#Final correction for focus length. Linear models obtained from tests (see R docs)
def camera_corrected_fx(posX):
    return 1456.138

#ejemplo solamente:
#    fx = 0.0
#    if posX < 320.0:
#        fx = 816.7156+0.2356*posX
#    elif posX <= 370.0:
#        fx = 4820.57-10.38*posX
#    else:
#         fx = 952.9760-0.1153*posX
#    return fx

