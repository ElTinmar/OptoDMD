from daq import LabJackU3LV
from LED import LEDD1B

daio = LabJackU3LV()
led = LEDD1B(daio, pwm_channel=4)

led.set_intensity(0.5)
led.on()
led.set_intensity(0.75)

led.off()

led.pulse(duration_ms=1000)