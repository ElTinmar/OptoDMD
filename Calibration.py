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

def regular_polygon(center: NDArray, n: int, theta: float, scale: int) -> NDArray:
    
    polygon = []
    angle_increment = 2*np.pi/n
    for i in range(n):
        alpha = theta+i*angle_increment
        x, y = np.cos(alpha), np.sin(alpha)
        new_point = center + scale * np.array([x, y])
        polygon.append(new_point)
    
    return np.asarray(polygon, dtype=np.int32)

def star(center: NDArray, n: int, theta: float, scale_0: int, scale_1: int) -> NDArray:
    
    angle_increment = 2*np.pi/n
    polygon_out = regular_polygon(center, n, theta, scale_1)
    polygon_in = regular_polygon(center, n, theta+angle_increment/2, scale_0)
    polygon = [val for pair in zip(polygon_out, polygon_in) for val in pair]

    return np.asarray(polygon, dtype=np.int32)

if __name__ == "__main__":

    DMD_HEIGHT = 2560
    DMD_WIDTH = 1440
    SCREEN_DMD = 2
    
    ## DMD to camera

    # 1. Project a pattern onto a slide, and image the slide on the camera

    div = 5
    step = min(DMD_HEIGHT,DMD_WIDTH)//div

    calibration_pattern = np.zeros((DMD_HEIGHT,DMD_WIDTH,3), np.uint8)
    for y in range(DMD_HEIGHT//(2*div),DMD_HEIGHT,step):
        for x in range(DMD_WIDTH//(2*div),DMD_WIDTH,step):

            n = np.random.randint(3,7)
            s = np.random.randint(step//4, step//2)
            pos = np.array([x,y])
            theta = 2*np.pi*np.random.rand()

            if np.random.rand()>0.5:
                poly = regular_polygon(pos,n,theta,s)
            else:
                poly = star(pos,n,theta,s//2,s)

            calibration_pattern = cv2.fillPoly(calibration_pattern, pts=[poly], color=(255, 255, 255))


    app = QApplication(sys.argv)

    # projector
    dmd_widget = DMD(screen_num=SCREEN_DMD)
    dmd_widget.update_image(calibration_pattern)

    # camera 
    #cam = XimeaCamera()
    cam = OpenCV_Webcam()

    input("Press Enter to grab frame...")
    frame = cam.get_frame()

    register = AlignAffine2D(calibration_pattern[:,:,0], frame.image[:,:,0])
    register.show()

    app.exec()

    ## Camera to 2P