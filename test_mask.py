from DrawMasks_2 import  MaskManager, DrawPolyMaskOpto, DrawPolyMaskOptoDMD
from DMD import DMD
from camera_tools import CameraPreview, CameraControl, RandomCam, OpenCV_Webcam
from PyQt5.QtWidgets import QApplication
import sys
import cv2
import numpy as np

image = cv2.imread('toy_data/image_00.jpg')
transformations = np.tile(np.eye(3), (3,3,1,1))
#transformations[0,1,0,0] = 2.0
DMD_HEIGHT = 2560//2
DMD_WIDTH = 1440//2

app = QApplication(sys.argv)
webcam = OpenCV_Webcam()
webcam_controls = CameraControl(webcam)
dmd_display = DMD(screen_num=2)
cam_mask = DrawPolyMaskOpto(image)
dmd_mask = DrawPolyMaskOptoDMD(DMD_HEIGHT, DMD_WIDTH)
twop_mask = DrawPolyMaskOpto(image)
window = MaskManager([cam_mask, dmd_mask, twop_mask], ["Camera", "DMD", "Two Photon"], transformations)

dmd_mask.DMD_update.connect(dmd_display.update_image)
webcam_controls.image_ready.connect(cam_mask.set_image)

webcam_controls.show()
window.show()
app.exec()
