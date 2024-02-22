from DMD import DMD
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = DMD(screen_num=2)
window.show()
app.exec()
