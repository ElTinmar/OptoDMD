from Microscope import TwoPhoton, ImageReceiver
from daq import LabJackU3LV, myArduino
from LED import LEDD1B, LEDWidget
from DMD import DMD
from camera_tools import CameraWidget, XimeaCamera
from PyQt5.QtWidgets import QApplication
from alignment_tools import AlignAffine2D
from image_tools import ROISelectorWidget
import sys

# TODO define protocols as input parameters instead of concrete classes ?

class OptoDMD():
    
    def __init__(
            self, 
            camera: CameraWidget,
            two_photon: TwoPhoton,
            led: LEDWidget,
            dmd: DMD
        ) -> None:

        self.camera = camera
        self.two_photon = two_photon
        self.led = led
        self.dmd = dmd
    
if __name__ == "__main__":

    o1_263 = "192.168.236.75"
    PORT = "5555"
    ZMQ_ADDRESS= "tcp://" + o1_263 + ":" + PORT
    SCREEN_DMD = 1

    app = QApplication(sys.argv)

    # Communication with ScanImage
    receiver = ImageReceiver(ZMQ_ADDRESS)
    two_photon_widget = TwoPhoton(receiver)

    # Camera 
    cam = XimeaCamera()
    camera_widget = CameraWidget(cam)

    # Control LEDs
    daio = LabJackU3LV()
    #daio = myArduino("/dev/ttyUSB0")
    led = LEDD1B(daio, pwm_channel=5, name = "465 nm") 
    led_widget = LEDWidget(led_drivers=[led])

    # Control DMD
    dmd_widget = DMD(screen_num=SCREEN_DMD)

    # 
    window = OptoDMD(camera_widget,two_photon_widget,led_widget,dmd_widget)
    window.show()
    
    app.exec()


# TODO inherit from mask, make three tabs, one for Camera, one for TwoPhoton, one for DMD 
# be 