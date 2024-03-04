from DrawMasks_2 import  MaskManager, DrawPolyMaskOpto
from PyQt5.QtWidgets import QApplication
import sys
import cv2
import numpy as np

image = cv2.imread('toy_data/image_00.jpg')
transformations = np.tile(np.eye(3), (3,3,1,1))
#transformations[0,1,0,0] = 2.0

app = QApplication(sys.argv)

cam = DrawPolyMaskOpto(image)
dmd = DrawPolyMaskOpto(image)
twop = DrawPolyMaskOpto(image)
window = MaskManager([cam, dmd, twop], ["Camera", "DMD", "Two Photon"], transformations)
window.show()
cam.show()

app.exec()
