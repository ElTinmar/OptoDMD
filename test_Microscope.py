from Microscope import TwoPhoton
from PyQt5.QtWidgets import QApplication
import sys

o1_263 = "192.168.236.75"
PORT = "5555"
zmq_adress= "tcp://" + o1_263 + ":" + PORT

app = QApplication(sys.argv)
window = TwoPhoton(zmq_adress)
window.show()
app.exec()
