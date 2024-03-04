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

class ImageSignal(QObject):
    # only QObject can emit signals, not QRunnable
    image_ready = pyqtSignal(np.ndarray)

class ImageSender(QRunnable):

    def __init__(self, zmq_adress, *args, **kwargs):

        super().__init__(*args, **kwargs)
        
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.connect(zmq_adress)
        self.signal = ImageSignal()
        self.keepgoing = True
    
    def stop(self):
        self.keepgoing = False

    def run(self):
        while self.keepgoing:
            message = self.socket.recv()
            image = deserialize(message.decode())
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
