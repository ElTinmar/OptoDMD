from DrawMasks import DrawPolyMask, Bla
from PyQt5.QtWidgets import QApplication
import sys
import cv2

image = cv2.imread('toy_data/image_00.jpg')

app = QApplication(sys.argv)
cam = DrawPolyMask(image)
dmd = DrawPolyMask(image)
twop = DrawPolyMask(image)
window = Bla(
    dmd_mask_drawer=dmd, 
    cam_mask_drawer=cam, 
    twop_mask_drawer=twop
)
window.show()
app.exec()
