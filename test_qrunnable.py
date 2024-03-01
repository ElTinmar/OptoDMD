from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRunnable, QThreadPool, QObject
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
import sys
import time

class Emitter(QObject):
    data_ready = pyqtSignal(int)

class DataSender(QRunnable):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.emitter = Emitter()
        self.acquisition_started = False
        self.keepgoing = True

    def start(self):
        self.acquisition_started = True

    def stop(self):
        self.acquisition_started = False

    def finish(self):
        self.keepgoing = False

    def run(self):
        while self.keepgoing:
            if self.acquisition_started:
                self.emitter.data_ready.emit(1)
            else:
                self.emitter.data_ready.emit(0)
            time.sleep(0.1)

class Main(QWidget):

    def __init__(self, sender: DataSender, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.sender = sender
        self.sender.emitter.data_ready.connect(self.display)
        self.thread_pool = QThreadPool()
        self.thread_pool.start(self.sender)

        self.button_start = QPushButton()
        self.button_start.setText('start')
        self.button_start.clicked.connect(self.start)

        self.button_stop = QPushButton()
        self.button_stop.setText('stop')
        self.button_stop.clicked.connect(self.stop)

        self.button_finish = QPushButton()
        self.button_finish.setText('finish')
        self.button_finish.clicked.connect(self.finish)

        layout = QVBoxLayout(self)
        layout.addWidget(self.button_start)
        layout.addWidget(self.button_stop)
        layout.addWidget(self.button_finish)

    def start(self):
        self.sender.start()

    def stop(self):
        self.sender.stop()

    def finish(self):
        self.sender.finish()

    def display(self, value: int):
        print(value)

if __name__ == "__main__":

    app = QApplication(sys.argv)
    sender = DataSender()
    window = Main(sender)
    window.show()
    app.exec()

