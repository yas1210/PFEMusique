import cv2
from PyQt6.QtWidgets import (QListWidget, QWidget, QHBoxLayout, QLabel, QPushButton, 
                             QColorDialog, QSpinBox, QComboBox, QFormLayout, QInputDialog, QListWidgetItem, QFileDialog)
from PyQt6.QtGui import QImage, QPixmap, QColor, QMouseEvent
from PyQt6.QtCore import Qt, QPoint 

from core.models import (InteractiveSquare, NOTE_NAMES, 
                         NOTE_TO_OFFSET, DEFAULT_NOTE_COLORS)
from .widgets import *
from .student_management import StudentManagementDialog
import os
import json

class MainWindow(QWidget):

    def __init__(self, midi_manager, pose_engine, user_manager=None):
        super().__init__()
        self.setWindowTitle("MUSIC-MOVE")
        self.resize(1100, 600)
        
        self.midi = midi_manager
        self.engine = pose_engine
        self.user_manager = user_manager
        self.squares = []
        self.active_square = None
        self.config_minimized = False
        self.current_color = None
        self.saved_configs = {}

        # Dossier data
        self.data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.config_file = os.path.join(self.data_dir, "configs.json")
        self.saved_configs = {}

        # Mapping entre le texte UI et les clés du PoseEngine
        self.mode_map = {
            "Mains (Poignets+main)": "MAINS",
            "Membres Supérieurs": "MEMBRES_SUP",
            "Visage (Yeux+Nez+Bouche)": "VISAGE",
            "Tout le corps (Sans filtre)": "SANS_FILTRE"
        }

        self.init_ui()
        self.load_configs_from_disk = self.charger_configs_du_disque  # Alias pour compatibilité
        self.charger_configs_du_disque()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        #  Zone Vidéo
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setScaledContents(True)
        layout.addWidget(self.video_label, stretch=1)

        # Panneau de Configuration 
        self.config_panel = QWidget()
        self.config_panel.setFixedWidth(300)
        self.config_layout = QFormLayout(self.config_panel)
        layout.addWidget(self.config_panel)

        # Profile Selection Button (at the top of config panel)
        if self.user_manager:
            self.profile_btn = QPushButton("📋 Gérer Profils")
            self.profile_btn.clicked.connect(self.open_profile_dialog)
            self.config_layout.addRow(self.profile_btn)
            
            self.profile_label = QLabel()
            self.profile_label.setStyleSheet("color: #2E7D32; font-weight: bold;")
            self.update_profile_label()
            self.config_layout.addRow("Profil :", self.profile_label)
            
            # Séparateur visuel
            line = QWidget()
            line.setFixedHeight(2)
            line.setStyleSheet("background-color: #444;")
            self.config_layout.addRow(line)

        # AJOUT : Sélecteur de Mode
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(self.mode_map.keys())
        self.config_layout.addRow("Membre suivi :", self.mode_combo)

        # Séparateur visuel
        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet("background-color: #444;")
        self.config_layout.addRow(line)

        # Paramètres des zones interactives
        # choix de la couleur
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

        # choix de l'instrument
        self.instrument_combo = QComboBox()
        self.instruments = {
            "Piano": (0,0),
            "Guitare": (24,1),
            "Violons": (40,2),
            "Violoncelle": (42,3),
            "Flute": (73,4),
            "Trompette": (56,5)
        }
        self.instrument_combo.addItems(self.instruments.keys())
        self.config_layout.addRow("Instrument :", self.instrument_combo)

        #bouton ajouter une forme
        self.add_btn = QPushButton("Ajouter une forme interactive")
        self.add_btn.clicked.connect(self.add_square)
        self.config_layout.addRow(self.add_btn)

        # Séparateur visuel
        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet("background-color: #444;")
        self.config_layout.addRow(line)

        #Ajout son personalisé
        self.custom_sound_btn = QPushButton("Ajouter un son personnalisé")
        self.custom_sound_btn.clicked.connect(self.load_custom_sound)
        self.config_layout.addRow(self.custom_sound_btn)

        # Séparateur visuel
        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet("background-color: #444;")
        self.config_layout.addRow(line)

        # Bouton sauvegarde configuration
        self.save_config_btn = QPushButton("Sauvegarder configuration")
        self.save_config_btn.clicked.connect(self.save_configuration)
        self.config_layout.addRow(self.save_config_btn)

        # Liste des configurations sauvegardées
        self.config_list = QListWidget()
        self.config_layout.addRow("Partitions Enregistrées", self.config_list)
        self.config_list.itemClicked.connect(self.load_config_from_item)

        # Démarrer la séance musicale (sortie du mode config)
        self.start_btn = StartButton()
        self.start_btn.clicked.connect(self.toggle_config)
        self.config_layout.addRow(self.start_btn)

        # Bouton latéral (Dock)
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


    def update_video_display(self, frame, points=None, show_points=True):
        h, w, _ = frame.shape

        # Dessin des points du corps
        if show_points and points:
            for p in points:
                cv2.circle(frame, (p[0], p[1]), 6, (0,255,0), -1)

        img = QImage(frame.data, w, h, w*3, QImage.Format.Format_RGB888).rgbSwapped()
        self.video_label.setPixmap(QPixmap.fromImage(img))

    # --- Méthodes utilitaires  ---
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid(): self.current_color = color

    def add_square(self):

        note_name = self.note_combo.currentText()
        octave = self.octave_spin.value()
        color = self.current_color or DEFAULT_NOTE_COLORS[NOTE_TO_OFFSET[note_name]]
        midi_note = 12*(octave+1) + NOTE_TO_OFFSET[note_name]

        instrument = self.instrument_combo.currentText()
        program, channel = self.instruments[instrument]
        sq = InteractiveSquare(
            100,
            100,
            200,
            200,
            color,
            midi_note,
            instrument,
            program,
            getattr(self,"custom_sound",None)
        )

        sq.channel = channel
        self.squares.append(sq)

    def toggle_config(self):
        # On inverse l'état
        self.config_minimized = not self.config_minimized
        
        # On agit sur les widgets
        self.config_panel.setVisible(not self.config_minimized)
        self.dock_btn.setVisible(self.config_minimized)
        
        # FORCE l'affichage à se rafraîchir
        self.update()

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

    
# ENREGISTRER LES CONFIGURATIONS
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
                "color": (sq.color.red(), sq.color.green(), sq.color.blue()),
                "instrument": sq.instrument,
                "program": sq.program,
                "custom_sound": sq.custom_sound
            }
            config_data.append(data)

        # Link config to current profile
        if self.user_manager:
            config_entry = {
                "name": name,
                "data": config_data,
                "musicotherapist_id": self.user_manager.current_user,
                "student_id": self.user_manager.current_student_id,
                "profile_type": self.user_manager.current_profile_type
            }
            self.saved_configs[name] = config_entry
            print(f"\n💾 Enregistrement de config '{name}':")
            print(f"   MT: {self.user_manager.current_user}")
            print(f"   Étudiant: {self.user_manager.current_student_id}")
            print(f"   Type profil: {self.user_manager.current_profile_type}\n")
        else:
            # Fallback for when user_manager is not available
            self.saved_configs[name] = {"name": name, "data": config_data}
        
        # Sauvegarder TOUTES les configs sur disque
        self.save_configs_to_disk()
        
        # Rafraîchir la liste UI pour afficher la nouvelle config
        self.charger_configs_du_disque()


    # --- Charger une configuration
    def load_configuration_by_name(self, name):
        if name not in self.saved_configs:
            return

        self.squares.clear()
        
        # Extract config data from new structure
        config_entry = self.saved_configs[name]
        if isinstance(config_entry, dict) and "data" in config_entry:
            config_data = config_entry["data"]
        else:
            # Fallback for old format
            config_data = config_entry

        for data in config_data:
            color = QColor(*data["color"])

            sq = InteractiveSquare(
                data["x"],
                data["y"],
                data["x"] + data["w"],
                data["y"] + data["h"],
                color,
                data["note"],
                instrument=data.get("instrument", "Piano"),
                program=data.get("program", 0),
                custom_sound=data.get("custom_sound", None)
            )

            self.squares.append(sq)

        self.update()

    def ajouter_config_a_liste(self, name):
        """Ajouter une configuration à la liste UI."""
        item = QListWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, name)  # stocke le nom de la config

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

        # suppression d'une config enregistrée
        delete_btn.clicked.connect(lambda: self.delete_configuration(name, item))
    
    # Alias pour compatibilité
    def add_config_to_list(self, name):
        self.ajouter_config_a_liste(name)

    # Sauvegarder les partitions localement
    def sauvegarder_configs_sur_disque(self):
        """Sauvegarder les configurations sur le disque."""
        try:
            # Vérifier que le répertoire existe
            os.makedirs(self.data_dir, exist_ok=True)
            
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.saved_configs, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Erreur lors de la sauvegarde des configs: {e}")
    
    # Alias pour compatibilité
    def save_configs_to_disk(self):
        self.sauvegarder_configs_sur_disque()

    def charger_configs_du_disque(self):
        """Charger les configurations depuis le disque.
        
        IMPORTANT: On garde TOUTES les configs en mémoire pour éviter de les perdre
        lors de sauvegardes. On filtre seulement l'AFFICHAGE dans la liste UI.
        """
        if not os.path.exists(self.config_file):
            print(f"Fichier config n'existe pas: {self.config_file}")
            return

        # Charger toutes les configs depuis le disque
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.saved_configs = json.load(f)
                print(f"✓ Configs chargées du disque: {list(self.saved_configs.keys())}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"✗ Erreur lors du chargement des configs: {e}")
            self.saved_configs = {}
            return

        # Effacer UNIQUEMENT la liste UI, pas les configs en mémoire !
        self.config_list.clear()
        
        if not self.user_manager:
            # Si pas de gestionnaire d'utilisateur, afficher toutes les configs
            for name in self.saved_configs:
                self.ajouter_config_a_liste(name)
            print(f"Aucun user_manager: {len(self.saved_configs)} configs affichées")
            return
        
        current_user = self.user_manager.current_user
        current_profile_type = self.user_manager.current_profile_type
        current_student_id = self.user_manager.current_student_id
        
        print(f"\n📋 Affichage des configs:")
        print(f"   Utilisateur: {current_user}")
        print(f"   Type profil: {current_profile_type}")
        print(f"   ID élève: {current_student_id}")
        print(f"   Configs EN MÉMOIRE: {list(self.saved_configs.keys())}\n")
        
        # Compter les configs affichées
        configs_affichees = 0
        
        if current_profile_type == "musicotherapist":
            # Agréger toutes les configs pour les élèves de ce musicothérapeute
            print(f"Mode MUSICOTHÉRAPEUTE: affichage configs pour MT '{current_user}'")
            for config_name, config_entry in self.saved_configs.items():
                # Gérer les formats ancien et nouveau
                if isinstance(config_entry, dict) and "musicotherapist_id" in config_entry:
                    mt_id = config_entry.get("musicotherapist_id")
                    if mt_id == current_user:
                        self.ajouter_config_a_liste(config_name)
                        configs_affichees += 1
                        print(f"   ✓ '{config_name}' affichée (MT match)")
                    else:
                        print(f"   ✗ '{config_name}' ignorée (MT '{mt_id}' ≠ '{current_user}')")
                else:
                    # Format ancien - afficher seulement s'il n'y a pas de suivi d'utilisateur
                    self.ajouter_config_a_liste(config_name)
                    configs_affichees += 1
                    print(f"   ✓ '{config_name}' affichée (ancien format)")
        
        elif current_profile_type == "student":
            # Afficher seulement les configs liées à cet élève spécifique
            print(f"Mode ÉLÈVE: affichage configs pour élève '{current_student_id}' de MT '{current_user}'")
            for config_name, config_entry in self.saved_configs.items():
                # Gérer les formats ancien et nouveau
                if isinstance(config_entry, dict) and "student_id" in config_entry:
                    student_id = config_entry.get("student_id")
                    mt_id = config_entry.get("musicotherapist_id")
                    if (student_id == current_student_id and 
                        mt_id == current_user):
                        self.ajouter_config_a_liste(config_name)
                        configs_affichees += 1
                        print(f"   ✓ '{config_name}' affichée (match parfait)")
                    else:
                        print(f"   ✗ '{config_name}' ignorée (Student: '{student_id}' ≠ '{current_student_id}' OU MT: '{mt_id}' ≠ '{current_user}')")
                else:
                    # Format ancien - afficher seulement s'il n'y a pas de suivi
                    if "musicotherapist_id" not in config_entry:
                        self.ajouter_config_a_liste(config_name)
                        configs_affichees += 1
                        print(f"   ✓ '{config_name}' affichée (ancien format)")
        
        print(f"\n✓ {configs_affichees}/{len(self.saved_configs)} config(s) affichées en UI\n")

    # supprimer une partition
    def delete_configuration(self, name, item):
        print(f"\n🗑️  Suppression de '{name}'")
        if name in self.saved_configs:
            del self.saved_configs[name]
            print(f"   ✓ Supprimée de la mémoire")

        row = self.config_list.row(item)
        self.config_list.takeItem(row)
        
        # Sauvegarder TOUTES les configs restantes sur disque
        self.save_configs_to_disk()
        print(f"   ✓ Fichier sauvegardé\n")

    def load_config_from_item(self, item):
        name = item.data(Qt.ItemDataRole.UserRole)
        self.load_configuration_by_name(name)

# AJOUTER UN SON CUSTOM
    def load_custom_sound(self):
        # Sélection du fichier audio
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir un son personnalisé",
            "",
            "Audio (*.wav *.mp3)"
        )

        if path:
            # Demander le nom du label 
            default_name = os.path.basename(path).split('.')[0] # Nom du fichier sans extension
            label_name, ok = QInputDialog.getText(
                self, 
                "Nom du son", 
                "Comment voulez-vous nommer ce bouton ?",
                text=default_name
            )

            if ok and label_name:
                # Création automatique du carré interactif
                # On utilise une couleur par défaut (ex: Violet) ou la couleur actuelle
                color = self.current_color or QColor(155, 89, 182) 
                
                new_sq = InteractiveSquare(
                    150, 150, 250, 250,  # Position par défaut
                    color=color,
                    note=0,               # Pas de note MIDI spécifique car c'est un son custom
                    instrument=label_name, # Le label affiché sur le carré
                    custom_sound=path      # Le chemin vers le fichier
                )
                
                # On l'ajoute directement à la liste
                self.squares.append(new_sq)

    # --- Profile Management ---
    def open_profile_dialog(self):
        """Open the student management dialog."""
        if not self.user_manager:
            return
        
        dialog = StudentManagementDialog(self.user_manager, self)
        dialog.profile_changed.connect(self.on_profile_changed)
        dialog.exec()

    def on_profile_changed(self, profile_type, profile_id):
        """Handle profile change and reload configurations for the new profile."""
        # Clear current drawings but not configs yet
        self.squares.clear()
        
        # Reload configurations for the new profile (filters by profile)
        # This will properly filter/aggregate based on the new profile
        self.load_configs_from_disk()
        self.update_profile_label()
        self.update()

    def update_profile_label(self):
        """Update the profile label in the UI."""
        if not self.user_manager or not hasattr(self, 'profile_label'):
            return
        
        profile_name = self.user_manager.get_current_profile_name()
        profile_type = self.user_manager.current_profile_type
        
        if profile_type == "musicotherapist":
            label = f"Prof: {profile_name}"
        elif profile_type == "student":
            label = f"Elève : {profile_name}"
        else:
            label = "Selectionnez un profil"
        
        self.profile_label.setText(label)
