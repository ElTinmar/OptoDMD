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

    # Project a pattern onto a slide, and image the slide on the camera

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

    register = AlignAffine2D(pattern, frame.image)
    register.show()

    with open('cam2dmd.npy', 'wb') as f:
        np.save(f, register.affine_transform)

    ## Camera to 2P
    
    # put a slide with some structure under the microscope
    # show some light and take an epifluorescence image with the camera
    # The slide should be ideally very thin and auto-fluorescent
    
    # use the DMD to expose the image
    dmd_widget.update_image(255*np.ones((DMD_HEIGHT,DMD_WIDTH,3), np.uint8))
    frame = cam.get_frame()

    # Then take picture from the same sample with the two photon microscope
    N = 5 
    zoom = np.linspace(1,10,N)
    T = np.zeros(3,3,N)
    for idx, z in enumerate(zoom):
        # send zoom value to scanimage over zeromq, and acquire frames
        # for each frame do the control point registration
        twop_image = microscope.get_image() # TODO
        register = AlignAffine2D(twop_image, frame.image)
        register.show()
        T[:,:,idx] = register.affine_transform

    # TODO maybe plot calibration with matplotlib 
    A = np.vstack([zoom, np.ones(len(zoom))]).T # add intercept 
    M = np.zeros(3,3,2)
    for i in range(3):
        for j in range(3):
            M[i,j,:] = np.linalg.lstsq(A, T[i,j,:], rcond=None)[0]

    with open('cam2twop.npy', 'wb') as f:
        np.save(f, M)

    # to get the transformation matrix for a given zoom level
    def tform(zoom: float, M: NDArray):
        return zoom*M[:,:,0] + M[:,:,1]

    app.exec()