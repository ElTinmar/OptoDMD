# for Arduino, you can use pyFirmata 
# https://pyfirmata.readthedocs.io/en/latest/ 

# LabJack Documentation can be found here:
# https://github.com/labjack/LabJackPython/blob/master/Examples/workingWithModbus.py
# https://labjack.com/pages/support?doc=%2Fsoftware-driver%2Fdirect-modbus-tcp%2Fud-modbus-old-deprecated%2F
# https://files.labjack.com/datasheets/LabJack-U3-Datasheet.pdf

# TODO National Instruments ?

import u3
from pyfirmata import Arduino
from typing import Protocol

class DigitalAnalogIO(Protocol):

    def digitalRead(self, channel: int) -> float:
        ...

    def digitalWrite(self, channel: int, val: bool):
        ...

    def pwm_configure(self, channel: int, duty_cycle: float, frequency: float) -> None:
        ...

    def pwm_start(self) -> None:
        ...

    def pwm_stop(self) -> None:
        ...
        
    def analogRead(self, channel: int) -> float:
        ...

    def analogWrite(self, channel: int, val: float) -> None:
        ...

    def close(self) -> None:
        ...

class myArduino:

    # PWM frequency is around 490Hz on most pins, 
    # and 980Hz on pin 5 and 6

    def __init__(self, board_id: str) -> None:
        self.device = Arduino(board_id)
        self.pwm_pin = None
        self.pwm_pin_number = -1
        self.dc_value = 0

    def digitalRead(self, channel: int) -> float:
        pin = self.device.get_pin(f'd:{channel}:i')       
        val = pin.read()  
        self.device.taken['digital'][channel] = False
        return val

    def digitalWrite(self, channel: int, val: bool):
        pin = self.device.get_pin(f'd:{channel}:o')
        pin.write(val)
        self.device.taken['digital'][channel] = False

    def pwm_configure(self, channel: int, duty_cycle: float, frequency: float) -> None:
        print('frequency was ignored. Most ports use 490Hz, port 5 and 6 use 980Hz')
        self.dc_value = duty_cycle
        self.pwm_pin = self.device.get_pin(f'd:{channel}:p')
        self.pwm_pin_number = channel

    def pwm_start(self) -> None:
        self.pwm_pin.write(self.dc_value)

    def pwm_stop(self) -> None:
        self.pwm_pin.write(0)
        self.device.taken['digital'][self.pwm_pin_number] = False
        self.pwm_pin = None
        self.pwm_pin_number = -1
        
    def analogRead(self, channel: int) -> float:
        pin = self.device.get_pin(f'a:{channel}:i')
        val = pin.read()
        self.device.taken['analog'][channel] = False
        return val

    def analogWrite(self, channel: int, val: float) -> None:
        # Can not do analog write, the arduino does not have a DAC
        print("""The arduino does not have a DAC, no analog writing. 
              Consider hooking a capacitor on a PWM output instead""")

    def close(self) -> None:
        self.device.exit()

class LabJackU3LV:
    '''
    Use LabJack to read and write from a single pin at a time.
    Supports Analog input (FIOs) and output (DACs), digital
    input and output (FIOs), as well as PWM (FIOs). 
    '''
    
    # Analog outputs (they can also do input, but I decided to ignore that)
    # 10 bit resolution
    # [0.04V, 4.95V]
    DAC0 = 5000
    DAC1 = 5002

    # Digital Input/Output
    DIO0 = 6000
    DIO1 = 6001
    DIO2 = 6002
    DIO3 = 6003
    DIO4 = 6004
    DIO5 = 6005
    DIO6 = 6006
    DIO7 = 6007

    # 12 bits resolution
    # single-ended: [0V, 2.44V]
    # differential: [-2.44V, 2.44V] 
    # special: [0V, 3.6V] 
    AIN0 = 0
    AIN1 = 2
    AIN2 = 4
    AIN3 = 6
    AIN4 = 8
    AIN5 = 10
    AIN6 = 12
    AIN7 = 14

    # configure FIO as analog or digital
    # bitmask: 1=Analog, 0=digital
    FIO_ANALOG = 50590

    channels = {
        'AnalogInput': [AIN0,AIN1,AIN2,AIN3,AIN4,AIN5,AIN6,AIN7],
        'AnalogOutput': [DAC0,DAC1],
        'DigitalInputOutput': [DIO0,DIO1,DIO2,DIO3,DIO4,DIO5,DIO6,DIO7]
    }

    TIMER_CLOCK_BASE = 7000
    TIMER_CLOCK_DIVISOR = 7002
    NUM_TIMER_ENABLED = 50501
    TIMER_PIN_OFFSET = 50500
    TIMER_CONFIG = 7100
    TIMER_MODE_16BIT = 0
    TIMER_MODE_8BIT = 1

    CLOCK: int = 48 # I'm only using the 48MHz clock with divisors enabled 
        
    def __init__(self) -> None:
        self.device = u3.U3()
        self.timer_mode = 0
        self.dc_value = 65535

    def analogWrite(self, channel: int, val: float) -> None:
        self.device.writeRegister(self.channels['AnalogOutput'][channel], val)

    def analogRead(self, channel: int) -> float:
        self.device.writeRegister(self.FIO_ANALOG, channel**2) # set channel as analog
        return self.device.readRegister(self.channels['AnalogInput'][channel])
    
    def digitalWrite(self, channel: int, val: bool):
        self.device.writeRegister(self.FIO_ANALOG, 0) # set channel as digital
        self.device.writeRegister(self.channels['DigitalInputOutput'][channel], val)

    def digitalRead(self, channel: int) -> float:
        self.device.writeRegister(self.FIO_ANALOG, 0) # set channel as digital
        return self.device.readRegister(self.channels['DigitalInputOutput'][channel])
    
    def pwm_configure(self, channel: int = 4, duty_cycle: float = 0.5, frequency: float = 732.42) -> None:
        # duty_cycle: fraction of time signal is HIGH

        if not (0 <= duty_cycle <= 1):
            raise ValueError('duty_cycle should be between 0 and 1')

        if frequency > 187_500:
            raise ValueError('max frequency at 48MHz is 187_500 Hz')
        elif frequency < 2.861:
            raise ValueError('min frequency at 48MHz is 2.861 Hz')
         
        if frequency > 732.42:
            self.timer_mode = self.TIMER_MODE_8BIT
            div = 2**8
        else:
            self.timer_mode = self.TIMER_MODE_16BIT
            div = 2**16

        # make sure digital value is 0
        self.digitalWrite(channel,0)
    
        # divisor should be in the range 0-255, 0 corresponds to a divisor of 256
        timer_clock_divisor = int( (self.CLOCK * 1e6)/(frequency * div) )
        if timer_clock_divisor == 256: timer_clock_divisor = 0 

        # set the timer clock to 48 MHz with divisor (correspond to register value of 6)
        self.device.writeRegister(self.TIMER_CLOCK_BASE, 6)

        # set divisor
        self.device.writeRegister(self.TIMER_CLOCK_DIVISOR, timer_clock_divisor)

        # Pin offset (FIO) 
        self.device.writeRegister(self.TIMER_PIN_OFFSET, channel) 

        # 16 bit value for duty cycle
        self.dc_value = int(65535*(1-duty_cycle))
    
    def pwm_start(self) -> None:

        # enable Timer0
        self.device.writeRegister(self.NUM_TIMER_ENABLED, 1)

        # Configure the timer for 16-bit PWM
        self.device.writeRegister(self.TIMER_CONFIG, [self.timer_mode, self.dc_value]) 

    def pwm_stop(self) -> None:
        
        # always low
        self.device.writeRegister(self.TIMER_CONFIG, [self.timer_mode, 65535]) 

        # disable Timer0 
        self.device.writeRegister(self.NUM_TIMER_ENABLED, 0)

    def close(self) -> None:

        self.device.close()

