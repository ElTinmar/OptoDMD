import zmq
import numpy as np
from numpy.typing import NDArray
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRunnable, QThreadPool, QObject
from PyQt5.QtWidgets import QLabel,  QWidget
from qt_widgets import NDarray_to_QPixmap
from image_tools import im2uint8
from typing import Callable
from camera_tools import FrameRingBuffer, BaseFrame, Frame


def deserialize(message: str) -> NDArray:
    '''deserialize string into numpy array'''

    image_num, image_time, data = message.split('|')
    image = [r.split(',') for r in data.split(';')]
    return BaseFrame(int(image_num), float(image_time), np.array(image, dtype = np.float32))

class ScanImage(QObject):

    def __init__(self, protocol: str, host: str, port: int, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        self.context = zmq.Context()

        # get images from scanimage
        address_image = protocol + host + ":" + str(port)
        self.socket_image = self.context.socket(zmq.PULL)
        self.socket_image.connect(address_image)
    
    def get_frame(self) -> Frame:
        message = self.socket_image.recv()
        image = deserialize(message.decode())
        return frame

class TwoPReceiver(QRunnable):

    def __init__(self, scan_image: ScanImage, ring_buffer: FrameRingBuffer, *args, **kwargs):

        super().__init__(*args, **kwargs)
        
        self.scan_image = scan_image
        self.keepgoing = True
        self.ring_buffer = ring_buffer
    
    def terminate(self):
        self.keepgoing = False

    def run(self):
        while self.keepgoing:
            image = self.scan_image.get_image()
            frame = BaseFrame()
            self.callback(image)


