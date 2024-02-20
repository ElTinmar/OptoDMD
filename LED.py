from daq import DigitalAnalogIO
import time
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QSpinBox, QSlider, QListWidgetItem, QListWidget, QFileDialog, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from qt_widgets import NDarray_to_QPixmap,  LabeledSliderSpinBox, LabeledSpinBox
from typing import Protocol, List

class LEDDriver(Protocol):
    
    def set_intensity(self, intensity: float) -> None:
        ...

    def on(self) -> None:
        ...

    def off(self) -> None:
        ...

    def pulse(self, duration_ms: int) -> None:
        ...

class LEDD1B:
    '''Control a Thorlabs LED driver for optogenetics stimulation using PWM'''

    def __init__(
            self, 
            DAIO: DigitalAnalogIO, 
            pwm_frequency: float = 1000, 
            pwm_channel: int = 5,
            name: str = 'LED'
        ) -> None:

        self.DAIO = DAIO
        self.name = name
        self.pwm_frequency = pwm_frequency
        self.pwm_channel = pwm_channel 
        self.intensity = 1
        self.started = False

    def set_intensity(self, intensity: float) -> None:

        if not (0 <= intensity <= 1):
            ValueError("intensity should be between 0 and 1")
            
        self.intensity = intensity
        self.DAIO.pwm(channel=self.pwm_channel, duty_cycle=self.intensity, frequency=self.pwm_frequency)
    
    def on(self):
        self.started = True
        self.DAIO.pwm(channel=self.pwm_channel, duty_cycle=self.intensity, frequency=self.pwm_frequency)

    def off(self):
        self.DAIO.pwm(channel=self.pwm_channel, duty_cycle=0, frequency=self.pwm_frequency)
        self.started = False

    def pulse(self, duration_ms: int = 1000):
        if self.started:
            raise RuntimeError('Already ON')

        self.DAIO.pwm(channel=self.pwm_channel, duty_cycle=self.intensity, frequency=self.pwm_frequency)
        time.sleep(duration_ms/1000.0)
        self.DAIO.pwm(channel=self.pwm_channel, duty_cycle=0, frequency=self.pwm_frequency)


class DriverWidget(QWidget):
    
    def __init__(self, driver: LEDDriver, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.driver = driver
        self.declare_components()
        self.layout_components()

    def declare_components(self):

        self.name_label = QLabel(self)
        self.name_label.setText(self.driver.name)

        self.intensity_slider = LabeledSliderSpinBox(self)
        self.intensity_slider.setText('intensity (%)')
        self.intensity_slider.setRange(0, 100)
        self.intensity_slider.setValue(50)
        self.intensity_slider.valueChanged.connect(self.set_intensity)
        self.driver.set_intensity(0.5)

        self.on_button = QPushButton(self)
        self.on_button.setText('ON')
        self.on_button.clicked.connect(self.on)

        self.off_button = QPushButton(self)
        self.off_button.setText('OFF')
        self.off_button.clicked.connect(self.off)

        self.pulse_spinbox = LabeledSpinBox(self)
        self.pulse_spinbox.setText('pulse duration (ms)')
        self.pulse_spinbox.setRange(0, 100_000)
        self.pulse_spinbox.setValue(1000)
        
        self.pulse_button = QPushButton(self)
        self.pulse_button.setText('pulse')
        self.pulse_button.clicked.connect(self.pulse)

    def layout_components(self):
         
        main_layout = QHBoxLayout(self)
        main_layout.addStretch()
        main_layout.addWidget(self.name_label)
        main_layout.addWidget(self.intensity_slider)
        main_layout.addWidget(self.on_button)
        main_layout.addWidget(self.off_button)
        main_layout.addWidget(self.pulse_spinbox)
        main_layout.addWidget(self.pulse_button)
        main_layout.addStretch()

    def set_intensity(self, val: int):
        self.driver.set_intensity(val/100)

    def on(self):
        self.driver.on()

    def off(self):
        self.driver.off()

    def pulse(self):
        self.driver.pulse(duration_ms=self.pulse_spinbox.value())


class LEDWidget(QWidget):

    def __init__(self, led_drivers: List[LEDDriver], *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.led_drivers = led_drivers
        self.declare_components()
        self.layout_components()

    def declare_components(self):
        
        self.driver_widgets = []
        for driver in self.led_drivers:
            self.driver_widgets.append(DriverWidget(driver))

    def layout_components(self):
        
        main_layout = QVBoxLayout(self)
        main_layout.addStretch()
        for w in self.driver_widgets:
            main_layout.addWidget(w)
        main_layout.addStretch()