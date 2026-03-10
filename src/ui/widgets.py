from PyQt6.QtWidgets import QPushButton, QSizePolicy
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt, QRect

class FlippedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(-90)
        rect = QRect(-self.height() // 2, -self.width() // 2, self.height(), self.width())
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()

class StartButton(QPushButton):
    """Bouton personnalisé vert foncé avec icône de démarrage."""
    def __init__(self, text="▶ Démarrer la séance", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                border: 1px solid #1B5E20;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #1B5E20;
            }
        """)