from daq import DigitalAnalogIO
import time

class LEDD1B:
    '''Control a Thorlabs LED driver for optogenetics stimulation using PWM'''

    def __init__(
            self, 
            DAIO: DigitalAnalogIO, 
            pwm_frequency: float = 1000, 
            pwm_channel: int = 5
        ) -> None:

        self.DAIO = DAIO
        self.pwm_frequency = pwm_frequency
        self.pwm_channel = pwm_channel 
        self.intensity = 0
        self.started = False

    def set_intensity(self, intensity: float) -> None:

        if not (0 <= intensity <= 1):
            ValueError("intensity should be between 0 and 1")

        if self.started:
            self.DAIO.pwm_stop()
            
        self.intensity = intensity
        self.DAIO.pwm_configure(channel=self.pwm_channel, duty_cycle=intensity, frequency=self.pwm_frequency)

        if self.started:
            self.DAIO.pwm_start()
    
    def on(self):
        self.started = True
        self.DAIO.pwm_start()

    def off(self):
        self.DAIO.pwm_stop()
        self.started = False

    def pulse(self, duration_ms: int = 1000):
        if self.started:
            raise RuntimeError('Already ON')

        self.DAIO.pwm_start()
        time.sleep(duration_ms/1000.0)
        self.DAIO.pwm_stop()