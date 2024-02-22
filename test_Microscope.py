from Microscope import TwoPhoton
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = TwoPhoton(zmq_adress="tcp://localhost:5560")
window.show()
app.exec()
