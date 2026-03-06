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