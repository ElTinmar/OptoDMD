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
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QLabel,  QWidget
from qt_widgets import NDarray_to_QPixmap

def deserialize(message: str) -> NDArray:
    '''parse the output of matlab mat2str function'''
    rows = message.split(';')
    data = []
    for r in rows:
        data.append(r.split(','))
    array = np.array(data, dtype = np.float32)
    return array


class TwoPhoton(QWidget):

    def __init__(self, zmq_adress: str, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.connect(zmq_adress)

        self.twop_image = QLabel(self)
        self.twop_image.setFixedWidth(512)
        self.twop_image.setFixedHeight(512)

        # TODO using a QTimer may be a bad idea. What should I do instead ? 
        self.timer = QTimer()
        self.timer.timeout.connect(self.loop)
        self.timer.setInterval(33)
        self.timer.start()

    def loop(self):
        try:
            message = self.socket.recv(flags=zmq.NOBLOCK)
            image = deserialize(message.decode())
            image = (255*image).astype(np.uint8)
            self.twop_image.setPixmap(NDarray_to_QPixmap(image))
            self.update()
        except zmq.Again:
            pass