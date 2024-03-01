import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QRunnable, QThreadPool, QObject, Qt
from PyQt5.QtWidgets import QLabel,  QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QCheckBox, QListWidget, QListWidgetItem
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QIntValidator
from qt_widgets import NDarray_to_QPixmap
import numpy as np
from numpy.typing import NDArray
from typing import Optional

class DrawPolyROI(QWidget):
    
    def __init__(self, image: Optional[NDArray] = None, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.image = image or np.zeros((512,512,3),dtype=np.uint8)
        self.polygons = []
        self.masks = []
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

    def layout_components(self):

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.image_label)

    def set_image(self, image: NDArray):
        self.image = image
        self.image_label.setPixmap(NDarray_to_QPixmap(self.image))

    def paintEvent(self, event):
        
        self.image_label.setPixmap(NDarray_to_QPixmap(self.image))
        painter = QPainter(self.image_label.pixmap())

        green_pen = QPen()
        green_pen.setWidth(1)
        green_pen.setColor(QColor(0, 255, 0, 255))

        red_pen = QPen()
        red_pen.setWidth(1)
        red_pen.setColor(QColor(255, 0, 0, 255))
        
        painter.setPen(green_pen)
        for shape in self.polygons:
            for pt1, pt2 in zip(shape[:-1],shape[1:]):
                painter.drawLine(pt1, pt2)

        painter.setPen(red_pen)
        if len(self.current_polygon) == 1:
            painter.drawLine(self.current_polygon[0], self.mouse_pos)
        elif len(self.current_polygon) > 1:
            for pt1, pt2 in zip(self.current_polygon[:-1],self.current_polygon[1:]):
                painter.drawLine(pt1, pt2)
            painter.drawLine(pt2, self.mouse_pos)

    def on_mouse_press(self, event):
        
        # left-click adds a new point to polygon
        if event.button() == Qt.LeftButton:
            self.current_polygon.append(event.pos())

            # remove point with shift pressed
            if event.modifiers() == Qt.ShiftModifier:
                pass
            
        # right-click closes polygon
        if event.button() == Qt.RightButton:

            # close polygon
            self.current_polygon.append(self.current_polygon[0])

            # store coordinates
            coords = [[pt.x(), pt.y()] for pt in self.current_polygon]
            coords = np.array(coords, dtype=np.int32)
            self.polygons.append(self.current_polygon)

            # store mask
            mask = np.zeros_like(self.image)
            mask_RGB = cv2.fillPoly(mask, [coords], 255)
            self.masks.append(mask_RGB[:,:,0])

            # reset current polygon
            self.current_polygon = []

        self.update()

    def on_mouse_move(self, event):

        self.mouse_pos = event.pos()
        self.update()

class MaskListHeader(QWidget):
    # show labels hide, id, exposure time
    # Maybe use a table instead?
    pass

class MaskListItem(QWidget):

    hidden = pyqtSignal(int)
    exposureChanged = pyqtSignal(int)
    deletePressed = pyqtSignal()

    def __init__(self, id: int, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.id = id
        self.exposure_time = 0
        self.create_components()
        self.layout_components()

    def create_components(self):
        
        self.hide = QCheckBox(self)
        self.hide.stateChanged.connect(self.hidden)

        self.delete = QPushButton(self)
        self.delete.setText('delete')
        self.delete.pressed.connect(self.deletePressed)

        self.id = QLabel(self)
        self.id.setText(str(self.id))

        self.exposure_time = QLineEdit(self)
        self.exposure_time.setText(str(self.exposure_time))
        self.exposure_time.setValidator(QIntValidator(0,10_000,self))
        self.exposure_time.editingFinished.connect(self.set_exposure_time)

    def layout_components(self):
        
        layout = QHBoxLayout(self)
        layout.addWidget(self.hide)
        layout.addWidget(self.id)
        layout.addWidget(self.exposure_time)
    
    def set_exposure_time(self):
        self.exposure_time = int(self.exposure_time.text())
        self.exposureChanged.emit(self.exposure_time)
        

class WhatsYourName(QWidget):

    def __init__(self, image: Optional[NDArray] = None, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.masks = []
        self.create_components()
        self.layout_components()

    def create_components(self):

        # ROI list 
        self.polygon_list = QListWidget(self)

        # flatten button 
        self.flatten = QPushButton(self)
        self.flatten.setText('flatten')
        self.flatten.clicked.connect(self.flatten_masks)

    def layout_components(self):

        right_panel = QVBoxLayout(self)
        right_panel.addWidget(self.polygon_list)
        right_panel.addWidget(self.flatten)

    def flatten_masks(self):
        pass

    def mask_added(self):

        mask_item = MaskListItem(0)
        list_item = QListWidgetItem(mask_item)
        self.polygon_list.addItem(list_item)