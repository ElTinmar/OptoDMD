# https://github.com/labjack/LabJackPython/blob/master/Examples/workingWithModbus.py
# https://labjack.com/pages/support?doc=%2Fsoftware-driver%2Fdirect-modbus-tcp%2Fud-modbus-old-deprecated%2F

import u3
from typing import Protocol

registers = {
    'DAC0': 5000,
    'DAC1': 5002
}

d = u3.U3()
d.writeRegister(registers["DAC0"], 0)
d.writeRegister(registers["DAC0"], 3.0)

class DigitalAnalogIO(Protocol):

    def digitalRead(self) -> bool:
        ...

    def digitalWrite(self, val: bool) -> None:
        ...

    def pwm(self, duty_cycle: float, frequency: float) -> None:
        ...
        
    def analogRead(self) -> float:
        ...

    def analogWrite(self, val: float) -> None:
        ...

class LabJackU3:

    registers = {
        'DAC0': 5000,
        'DAC1': 5002,
        'TimerClockBase': 7000,
        'TimerClockDiviser': 7002,
    }
        
    def __init__(self) -> None:
        self.device = u3.U3()

    def write(self, register: str, val):
        self.device.writeRegister(self.registers[register], val)

    def read(self, register) -> float:
        return self.device.readRegister()
    
    def pwm(self, duty_cycle: float, frequency: float):
        # duty_cycle between zero and one

        timer_clock_base = 48
        timer_clock_divisor = int( (timer_clock_base * 1e6)/(frequency * 65536) )

        # set the timer clock to be 48 MHz
        d.writeRegister(7000, timer_clock_base)

        # set divisor of 15
        d.writeRegister(7002, timer_clock_divisor)

        # Pin offset (FIO) 
        d.writeRegister(50500, 4) # not sure about that 

        # enable 1 timer 
        d.writeRegister(50501, 1)

        # Configure the timer for PWM
        d.writeRegister(7100, [0, 65535*duty_cycle]) # what does that do ? First 0 then duty cycle ?
    

class LEDDB1:

    def __init__(self, DAIO: DigitalAnalogIO) -> None:
        self.DAIO = DAIO

    def on(self):
        self.DAIO.digitalWrite(True)

    def off(self):
        self.DAIO.digitalWrite(False)

    def pwm(self, duty_cycle: float, frequency: float):
        pass
