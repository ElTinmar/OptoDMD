from Microscope import ImageSender
from DrawMasks import  MaskManager, DrawPolyMaskOpto, DrawPolyMaskOptoDMD
from daq import LabJackU3LV, myArduino
from LED import LEDD1B, LEDWidget
from DMD import DMD
from camera_tools import XimeaCamera, CameraControl
from PyQt5.QtWidgets import QApplication
from alignment_tools import AlignAffine2D
import sys
import numpy as np

if __name__ == "__main__":

    O1_263 = "192.168.236.75"
    PORT = "5555"
    ZMQ_ADDRESS= "tcp://" + O1_263 + ":" + PORT
    SCREEN_DMD = 2
    TRANSFORMATIONS = np.tile(np.eye(3), (3,3,1,1))
    DMD_HEIGHT = 2560//2
    DMD_WIDTH = 1440//2

    app = QApplication(sys.argv)

    # Communication with ScanImage
    twop_sender = ImageSender(ZMQ_ADDRESS)

    # Camera 
    cam = XimeaCamera()
    camera_controls = CameraControl(cam)

    # Control LEDs
    daio = LabJackU3LV()
    #daio = myArduino("/dev/ttyUSB0")
    led = LEDD1B(daio, pwm_channel=5, name = "465 nm") 
    led_widget = LEDWidget(led_drivers=[led])

    # Control DMD
    dmd_widget = DMD(screen_num=SCREEN_DMD)

    # Masks
    cam_mask = DrawPolyMaskOpto()
    dmd_mask = DrawPolyMaskOptoDMD(DMD_HEIGHT, DMD_WIDTH)
    twop_mask = DrawPolyMaskOpto()
    masks = MaskManager([cam_mask, dmd_mask, twop_mask], ["Camera", "DMD", "Two Photon"], TRANSFORMATIONS)

    # connect signals and slots
    dmd_mask.DMD_update.connect(dmd_widget.update_image)
    camera_controls.image_ready.connect(cam_mask.set_image)
    twop_sender.signal.image_ready.connect(twop_mask.set_image)

    # show windows
    camera_controls.show()
    masks.show()
    led_widget.show()
    dmd_mask.show()

    app.exec()
