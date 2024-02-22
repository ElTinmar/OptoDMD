from camera_tools import CameraWidget, XimeaCamera, Camera
from PyQt5.QtWidgets import QApplication
import sys

cam = XimeaCamera()
app = QApplication(sys.argv)
window = CameraWidget(cam)
window.show()
app.exec()
