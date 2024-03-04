from DrawMasks_2 import DrawPolyMask, MaskManager
from PyQt5.QtWidgets import QApplication
import sys
import cv2
import numpy as np

image = cv2.imread('toy_data/image_00.jpg')
transformations = np.tile(np.eye(3), (3,3,1,1))
app = QApplication(sys.argv)

cam = DrawPolyMask(image)
dmd = DrawPolyMask(image)
twop = DrawPolyMask(image)
window = MaskManager([cam, dmd, twop], ["Camera", "DMD", "Two Photon"], transformations)
window.show()

app.exec()
