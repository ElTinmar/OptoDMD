from DrawMasks import DrawPolyMask
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = DrawPolyMask()
window.show()
app.exec()
