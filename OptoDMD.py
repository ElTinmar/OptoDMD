from Microscope import TwoPhoton, ImageReceiver
from daq import LabJackU3LV, myArduino
from LED import LEDD1B, LEDWidget
from DMD import DMD, ImageSender
from camera_tools import CameraWidget, XimeaCamera
from PyQt5.QtWidgets import QApplication
from alignment_tools import AlignAffine2D
from image_tools import ROISelectorWidget
import sys


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
    LABJACK_PWM_CHANNEL = 5

    receiver = ImageReceiver(ZMQ_ADDRESS)
    cam = XimeaCamera()
    daio = LabJackU3LV()
    led = LEDD1B(daio, pwm_channel=LABJACK_PWM_CHANNEL, name = 'red')

    camera_widget = CameraWidget(cam)
    two_photon_widget = TwoPhoton(receiver)
    led_widget = LEDWidget(led_drivers=[led])
    dmd_widget = DMD(screen_num=SCREEN_DMD)

    window = OptoDMD(camera_widget,two_photon_widget,led_widget,dmd_widget)

    app = QApplication(sys.argv)
    window.show()
    app.exec()
