from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRunnable, QThreadPool, QObject, Qt
from PyQt5.QtWidgets import QLabel,  QWidget, QVBoxLayout, QHBoxLayout
from qt_widgets import NDarray_to_QPixmap
import numpy as np
from numpy.typing import NDArray
from typing import Optional

class Mask(QWidget):
    
    def __init__(self, image: Optional[NDArray] = None, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.image = image or np.zeros((512,512),dtype=np.uint8)
        self.polygons = []
        self.current_polygon = []
        self.create_components()
        self.layout_components()

    def create_components(self):
        
        # label to draw on 
        self.image_label = QLabel(self)
        self.image_label.setPixmap(NDarray_to_QPixmap(self.image))
        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = self.on_mouse_press    
        self.image_label.mouseMoveEvent = self.on_mouse_move

        # flatten button 

    def layout_components(self):

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.image_label)

    def set_image(self, image: NDArray):
        self.image = image
        self.image_label.setPixmap(NDarray_to_QPixmap(self.image))

    def on_mouse_press(self, event):
        
        # left-click adds a new point to polygon
        if event.button() == Qt.LeftButton:
            print('click!')

        # right-click closes polygon

    def on_mouse_move(self, event):

        if event.buttons() == Qt.RightButton:
            print('swish!')
