from Microscope import ScanImage
from DrawMasks import  MaskManager, DrawPolyMaskOpto2P, DrawPolyMaskOptoDMD, DrawPolyMaskOptoCam
from daq import LabJackU3LV
from LED import LEDD1B, LEDWidget
from DMD import DMD
from camera_tools import CameraControl, OpenCV_Webcam
from PyQt5.QtWidgets import QApplication
from config import *

import sys
import numpy as np
from image_tools import DrawPolyMask
import json

if __name__ == "__main__":

    # calibration file
    transformations = np.tile(np.eye(3), (3,3,1,1))
    try:
        with open('calibration.json', 'r') as f:
            calibration = json.load(f)

        # 0: cam, 1: dmd, 2: twop
        transformations[0,1] = np.asarray(calibration["cam_to_dmd"])
        transformations[0,2] = np.asarray(calibration["cam_to_twop"])
        transformations[1,0] = np.asarray(calibration["dmd_to_cam"])
        transformations[1,2] = np.asarray(calibration["dmd_to_twop"])
        transformations[2,0] = np.asarray(calibration["twop_to_cam"])
        transformations[2,1] = np.asarray(calibration["twop_to_dmd"])
    except:
        print("calibration couldn't be loaded, defaulting to identity")
   
    app = QApplication(sys.argv)

    # Communication with ScanImage
    scan_image = ScanImage(PROTOCOL, HOST, PORT)

    # Camera 
    if XIMEA_INDEX:
        from camera_tools import XimeaCamera
        cam = XimeaCamera(XIMEA_INDEX)
        cam.set_height(CAM_HEIGHT)
        cam.set_width(CAM_WIDTH)
    else:
        cam = OpenCV_Webcam(WEBCAM_INDEX)

    camera_controls = CameraControl(cam)
    # disable ROI controls 
    camera_controls.height_spinbox.setDisabled(True)
    camera_controls.width_spinbox.setDisabled(True)
    camera_controls.offsetX_spinbox.setDisabled(True)
    camera_controls.offsetY_spinbox.setDisabled(True)
    camera_controls.show()

    # Control LEDs
    if USE_LABJACK:
        daio = LabJackU3LV()
        led = LEDD1B(daio, pwm_channel=PWM_CHANNEL, name = "465 nm") 
        led_widget = LEDWidget(led_drivers=[led])
        led_widget.show()

    # Control DMD
    dmd_widget = DMD(screen_num=SCREEN_DMD)

    # Masks
    cam_drawer = DrawPolyMask(np.zeros((CAM_HEIGHT,CAM_WIDTH)))
    dmd_drawer = DrawPolyMask(np.zeros((DMD_HEIGHT,DMD_WIDTH)))
    twop_drawer = DrawPolyMask(np.zeros((TWOP_HEIGHT,TWOP_WIDTH)))

    cam_mask = DrawPolyMaskOptoCam(cam_drawer, camera_controls)
    dmd_mask = DrawPolyMaskOptoDMD(dmd_drawer, dmd_widget)
    twop_mask = DrawPolyMaskOpto2P(twop_drawer, scan_image)

    masks = MaskManager([cam_mask, dmd_mask, twop_mask], ["Camera", "DMD", "Two Photon"], transformations)
    masks.show()

    # connect signals and slots
    masks.mask_expose.connect(dmd_mask.expose)
    masks.clear_dmd.connect(dmd_mask.clear)

    app.exec()
