# Get images from scanimage 
# Use a scanimage "user function" and some form of IPC to send
# images to python
# Looks like ZMQ might not be a bad idea there (can be used 
# with MATLAB by using the java implementation, JeroMQ)

# https://stackoverflow.com/questions/38060320/how-to-use-jeromq-in-matlab
# https://stackoverflow.com/questions/39316544/getting-started-with-jeromq-in-matlab

import zmq
import numpy as np
from numpy.typing import NDArray
from PyQt5.QtCore import QTimer, pyqtSignal, pyqtSlot, QRunnable, QThreadPool, QObject
from PyQt5.QtWidgets import QLabel,  QWidget
from qt_widgets import NDarray_to_QPixmap

def deserialize(message: str) -> NDArray:
    '''deserialize string into numpy array'''

    data = [r.split(',') for r in message.split(';')]
    return np.array(data, dtype = np.float32)

class Emitter(QObject):
    image_ready = pyqtSignal(np.ndarray)

class ImageReceiver(QRunnable):

    def __init__(self, zmq_adress, *args, **kwargs):

        super().__init__(*args, **kwargs)
        
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.connect(zmq_adress)
        self.emitter = Emitter()

    def run(self):
        # maybe find something more interruptible
        while True:
            message = self.socket.recv()
            image = deserialize(message.decode())
            image = (255*image).astype(np.uint8)
            self.emitter.image_ready.emit(image)

class TwoPhoton(QWidget):

    def __init__(self, receiver: ImageReceiver, *args, **kwargs):

        super().__init__(*args, **kwargs)

        receiver.emitter.image_ready.connect(self.display)
        self.thread_pool = QThreadPool()
        self.thread_pool.start(receiver)

        self.twop_image = QLabel(self)
        self.twop_image.setFixedWidth(512)
        self.twop_image.setFixedHeight(512)

    def display(self, image: NDArray):
        self.twop_image.setPixmap(NDarray_to_QPixmap(image))
        self.update()
