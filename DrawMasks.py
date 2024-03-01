import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QLabel,  QWidget, QVBoxLayout, QHBoxLayout, QBoxLayout, QScrollArea, QPushButton, QFrame, QLineEdit, QCheckBox, QListWidget, QListWidgetItem
from PyQt5.QtGui import QPainter, QColor, QPen, QIntValidator
from qt_widgets import NDarray_to_QPixmap
import numpy as np
from numpy.typing import NDArray
from typing import Optional
from image_tools import im2single, im2uint8

class MaskTableItem(QWidget):

    showClicked = pyqtSignal(int,int)
    deletePressed = pyqtSignal(int)

    def __init__(self, mask_index: int, name: Optional[str] = "name", *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.mask_index = mask_index
        self.name = name 
        self.create_components()
        self.layout_components()

    def create_components(self):
        
        self.show = QCheckBox(self)
        self.show.setCheckState(Qt.Checked)
        self.show.stateChanged.connect(self.show_clicked)

        self.name_label = QLineEdit(self)
        self.name_label.setText(self.name)
        self.name_label.editingFinished.connect(self.change_name)

        self.delete = QPushButton(self)
        self.delete.setText('X')
        self.delete.setMaximumWidth(25)
        self.delete.pressed.connect(self.delete_clicked)

    def layout_components(self):
        
        layout = QHBoxLayout(self)
        layout.addWidget(self.show)
        layout.addWidget(self.name_label)
        layout.addWidget(self.delete)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
    
    def change_name(self):
        self.name = self.name_label.text()

    def show_clicked(self):
        self.showClicked.emit(self.mask_index, self.show.checkState())

    def delete_clicked(self):
        self.deletePressed.emit(self.mask_index)

class DrawPolyMask(QWidget):
    
    def __init__(self, image: Optional[NDArray] = None, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if image is None:
            self.image = np.zeros((512,512,3),dtype=np.float32)
        else:
            self.image = im2single(image)

        self.masks = {}
        self.mask_widgets = {}
        self.current_polygon = []
        self.create_components()
        self.layout_components()

    def create_components(self):
        
        # label to draw on 
        self.image_label = QLabel(self)
        self.image_label.setPixmap(NDarray_to_QPixmap(im2uint8(self.image)))
        self.image_label.setMouseTracking(True)
        self.image_label.mousePressEvent = self.on_mouse_press    
        self.image_label.mouseMoveEvent = self.on_mouse_move

        # special masks
        self.checkerboard = QPushButton(self)
        self.checkerboard.setText('checkerboard')
        self.checkerboard.clicked.connect(self.create_checkerboard)

        self.whole_field = QPushButton(self)
        self.whole_field.setText('whole field')
        self.whole_field.clicked.connect(self.create_whole_field)

        # mask management

        # flatten button 
        self.flatten = QPushButton(self)
        self.flatten.setText('flatten')
        self.flatten.clicked.connect(self.flatten_masks)

        # clear button 
        self.clear = QPushButton(self)
        self.clear.setText('clear')
        self.clear.clicked.connect(self.clear_masks)

        self.mask_frame = QFrame(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.mask_frame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def layout_components(self):

        draw_buttons_layout = QHBoxLayout()
        draw_buttons_layout.addWidget(self.checkerboard)
        draw_buttons_layout.addWidget(self.whole_field)
        draw_buttons_layout.addStretch()
        
        buttons_and_image = QVBoxLayout()
        buttons_and_image.addLayout(draw_buttons_layout)
        buttons_and_image.addWidget(self.image_label)

        mask_buttons_layout = QHBoxLayout()
        mask_buttons_layout.addWidget(self.clear)
        mask_buttons_layout.addWidget(self.flatten)

        mask_controls = QVBoxLayout()
        mask_controls.addLayout(mask_buttons_layout)
        mask_controls.addWidget(self.scroll_area)

        self.frame_layout = QVBoxLayout(self.mask_frame)
        self.frame_layout.addStretch()
        self.frame_layout.setContentsMargins(0,0,0,0)
        self.frame_layout.setSpacing(0)
        self.frame_layout.setDirection(QBoxLayout.BottomToTop)

        main_layout = QHBoxLayout(self)
        main_layout.addLayout(buttons_and_image)
        main_layout.addLayout(mask_controls)
       
    def set_image(self, image: NDArray):

        self.image_label.setPixmap(NDarray_to_QPixmap(im2uint8(image)))
        self.image = im2single(image)

    def paintEvent(self, event):
        
        im_display = self.image.copy()

        # add masks 
        for key, mask_tuple in self.masks.items():
            show, mask = mask_tuple
            if show:
                im_display += np.dstack((mask,mask,mask))
        im_display = np.clip(im_display,0,1)

        # update image label
        self.image_label.setPixmap(NDarray_to_QPixmap(im2uint8(im_display)))

        # show current poly 
        painter = QPainter(self.image_label.pixmap())
        red_pen = QPen()
        red_pen.setWidth(1)
        red_pen.setColor(QColor(255, 0, 0, 255))
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

            # create key
            mask_keys = self.masks.keys() or [0]
            key = max(mask_keys) + 1

            # store mask
            coords = [[pt.x(), pt.y()] for pt in self.current_polygon]
            coords = np.array(coords, dtype = np.int32)
            mask = np.zeros_like(self.image, dtype=np.float32)
            mask_RGB = cv2.fillPoly(mask, [coords], 255)
            show_mask = True
            self.masks[key] = (show_mask, im2single(mask_RGB[:,:,0]))

            # add widget
            widget = MaskTableItem(key)
            widget.showClicked.connect(self.mask_visibility)
            widget.deletePressed.connect(self.delete_mask)
            self.mask_widgets[key] = widget
            self.frame_layout.addWidget(widget)

            # reset current polygon
            self.current_polygon = []

        self.update()

    def on_mouse_move(self, event):

        self.mouse_pos = event.pos()
        self.update()

    def delete_mask(self, key: int):

        # delete widget
        widget = self.mask_widgets.pop(key)
        self.frame_layout.removeWidget(widget)
        widget.deleteLater()

        # remove mask from storage
        self.masks.pop(key)

    def mask_visibility(self, key: int, visibility: int):

        show, mask = self.masks[key]
        if visibility == Qt.Unchecked:
            self.masks[key] = (False, mask)
        elif visibility == Qt.Checked:
            self.masks[key] = (True, mask)

    def create_checkerboard(self):
        
        # create key
        mask_keys = self.masks.keys() or [0]
        key = max(mask_keys) + 1

        # create checkerboard (8 cells in smallest dimension)
        h, w = self.image.shape[:2]
        num_pixels = min(w,h) // 8
        xv, yv = np.meshgrid(range(w), range(h), indexing='xy')
        checkerboard = ((xv // num_pixels) + (yv // num_pixels)) % 2
        checkerboard = checkerboard.astype(np.float32)

        # update masks
        self.masks[key] = (True, checkerboard)

        # update widget
        widget = MaskTableItem(key, "checkerboard")
        widget.showClicked.connect(self.mask_visibility)
        widget.deletePressed.connect(self.delete_mask)
        self.mask_widgets[key] = widget
        self.frame_layout.addWidget(widget)
    
    def create_whole_field(self):
        
        # create key
        mask_keys = self.masks.keys() or [0]
        key = max(mask_keys) + 1

        # create whole field
        whole_field = np.ones(self.image.shape[:2], dtype=np.float32)

        # update masks
        self.masks[key] = (True, whole_field)

        # update widget
        widget = MaskTableItem(key, "whole field")
        widget.showClicked.connect(self.mask_visibility)
        widget.deletePressed.connect(self.delete_mask)
        self.mask_widgets[key] = widget
        self.frame_layout.addWidget(widget)

    def flatten_masks(self):
        
        # flatten masks
        flat = np.zeros(self.image.shape[:2], dtype=np.float32)
        for key, mask_tuple in self.masks.items():
            mask = mask_tuple[1]
            flat += mask
        flat = np.clip(flat,0,1)

        # store flat mask
        self.masks = {}
        self.masks[1] = (True, flat)

        # remove widgets
        for key, widget in self.mask_widgets.items():
            self.frame_layout.removeWidget(widget)
            widget.deleteLater()
        self.mask_widgets = {}

        # update widget
        widget = MaskTableItem(1, "flat")
        widget.showClicked.connect(self.mask_visibility)
        widget.deletePressed.connect(self.delete_mask)
        self.frame_layout.addWidget(widget)
        self.mask_widgets[1] = widget

        # update display
        self.update()

    def clear_masks(self):
        
        # clear stored masks
        self.masks = {}

        # update widget
        for key, widget in self.mask_widgets.items():
            self.frame_layout.removeWidget(widget)
            widget.deleteLater()

        self.mask_widgets = {}

        # update display
        self.update()


class WhatsYourName(QWidget):

    def __init__(self, image: Optional[NDArray] = None, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.masks = []
        self.create_components()
        self.layout_components()

    def create_components(self):

        # ROI list 
        self.polygon_list = QListWidget(self)


    def layout_components(self):

        right_panel = QVBoxLayout(self)
        right_panel.addWidget(self.polygon_list)
        right_panel.addWidget(self.flatten)


    def mask_added(self):

        mask_item = MaskListItem(0)
        list_item = QListWidgetItem(mask_item)
        self.polygon_list.addItem(list_item)