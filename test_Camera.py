from camera_tools import CameraPreview, CameraControl, RandomCam, OpenCV_Webcam
#from camera_tools import XimeaCamera
from PyQt5.QtWidgets import QApplication
import sys
import numpy as np

app = QApplication(sys.argv)
#cam = XimeaCamera()
#cam = RandomCam((512,512), np.uint8)
cam = OpenCV_Webcam()

# Use control widgets to control the emission of frames
# This can be integrated in the main GUI
controls = CameraControl(cam)

# I am adding preview for fun
preview = CameraPreview(controls)
preview.show()

app.exec()
