# https://github.com/labjack/LabJackPython/blob/master/Examples/workingWithModbus.py
# https://labjack.com/pages/support?doc=%2Fsoftware-driver%2Fdirect-modbus-tcp%2Fud-modbus-old-deprecated%2F

import u3

registers = {
    'DAC0': 5000,
    'DAC1': 5002
}

d = u3.U3()
d.writeRegister(registers["DAC0"], 0)
d.writeRegister(registers["DAC0"], 3.0)

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
    

class LEDDB1:

    def on(self):
        pass

    def off(self):
        pass

    def pwm(self, duty_cycle: float, frequency: float):
        pass
