import zmq
import numpy as np
from numpy.typing import NDArray
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRunnable, QThreadPool, QObject
from PyQt5.QtWidgets import QLabel,  QWidget
from qt_widgets import NDarray_to_QPixmap
from image_tools import im2uint8
from typing import Callable
from camera_tools import FrameRingBuffer, BaseFrame, Frame


def deserialize(message: str) -> Frame:
    '''deserialize string into numpy array'''

    image_num, image_time, data = message.split('|')
    image = [r.split(',') for r in data.split(';')]
    return BaseFrame(int(image_num), float(image_time), np.array(image, dtype = np.float32))

class ScanImage(QObject):

    buffer_updated = pyqtSignal()
    frame_received = pyqtSignal()

    def __init__(self, protocol: str, host: str, port: int, buffer_size: int = 5, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        self.context = zmq.Context()
        self.buffer = None
        self.shape = None
        self.buffer_size = buffer_size

        # get images from scanimage
        address_image = protocol + host + ":" + str(port)
        self.socket_image = self.context.socket(zmq.PULL)
        self.socket_image.connect(address_image)
    
    def update_buffer(self) -> None:
        self.buffer = FrameRingBuffer(
            num_items = self.buffer_size,
            frame_shape=self.shape,
            frame_dtype=np.float32
        )
        self.buffer_updated.emit()

    def get_buffer(self) -> FrameRingBuffer:
        return self.buffer

    def get_frame(self) -> Frame:

        # get image over ZMQ socket
        message = self.socket_image.recv()
        frame = deserialize(message.decode())

        # update buffer if anything changed
        if frame.image.shape != self.shape:
            self.shape = frame.image.shape
            self.update_buffer()

        # put image on the ring buffer
        self.buffer.put(frame)

        # emit signal
        self.frame_received.emit()

        # return frame
        return frame

class TwoPReceiver(QRunnable):

    def __init__(self, scan_image: ScanImage, *args, **kwargs):

        super().__init__(*args, **kwargs)
        
        self.scan_image = scan_image
        self.keepgoing = True

    def terminate(self):
        self.keepgoing = False

    def run(self):
        while self.keepgoing:
            self.scan_image.get_frame()
            


