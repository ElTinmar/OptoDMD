from daq import LabJackU3LV, myArduino
from LED import LEDD1B, LEDWidget
from PyQt5.QtWidgets import QApplication
import sys

daio = LabJackU3LV()
ardu = myArduino("/dev/ttyUSB0")
led1 = LEDD1B(ardu, pwm_channel=11)
led2 = LEDD1B(ardu, pwm_channel=13)


led1.set_intensity(0.5)
led1.on()
led1.set_intensity(0.75)

led1.off()

led1.pulse(duration_ms=1000)

app = QApplication(sys.argv)
window = LEDWidget(led_drivers=[led1, led2])
window.show()
sys.exit(app.exec())