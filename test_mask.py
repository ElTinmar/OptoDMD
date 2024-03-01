from DrawROI import DrawPolyROI
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = DrawPolyROI()
window.show()
app.exec()
