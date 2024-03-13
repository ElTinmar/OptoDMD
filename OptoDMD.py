from Microscope import ImageSender, ScanImage
from DrawMasks import  MaskManager, DrawPolyMaskOpto, DrawPolyMaskOptoDMD
from daq import LabJackU3LV, myArduino
from LED import LEDD1B, LEDWidget
from DMD import DMD
from camera_tools import XimeaCamera, CameraControl
from camera_tools import CameraControl, OpenCV_Webcam
from PyQt5.QtWidgets import QApplication
import sys
import numpy as np
from image_tools import DrawPolyMask

if __name__ == "__main__":

    # zmq settings
    PROTOCOL = "tcp://"
    HOST = "o1-317"
    PORT = 5555
    
    # dmd settings
    SCREEN_DMD = 1
    DMD_HEIGHT = 1140
    DMD_WIDTH = 912

    # labjack settingss
    PWM_CHANNEL = 6

    # calibration files
    with open("cam2dmd.npy", 'rb') as f:
        calibration_cam_to_dmd = np.load(f)

    with open("cam2twop.npy", 'rb') as f:
        calibration_cam_to_twop = np.load(f)

    app = QApplication(sys.argv)

    # Communication with ScanImage
    scan_image = ScanImage(PROTOCOL, HOST, PORT)
    twop_sender = ImageSender(scan_image)

    # Camera 
    cam = XimeaCamera()
    camera_controls = CameraControl(cam)
    camera_controls.show()

    # Control LEDs
    daio = LabJackU3LV()
    #daio = myArduino("/dev/ttyUSB0")
    led = LEDD1B(daio, pwm_channel=PWM_CHANNEL, name = "465 nm") 
    led_widget = LEDWidget(led_drivers=[led])
    led_widget.show()

    # Control DMD
    dmd_widget = DMD(screen_num=SCREEN_DMD)

    # Masks
    cam_drawer = DrawPolyMask(np.zeros((512,512)))
    dmd_drawer = DrawPolyMask(np.zeros((DMD_HEIGHT,DMD_WIDTH)))
    twop_drawer = DrawPolyMask(np.zeros((512,512)))

    cam_mask = DrawPolyMaskOpto(cam_drawer)
    dmd_mask = DrawPolyMaskOptoDMD(dmd_drawer)
    twop_mask = DrawPolyMaskOpto(twop_drawer)

    transformations = np.tile(np.eye(3), (3,3,1,1))
    transformations[0,1] = calibration_cam_to_dmd
    transformations[1,0] = np.linalg.inv(calibration_cam_to_dmd)
    transformations[0,2] = calibration_cam_to_twop
    transformations[2,0] = np.linalg.inv(calibration_cam_to_twop)

    masks = MaskManager([cam_mask, dmd_mask, twop_mask], ["Camera", "DMD", "Two Photon"], transformations)
    masks.show()

    # connect signals and slots
    dmd_mask.DMD_update.connect(dmd_widget.update_image)
    masks.mask_expose.connect(dmd_mask.expose)
    masks.clear_dmd.connect(dmd_mask.clear)
    camera_controls.image_ready.connect(cam_mask.set_image)
    twop_sender.scan_image.image_ready.connect(twop_mask.set_image)

    app.exec()

    twop_sender.stop()
