from Microscope import ImageSender
from DrawMasks import  MaskManager, DrawPolyMaskOpto, DrawPolyMaskOptoDMD
from daq import LabJackU3LV, myArduino
from LED import LEDD1B, LEDWidget
from DMD import DMD
#from camera_tools import XimeaCamera, CameraControl
from camera_tools import CameraControl, OpenCV_Webcam
from PyQt5.QtWidgets import QApplication
from alignment_tools import AlignAffine2D
import sys
import numpy as np
from typing import Tuple
from numpy.typing import NDArray
import cv2
from image_tools import regular_polygon, star

def create_calibration_pattern(div: int, height: int, width: int) -> NDArray:
    
    step = min(height,width)//div
    calibration_pattern = np.zeros((height,width,3), np.uint8)

    for y in range(height//(2*div),height,step):
        for x in range(width//(2*div),width,step):

            n = np.random.randint(3,7)
            s = np.random.randint(step//4, step//2)
            pos = np.array([x,y])
            theta = 2*np.pi*np.random.rand()

            if np.random.rand()>0.5:
                poly = regular_polygon(pos,n,theta,s)
            else:
                poly = star(pos,n,theta,s//2,s)

            calibration_pattern = cv2.fillPoly(calibration_pattern, pts=[poly], color=(255, 255, 255))
    
    return calibration_pattern

if __name__ == "__main__":

    SCREEN_DMD = 1
    DMD_HEIGHT = 1920
    DMD_WIDTH = 1080
    
    ## DMD to camera

    # 1. Project a pattern onto a slide, and image the slide on the camera

    pattern = create_calibration_pattern(5, DMD_HEIGHT, DMD_WIDTH)

    app = QApplication(sys.argv)

    # projector
    dmd_widget = DMD(screen_num=SCREEN_DMD)
    dmd_widget.update_image(pattern)

    # camera 
    #cam = XimeaCamera()
    cam = OpenCV_Webcam(-1)
    input("Press Enter to grab frame...")
    frame = cam.get_frame()
    cam.close()

    register = AlignAffine2D(pattern, frame.image)
    register.show()

    app.exec()

    with open('cam2dmd.npy', 'wb') as f:
        np.save(f, register.affine_transform)

    ## Camera to 2P

    cam = OpenCV_Webcam(-1)
    input("Press Enter to grab frame...")
    frame = cam.get_frame()
    cam.close()

    
