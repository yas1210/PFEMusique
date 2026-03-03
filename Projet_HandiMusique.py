import sys #Gère sortie de l'app
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton,
    QComboBox, QSpinBox,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem
)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QBrush, QColor, QPen
from PyQt5.QtWidgets import QInputDialog

#QMainWindow → fenêtre principale

#QWidget → barre de configuration

#QVBoxLayout / QHBoxLayout → organisation verticale / horizontale des rectangles

#QSpinBox → nombre de zones

#QGraphicsView → zone graphique interactive

#QGraphicsScene → scène qui contient les objets (après bouton démarrer)

#QGraphicsRectItem → rectangle interactif

#QRectF -> rectangle flottant


#Rectangle interactif

class InteractiveRect(QGraphicsRectItem):
  
    def __init__(self, x, y, w, h, color):
        super().__init__(x, y, w, h)

        self.note = None  # note associée

        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.black, 2))

        self.setFlags(
            QGraphicsRectItem.ItemIsMovable |
            QGraphicsRectItem.ItemIsSelectable |
            QGraphicsRectItem.ItemIsFocusable
        )

        self.resizing = False
        
 
# si on clique en bas à droite -> redimensionnement , puis déplacement du rectangle avec la souris
    def mousePressEvent(self, event):
        if event.pos().x() > self.rect().width() - 10 and \
           event.pos().y() > self.rect().height() - 10:
            self.resizing = True
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing:
            rect = QRectF(0, 0, event.pos().x(), event.pos().y())
            self.setRect(rect)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.resizing = False
        super().mouseReleaseEvent(event)


#Attribuer une note à chaque rectangle (double clic)
    def mouseDoubleClickEvent(self, event):
        notes = ["Do", "Ré", "Mi", "Fa", "Sol", "La", "Si", "Do aigu"]

        note, ok = QInputDialog.getItem(
            None,
            "Choisir une note",
            "Note pour cette zone :",
            notes,
            0,
            False
        )

        if ok:
            self.note = note
            print(f"Note assignée : {self.note}")

#fenetre principale
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Interface Musicothérapie - Projet HandiMusique")
        self.setGeometry(100, 100, 1000, 700)

        self.zones = []  #liste qui contient les zones interactives
        
        self.colors = [
    QColor(255, 100, 100, 150),
    QColor(100, 255, 100, 150),
    QColor(100, 100, 255, 150),
    QColor(255, 255, 100, 150),
    QColor(255, 100, 255, 150),
    QColor(100, 255, 255, 150),
    QColor(200, 150, 255, 150),
    QColor(255, 180, 120, 150)
]

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.create_config_bar()
        self.create_visualisation_area()

    def create_config_bar(self):
        self.config_widget = QWidget()
        self.config_layout = QHBoxLayout()
        self.config_widget.setLayout(self.config_layout)

#Partie du corps (zone texte libre mais à changer en item à selectionner )
        self.body_label = QLabel("Partie du corps :")
        self.body_input = QLineEdit()

        self.zone_label = QLabel("Nombre zone(s) interactive(s) :")
        self.zone_spin = QSpinBox()
        self.zone_spin.setMinimum(1)
        self.zone_spin.setMaximum(10)
        self.zone_spin.valueChanged.connect(self.update_zones)

        self.instrument_label = QLabel("Instrument :")
        self.instrument_combo = QComboBox()
        self.instrument_combo.addItems(["Piano", "Guitare", "Batterie"])

        self.start_button = QPushButton("Démarrer")
        self.start_button.clicked.connect(self.start_session)

        self.config_layout.addWidget(self.body_label)
        self.config_layout.addWidget(self.body_input)
        self.config_layout.addWidget(self.zone_label)
        self.config_layout.addWidget(self.zone_spin)
        self.config_layout.addWidget(self.instrument_label)
        self.config_layout.addWidget(self.instrument_combo)
        self.config_layout.addWidget(self.start_button)

        self.main_layout.addWidget(self.config_widget)

    def create_visualisation_area(self):
        self.view = QGraphicsView()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)

        self.view.setStyleSheet("background-color: lightgray;")
        self.main_layout.addWidget(self.view)

    def update_zones(self, value):

        current_count = len(self.zones)

        # Si on augmente
        if value > current_count:
            for i in range(current_count, value):
                rect = InteractiveRect(
                    50 + i * 120,
                    100,
                    100,
                    100,
                    self.colors[i % len(self.colors)])
                self.scene.addItem(rect)
                self.zones.append(rect)

        # Si on diminue
        elif value < current_count:
            for i in range(current_count - 1, value - 1, -1):
                self.scene.removeItem(self.zones[i])
                self.zones.pop()

    def start_session(self):
        self.config_widget.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.config_widget.show()
            
            


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())