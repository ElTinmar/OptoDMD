import zmq
import numpy as np
from numpy.typing import NDArray
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRunnable, QThreadPool, QObject
from PyQt5.QtWidgets import QLabel,  QWidget
from qt_widgets import NDarray_to_QPixmap
from image_tools import im2uint8
from typing import Callable

def deserialize(message: str) -> NDArray:
    '''deserialize string into numpy array'''

    data = [r.split(',') for r in message.split(';')]
    return np.array(data, dtype = np.float32)

class ScanImage(QObject):

    def __init__(self, protocol: str, host: str, port: int, *args, **kwargs) -> None:

        super().__init__(*args, **kwargs)

        self.context = zmq.Context()

        # get images from scanimage
        address_image = protocol + host + ":" + str(port)
        self.socket_image = self.context.socket(zmq.PULL)
        self.socket_image.connect(address_image)
    
    def get_image(self) -> np.ndarray:
        message = self.socket_image.recv()
        image = deserialize(message.decode())
        image = np.clip(image,0,1)
        return image

class TwoPReceiver(QRunnable):

    def __init__(self, scan_image: ScanImage, callback: Callable[[np.ndarray], None], *args, **kwargs):

        super().__init__(*args, **kwargs)
        
        self.scan_image = scan_image
        self.keepgoing = True
        self.callback = callback
    
    def terminate(self):
        self.keepgoing = False

    def run(self):
        while self.keepgoing:
            image = self.scan_image.get_image()
            self.callback(image)

