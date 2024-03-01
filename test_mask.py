from DrawMasks import DrawPolyMask
from PyQt5.QtWidgets import QApplication
import sys
import cv2

image = cv2.imread('/home/martin/Code/alignment_tools/toy_data/image_00.jpg')

app = QApplication(sys.argv)
window = DrawPolyMask()
window.set_image(image)
window.show()
app.exec()
