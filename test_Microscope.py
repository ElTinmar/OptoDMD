from Microscope import TwoPhoton, ImageReceiver
from PyQt5.QtWidgets import QApplication
import sys

o1_263 = "192.168.236.75"
PORT = "5555"
zmq_address= "tcp://" + o1_263 + ":" + PORT

app = QApplication(sys.argv)
receiver = ImageReceiver(zmq_address)
window = TwoPhoton(receiver)
window.show()
app.exec()
