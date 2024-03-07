import cv2
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QScrollArea, QPushButton, QFrame, QLineEdit, QCheckBox
import numpy as np
from numpy.typing import NDArray
from typing import Optional, List
from image_tools import im2uint8, im2rgb, DrawPolyMask

class DrawPolyMaskOpto(DrawPolyMask):
    """
    Derived class implementing slots to receive, delete, clear, flatten,
    or hide masks
    """

    def __init__(self, image: Optional[NDArray] = None, *args, **kwargs):
    
        if image is None:
            image = np.zeros((512,512,3), np.uint8)

        super().__init__(image, *args, **kwargs)

    def create_components(self):

        super().create_components()

        # special masks
        self.checkerboard = QPushButton(self)
        self.checkerboard.setText('checkerboard')
        self.checkerboard.clicked.connect(self.create_checkerboard)

        self.whole_field = QPushButton(self)
        self.whole_field.setText('whole field')
        self.whole_field.clicked.connect(self.create_whole_field)

    def layout_components(self):

        super().layout_components()

        draw_buttons_layout = QHBoxLayout()
        draw_buttons_layout.addWidget(self.checkerboard)
        draw_buttons_layout.addWidget(self.whole_field)
        draw_buttons_layout.addStretch()

        self.layout.insertLayout(0, draw_buttons_layout)

    def on_mask_receive(self, recipient: int, key: int, mask: NDArray):
         
        if recipient == self.ID:

            # store mask
            show_mask = True
            self.masks[key] = (show_mask, mask)

        self.update_pixmap()

    def on_mask_delete(self, key: int):

        # remove mask from storage
        self.masks.pop(key)
        self.update_pixmap()

    def on_mask_clear(self):

        # remove mask from storage
        self.masks = {}
        self.update_pixmap()

    def on_mask_flatten(self):
        
        # flatten masks
        flat = np.zeros(self.image.shape[:2], dtype=np.float32)
        for key, mask_tuple in self.masks.items():
            mask = mask_tuple[1]
            flat += mask
        flat = np.clip(flat,0,1)

        # store flat mask
        self.masks = {}
        self.masks[1] = (True, flat)

        # update display
        self.update_pixmap()

    def on_mask_visibility(self, key: int, visibility: bool):

        _, mask = self.masks[key]
        self.masks[key] = (visibility, mask)
        self.update_pixmap()

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

        self.update_pixmap()

        # send signal
        self.mask_drawn.emit(self.ID, key, checkerboard)
    
    def create_whole_field(self):

        # create key
        mask_keys = self.masks.keys() or [0]
        key = max(mask_keys) + 1
        
        # create whole field
        whole_field = np.ones(self.image.shape[:2], dtype=np.float32)

        # update masks
        self.masks[key] = (True, whole_field)

        self.update_pixmap()

        # send signal
        self.mask_drawn.emit(self.ID, key, whole_field)

class DrawPolyMaskOptoDMD(DrawPolyMaskOpto):
    '''
    Derived class that emits the collection of visible masks 
    '''

    DMD_update = pyqtSignal(np.ndarray)

    def __init__(self, height: int, width: int, *args, **kwargs):

        image = np.zeros((height, width, 3))
        super().__init__(image, *args, **kwargs)

    def update_pixmap(self):
        super().update_pixmap()
        self.DMD_update.emit(im2uint8(self.im_display))

    def expose(self, key: int):
        visible, mask = self.masks[key]
        mask_RGB = im2rgb(im2uint8(mask))
        self.DMD_update.emit(mask_RGB)
        
    def clear(self):
        black = np.zeros_like(self.image, np.uint8)
        self.DMD_update.emit(black)

class MaskItem(QWidget):

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
        visible = (self.show.checkState() == Qt.Checked)
        self.showClicked.emit(self.mask_index, visible)

    def delete_clicked(self):
        self.deletePressed.emit(self.mask_index)

class MaskManager(QWidget):
    
    send_mask = pyqtSignal(int, int, np.ndarray)
    delete_mask = pyqtSignal(int) 
    flatten_mask = pyqtSignal()
    clear_mask = pyqtSignal()
    mask_visibility = pyqtSignal(int, int)

    def __init__(
        self,
        mask_drawers: List[DrawPolyMask],
        mask_drawer_names: List[str],
        transformations: NDArray, 
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        N = len(mask_drawers)
        if not np.all(transformations.shape == np.array([N,N,3,3])):
            raise ValueError(f"transformations should be a {[N,N,3,3]} array")

        self.mask_widgets = {} 
        self.mask_drawers = mask_drawers
        self.mask_drawer_names = mask_drawer_names
        self.transformations = transformations 
        self.create_components()
        self.layout_components()

        for idx, drawer in enumerate(self.mask_drawers):
            drawer.set_ID(idx)
            drawer.mask_drawn.connect(self.on_mask_receive)

            self.send_mask.connect(drawer.on_mask_receive)
            self.delete_mask.connect(drawer.on_mask_delete)
            self.mask_visibility.connect(drawer.on_mask_visibility)
            self.flatten_mask.connect(drawer.on_mask_flatten)
            self.clear_mask.connect(drawer.on_mask_clear)

    def create_components(self):

        # flatten button 
        self.flatten = QPushButton(self)
        self.flatten.setText('flatten')
        self.flatten.clicked.connect(self.on_flatten_mask)

        # clear button 
        self.clear = QPushButton(self)
        self.clear.setText('clear')
        self.clear.clicked.connect(self.on_clear_masks)

        self.mask_frame = QFrame(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.mask_frame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

    def layout_components(self):

        mask_buttons_layout = QHBoxLayout()
        mask_buttons_layout.addWidget(self.clear)
        mask_buttons_layout.addWidget(self.flatten)

        self.frame_layout = QVBoxLayout(self.mask_frame)
        self.frame_layout.addStretch()
        self.frame_layout.setContentsMargins(0,0,0,0)
        self.frame_layout.setSpacing(0)

        mask_controls = QVBoxLayout()
        mask_controls.addLayout(mask_buttons_layout)
        mask_controls.addWidget(self.scroll_area)

        tabs = QTabWidget()
        for drawer, name in zip(self.mask_drawers, self.mask_drawer_names):
            tabs.addTab(drawer, name)

        layout = QHBoxLayout(self)
        layout.addWidget(tabs)
        layout.addLayout(mask_controls)

    def on_mask_receive(self, drawer_ID: int, key: int, mask: NDArray):

        # transform and send to other drawers
        for idx, drawer in enumerate(self.mask_drawers):

            # don't send to yourself
            if not idx == drawer_ID:

                T = self.transformations[drawer_ID, idx, :2, :]
                shape = drawer.get_image_size()
                dsize = shape[::-1] # opencv expects (col, rows)
                mask_transformed = cv2.warpAffine(mask, T, dsize)
                self.send_mask.emit(idx, key, mask_transformed)
                
        # add widget 
        widget = MaskItem(key, str(key))
        widget.showClicked.connect(self.on_mask_visibility)
        widget.deletePressed.connect(self.on_delete_mask)
        self.mask_widgets[key] = widget
        self.frame_layout.insertWidget(self.frame_layout.count()-1, widget)

    def on_delete_mask(self, key: int):

        # delete widget
        widget = self.mask_widgets.pop(key)
        self.frame_layout.removeWidget(widget)
        widget.deleteLater()

        # propagate to connected widgets
        self.delete_mask.emit(key)

    def on_mask_visibility(self, key: int, visibility: bool):

        # propagate to connected widgets
        self.mask_visibility.emit(key, visibility)

    def on_clear_masks(self):

        self.clear_mask.emit()

        for key, widget in self.mask_widgets.items():
            # delete widget
            self.frame_layout.removeWidget(widget)
            widget.deleteLater()

        self.mask_widgets = {}

    def on_flatten_mask(self):

        if self.mask_widgets:

            self.flatten_mask.emit()

            # remove widgets
            for key, widget in self.mask_widgets.items():
                self.frame_layout.removeWidget(widget)
                widget.deleteLater()
            self.mask_widgets = {}

            # update widget
            widget = MaskItem(1, "flat")
            widget.showClicked.connect(self.on_mask_visibility)
            widget.deletePressed.connect(self.on_delete_mask)
            self.frame_layout.insertWidget(self.frame_layout.count()-1, widget)
            self.mask_widgets[1] = widget
