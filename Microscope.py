import zmq
import numpy as np
from numpy.typing import NDArray
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRunnable, QThreadPool, QObject
from PyQt5.QtWidgets import QLabel,  QWidget
from qt_widgets import NDarray_to_QPixmap

def deserialize(message: str) -> NDArray:
    '''deserialize string into numpy array'''

    data = [r.split(',') for r in message.split(';')]
    return np.array(data, dtype = np.float32)

class ScanImage:

    def __init__(self, protocol: str, host: str, port: int) -> None:

        self.context = zmq.Context()

        # get images from scanimage
        address_image = protocol + host + str(port)
        self.socket_image = self.context.socket(zmq.PULL)
        self.socket_image.connect(address_image)

        # send commands to scanimage 
        address_control = protocol + host + str(port + 1)
        self.socket_control = self.context.socket(zmq.PUSH)
        self.socket_control.bind(address_control)
    
    def get_image(self) -> NDArray:

        message = self.socket_image.recv()
        image = deserialize(message.decode())
        return image
    
    def set_zoom(self, zoom: float):

        # TODO check range
        self.socket_control.send(zoom)

class ImageSignal(QObject):
    # only QObject can emit signals, not QRunnable
    image_ready = pyqtSignal(np.ndarray)

class ImageSender(QRunnable):

    def __init__(self, scan_image: ScanImage, *args, **kwargs):

        super().__init__(*args, **kwargs)
        
        self.scan_image = scan_image
        self.signal = ImageSignal()
        self.keepgoing = True
    
    def stop(self):
        self.keepgoing = False

    def run(self):
        while self.keepgoing:
            image = self.scan_image.get_image()
            self.signal.image_ready.emit(image)

class TwoPhoton(QWidget):

    def __init__(self, sender: ImageSender, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.sender = sender
        self.sender.signal.image_ready.connect(self.display)
        self.thread_pool = QThreadPool()
        self.thread_pool.start(sender)

        self.twop_image = QLabel(self)
        self.twop_image.setFixedWidth(512)
        self.twop_image.setFixedHeight(512)

    @pyqtSlot(np.ndarray)
    def display(self, image: NDArray):
        image = (255*image).astype(np.uint8)
        self.twop_image.setPixmap(NDarray_to_QPixmap(image))
        self.update()

    def closeEvent(self, event):
        self.sender.stop()
