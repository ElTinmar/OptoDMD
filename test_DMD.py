from DMD import DMD, ImageSender
from PyQt5.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = DMD(screen_num=1)
window.show()
sendr = ImageSender(window)
app.exec()
