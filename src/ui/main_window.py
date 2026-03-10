import cv2
from PyQt6.QtWidgets import (QListWidget, QWidget, QHBoxLayout, QLabel, QPushButton, 
                             QColorDialog, QSpinBox, QComboBox, QFormLayout, QInputDialog, QListWidgetItem)
from PyQt6.QtGui import QImage, QPixmap, QColor, QMouseEvent
from PyQt6.QtCore import Qt, QPoint 

from core.models import (InteractiveSquare, NOTE_NAMES, 
                         NOTE_TO_OFFSET, DEFAULT_NOTE_COLORS)
from .widgets import FlippedButton 
import os
import json
# -----------------------------------------

# Supposons que ces imports sont dans votre structure de projet
# from core.models import InteractiveSquare, NOTE_NAMES, NOTE_TO_OFFSET, DEFAULT_NOTE_COLORS
# from .widgets import FlippedButton

class MainWindow(QWidget):


    def __init__(self, midi_manager, pose_engine):
        super().__init__()
        self.setWindowTitle("Séance de musique - MusicMoove")
        self.resize(1100, 600)
        
        self.midi = midi_manager #envoyer notes
        self.engine = pose_engine #stocker positions du corps
        self.squares = [] #liste des carrés interactifs à l’écran
        self.active_square = None #carré actuellement sélectionné pour drag/resizing
        self.config_minimized = False #état du panneau de configuration (affiché ou réduit)
        self.current_color = None #couleur sélectionnée pour un carré
        self.saved_configs = {} #sauvegarder configs

        # Dossier data pour stocker les configurations
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.config_file = os.path.join(self.data_dir, "configs.json")
        self.saved_configs = {}

        # Mapping entre le texte UI et les clés du PoseEngine avec MediaPipe
        self.mode_map = {
            "Mains (Poignets/Doigts)": "MAINS",
            "Membres Supérieurs": "MEMBRES_SUP",
            "Visage (Yeux/Nez/Bouche)": "VISAGE",
            "Tout le corps (Sans filtre)": "SANS_FILTRE"
        }

        self.init_ui()
        self.load_configs_from_disk()#récupérer les partitions déjà sauvegardées

    def init_ui(self):
        layout = QHBoxLayout(self) #QHBoxLayout pour séparer zone video et partie onglets config
        layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Zone Vidéo ---
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setScaledContents(True)
        layout.addWidget(self.video_label, stretch=1)

        # --- Panneau de Configuration ---
        self.config_panel = QWidget()
        self.config_panel.setFixedWidth(300)
        self.config_layout = QFormLayout(self.config_panel)
        layout.addWidget(self.config_panel)

        # Sélection du mode de détection des gestes (combobox)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(self.mode_map.keys())
        self.config_layout.addRow("Membre suivi :", self.mode_combo)

        # Séparateur visuel
        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet("background-color: #444;")
        self.config_layout.addRow(line)

        # Partie choix de la couleur de la zone interactive
        self.color_btn = QPushButton("Choisir couleur")
        self.color_btn.clicked.connect(self.choose_color)
        self.config_layout.addRow("Couleur :", self.color_btn)
        #Choix de la note
        self.note_combo = QComboBox()
        self.note_combo.addItems(NOTE_NAMES) # NOTE_NAMES doit être importé
        self.config_layout.addRow("Note :", self.note_combo)
        #Choix de l'octave
        self.octave_spin = QSpinBox()
        self.octave_spin.setRange(1,7)
        self.octave_spin.setValue(4)
        self.config_layout.addRow("Octave :", self.octave_spin)
        #Bouton ajouter carré
        self.add_btn = QPushButton("Ajouter carré")
        self.add_btn.clicked.connect(self.add_square)
        self.config_layout.addRow(self.add_btn)
        #Bouton démarrer
        self.start_btn = QPushButton("Démarrer / Minimiser")
        self.start_btn.clicked.connect(self.toggle_config)
        self.config_layout.addRow(self.start_btn)

        # Bouton sauvegarde configuration
        self.save_config_btn = QPushButton("Sauvegarder configuration")
        self.save_config_btn.clicked.connect(self.save_configuration)
        self.config_layout.addRow(self.save_config_btn)

        # Liste des configurations sauvegardées
        self.config_list = QListWidget()
        self.config_layout.addRow("Partitions Enregistrées", self.config_list)

        # Bouton CONFIGURATION latéral (Dock)
        self.dock_btn = FlippedButton("CONFIGURATION") # Doit être importé
        self.dock_btn.setFixedWidth(40)
        layout.addWidget(self.dock_btn)
        self.dock_btn.hide()
        self.dock_btn.clicked.connect(self.toggle_config)

        # Configuration Souris
        self.video_label.setMouseTracking(True)
        self.video_label.mousePressEvent = self.mouse_press
        self.video_label.mouseMoveEvent = self.mouse_move
        self.video_label.mouseReleaseEvent = self.mouse_release

    # Méthode permettant d'enregistrer les partitions dans la liste config_list
    def save_configuration(self):
        name, ok = QInputDialog.getText(self, "Nom configuration", "Nom :")
        if not ok or not name:
            return

        config_data = []

        for sq in self.squares:
            data = {
                "x": sq.rect.x(),
                "y": sq.rect.y(),
                "w": sq.rect.width(),
                "h": sq.rect.height(),
                "note": sq.midi_note,
                "color": (sq.color.red(), sq.color.green(), sq.color.blue())
            }
            config_data.append(data)
        self.saved_configs[name] = config_data
        self.add_config_to_list(name)
        self.save_configs_to_disk()


#Transforme un frame NumPy (provenant de la caméra) en QImage, puis en QPixmap pour affichage dans QLabel.
    def update_video_display(self, frame, points=None, show_points=True):
        h, w, _ = frame.shape

        # Dessine des points verts si le tracking du corps est activé
        if show_points and points:
            for p in points:
                cv2.circle(frame, (p[0], p[1]), 6, (0,255,0), -1)

        img = QImage(frame.data, w, h, w*3, QImage.Format.Format_RGB888).rgbSwapped()
        self.video_label.setPixmap(QPixmap.fromImage(img))

    #Ouvre un dialogue de couleur et sauvegarde la couleur choisie pour le prochain carré
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid(): self.current_color = color

    #Crée un InteractiveSquare avec Note MIDI calculée,Couleur choisie ou par défaut,Position initiale (100,100 à 200,200)
    def add_square(self):
        note_name = self.note_combo.currentText()
        octave = self.octave_spin.value()
        midi_note = 12*(octave+1) + NOTE_TO_OFFSET[note_name]
        color = self.current_color or DEFAULT_NOTE_COLORS[NOTE_TO_OFFSET[note_name]]
        self.squares.append(InteractiveSquare(100,100,200,200,color,midi_note))

#Gesion du panneau de config
    def toggle_config(self):
        # On inverse l'état
        self.config_minimized = not self.config_minimized
        
        # On agit sur les widgets
        self.config_panel.setVisible(not self.config_minimized)
        self.dock_btn.setVisible(self.config_minimized)
        
        # Force l'affichage à se rafraîchir
        self.update()


#transforme la position du clic sur le widget en coordonnées vidéo (640×480)

    def _scale_mouse_pos(self, event):
        label_w = self.video_label.width()
        label_h = self.video_label.height()
        scale_x = 640 / label_w
        scale_y = 480 / label_h
        pos = event.position().toPoint()
        return QPoint(int(pos.x() * scale_x), int(pos.y() * scale_y))
#Détecte si on clique sur un carré pour le supprimer, déplacer ou redimensionner
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

#déplace ou redimensionne le carré actif
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

#termine le drag ou resize
    def mouse_release(self, event: QMouseEvent):
        if self.active_square:
            self.active_square.dragging = self.active_square.resizing = False
            self.active_square = None

    # Sauvegarder partitions graphiquement
    def load_configuration_by_name(self, name):

        if name not in self.saved_configs:
            return

        self.squares.clear()

        for data in self.saved_configs[name]:

            color = QColor(*data["color"])

            sq = InteractiveSquare(
                data["x"],
                data["y"],
                data["x"] + data["w"],
                data["y"] + data["h"],
                color,
                data["note"]
            )

            self.squares.append(sq)
        self.update()

    def add_config_to_list(self, name):

        item = QListWidgetItem()
        widget = QWidget()

        layout = QHBoxLayout()
        layout.setContentsMargins(5,0,5,0)

        label = QLabel(name)

        delete_btn = QPushButton("x")
        delete_btn.setFixedWidth(20)

        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(delete_btn)

        widget.setLayout(layout)

        item.setSizeHint(widget.sizeHint())

        self.config_list.addItem(item)
        self.config_list.setItemWidget(item, widget)

        # chargement au clic sur le nom
        label.mousePressEvent = lambda event, n=name: self.load_configuration_by_name(n)

        # suppression
        delete_btn.clicked.connect(lambda: self.delete_configuration(name, item))

    # Sauvegarder les partitions localement
    def save_configs_to_disk(self):
        with open(self.config_file, "w") as f:
            json.dump(self.saved_configs, f, indent=4)

    def load_configs_from_disk(self):
        if not os.path.exists(self.config_file):
            return

        with open(self.config_file, "r") as f:
            self.saved_configs = json.load(f)

        for name in self.saved_configs:
            self.add_config_to_list(name)

    # supprimer une partition
    def delete_configuration(self, name, item):
        if name in self.saved_configs:
            del self.saved_configs[name]

        row = self.config_list.row(item)
        self.config_list.takeItem(row)

        self.save_configs_to_disk()