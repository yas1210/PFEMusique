import cv2
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, 
                             QColorDialog, QSpinBox, QComboBox, QFormLayout)
from PyQt6.QtGui import QImage, QPixmap, QColor, QMouseEvent
from PyQt6.QtCore import Qt, QPoint
from core.models import InteractiveSquare, NOTE_NAMES, NOTE_TO_OFFSET, DEFAULT_NOTE_COLORS
from .widgets import FlippedButton

class MainWindow(QWidget):
    def __init__(self, midi_manager, pose_engine):
        super().__init__()
        self.setWindowTitle("MPipophone Pro")
        self.resize(1100, 600)
        self.midi = midi_manager
        self.engine = pose_engine
        self.squares = []
        self.active_square = None
        self.config_minimized = False
        self.current_color = None

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setScaledContents(True)
        layout.addWidget(self.video_label, stretch=1)

        self.config_panel = QWidget()
        self.config_panel.setFixedWidth(300)
        self.config_layout = QFormLayout(self.config_panel)
        layout.addWidget(self.config_panel)

        self.color_btn = QPushButton("Choisir couleur")
        self.color_btn.clicked.connect(self.choose_color)
        self.config_layout.addRow("Couleur :", self.color_btn)

        self.note_combo = QComboBox()
        self.note_combo.addItems(NOTE_NAMES)
        self.config_layout.addRow("Note :", self.note_combo)

        self.octave_spin = QSpinBox()
        self.octave_spin.setRange(1,7)
        self.octave_spin.setValue(4)
        self.config_layout.addRow("Octave :", self.octave_spin)

        self.add_btn = QPushButton("Ajouter carré")
        self.add_btn.clicked.connect(self.add_square)
        self.config_layout.addRow(self.add_btn)

        self.start_btn = QPushButton("Démarrer / Minimiser")
        self.start_btn.clicked.connect(self.toggle_config)
        self.config_layout.addRow(self.start_btn)

        self.dock_btn = FlippedButton("CONFIGURATION")
        self.dock_btn.setFixedWidth(40)
        # Adaptabilité : le bouton prendra toute la hauteur disponible
        layout.addWidget(self.dock_btn)
        self.dock_btn.hide()
        self.dock_btn.clicked.connect(self.toggle_config)

        self.video_label.setMouseTracking(True)
        self.video_label.mousePressEvent = self.mouse_press
        self.video_label.mouseMoveEvent = self.mouse_move
        self.video_label.mouseReleaseEvent = self.mouse_release

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid(): self.current_color = color

    def add_square(self):
        note_name = self.note_combo.currentText()
        octave = self.octave_spin.value()
        midi_note = 12*(octave+1) + NOTE_TO_OFFSET[note_name]
        color = self.current_color or DEFAULT_NOTE_COLORS[NOTE_TO_OFFSET[note_name]]
        self.squares.append(InteractiveSquare(100,100,200,200,color,midi_note))

    def toggle_config(self):
        self.config_minimized = not self.config_minimized
        self.config_panel.setVisible(not self.config_minimized)
        self.dock_btn.setVisible(self.config_minimized)

    def _scale_mouse_pos(self, event):
        label_w = self.video_label.width()
        label_h = self.video_label.height()
        scale_x = 640 / label_w
        scale_y = 480 / label_h
        pos = event.position().toPoint()
        return QPoint(int(pos.x() * scale_x), int(pos.y() * scale_y))

    def mouse_press(self, event: QMouseEvent):
        if self.config_minimized: return
        pos = self._scale_mouse_pos(event)
        for sq in reversed(self.squares):
            if sq.delete_at(pos):
                self.squares.remove(sq)
                return
            handle = sq.handle_at(pos)
            if handle:
                sq.resizing, sq.resize_dir, self.active_square = True, handle, sq
                return
            elif sq.rect.contains(pos):
                sq.dragging, sq.offset, self.active_square = True, pos - sq.rect.topLeft(), sq
                return

    def mouse_move(self, event: QMouseEvent):
        if not self.active_square or self.config_minimized: return
        pos = self._scale_mouse_pos(event)
        sq = self.active_square
        if sq.dragging:
            sq.rect.moveTopLeft(pos - sq.offset)
        elif sq.resizing:
            if sq.resize_dir == "top_left": sq.rect.setTopLeft(pos)
            elif sq.resize_dir == "top_right": sq.rect.setTopRight(pos)
            elif sq.resize_dir == "bottom_left": sq.rect.setBottomLeft(pos)
            elif sq.resize_dir == "bottom_right": sq.rect.setBottomRight(pos)

    def mouse_release(self, event: QMouseEvent):
        if self.active_square:
            self.active_square.dragging = self.active_square.resizing = False
            self.active_square = None

    def update_video_display(self, frame):
        h, w, _ = frame.shape
        img = QImage(frame.data, w, h, w*3, QImage.Format.Format_RGB888).rgbSwapped()
        self.video_label.setPixmap(QPixmap.fromImage(img))