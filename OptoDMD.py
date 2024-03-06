from Microscope import ImageSender
from DrawMasks import  MaskManager, DrawPolyMaskOpto, DrawPolyMaskOptoDMD
from daq import LabJackU3LV, myArduino
from LED import LEDD1B, LEDWidget
from DMD import DMD
#from camera_tools import XimeaCamera, CameraControl
from camera_tools import CameraControl, OpenCV_Webcam
from PyQt5.QtWidgets import QApplication
import sys
import numpy as np

if __name__ == "__main__":

    O1_263 = "192.168.236.75"
    PORT = "5555"
    ZMQ_ADDRESS= "tcp://" + O1_263 + ":" + PORT
    SCREEN_DMD = 1
    DMD_HEIGHT = 1920
    DMD_WIDTH = 1080

    app = QApplication(sys.argv)

    # Communication with ScanImage
    twop_sender = ImageSender(ZMQ_ADDRESS)
    

    # Camera 
    #cam = XimeaCamera()
    cam = OpenCV_Webcam()
    camera_controls = CameraControl(cam)
    camera_controls.show()

    '''
    # Control LEDs
    daio = LabJackU3LV()
    #daio = myArduino("/dev/ttyUSB0")
    led = LEDD1B(daio, pwm_channel=6, name = "465 nm") 
    led_widget = LEDWidget(led_drivers=[led])
    led_widget.show()
    '''

    # Control DMD
    dmd_widget = DMD(screen_num=SCREEN_DMD)

    # Masks
    cam_mask = DrawPolyMaskOpto()
    dmd_mask = DrawPolyMaskOptoDMD(DMD_HEIGHT, DMD_WIDTH)
    twop_mask = DrawPolyMaskOpto()

    transformations = np.tile(np.eye(3), (3,3,1,1))
    transformations[0,1] = np.array([[3.05, -0.041, -441.7],[0.041, 3.07, 1455.99],[0, 0 ,1]])
    transformations[1,0] = np.linalg.inv(transformations[0,1])
    masks = MaskManager([cam_mask, dmd_mask, twop_mask], ["Camera", "DMD", "Two Photon"], transformations)
    masks.show()

    # connect signals and slots
    dmd_mask.DMD_update.connect(dmd_widget.update_image)
    camera_controls.image_ready.connect(cam_mask.set_image)
    twop_sender.signal.image_ready.connect(twop_mask.set_image)

    app.exec()
