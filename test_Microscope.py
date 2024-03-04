from Microscope import TwoPhoton, ImageSender
from PyQt5.QtWidgets import QApplication
import sys

o1_263 = "192.168.236.75"
PORT = "5555"
zmq_address= "tcp://" + o1_263 + ":" + PORT

app = QApplication(sys.argv)
sender = ImageSender(zmq_address)
window = TwoPhoton(sender)
window.show()
app.exec()
