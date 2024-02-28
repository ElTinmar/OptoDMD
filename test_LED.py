from daq import LabJackU3LV, myArduino
from LED import LEDD1B, LEDWidget
from PyQt5.QtWidgets import QApplication
import sys

#daio = LabJackU3LV()
daio = myArduino("/dev/ttyUSB0")
led0 = LEDD1B(daio, pwm_channel=5, name = 'red')
led1 = LEDD1B(daio, pwm_channel=11, name = 'yellow')

'''
led1.set_intensity(0.5)
led1.on()
led1.set_intensity(0.75)
led1.off()
led1.pulse(duration_ms=1000)
'''

app = QApplication(sys.argv)
window = LEDWidget(led_drivers=[led0, led1])
window.show()
app.exec()
daio.close()
