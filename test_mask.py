from Mask import Mask
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = Mask()
window.show()
app.exec()
