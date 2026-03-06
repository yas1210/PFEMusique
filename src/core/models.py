import cv2
from PyQt6.QtCore import QRect, QPoint
from PyQt6.QtGui import QColor

NOTE_NAMES = ["Do","Do#","Ré","Ré#","Mi","Fa","Fa#","Sol","Sol#","La","La#","Si"]
NOTE_TO_OFFSET = {name: i for i,name in enumerate(NOTE_NAMES)}

DEFAULT_NOTE_COLORS = {
    0: QColor(255,0,0), 1: QColor(255,128,0), 2: QColor(255,255,0),
    3: QColor(128,255,0), 4: QColor(0,255,0), 5: QColor(0,255,128),
    6: QColor(0,255,255), 7: QColor(0,128,255), 8: QColor(0,0,255),
    9: QColor(128,0,255), 10: QColor(255,0,255), 11: QColor(255,0,128)
}

class InteractiveSquare:
    HANDLE_SIZE = 10
    DELETE_SIZE = 15
    POINT_RADIUS = 5

    def __init__(self, x1, y1, x2, y2, color=QColor(255,0,0), note=60):
        # On définit le rectangle
        self.rect = QRect(x1, y1, x2-x1, y2-y1)
        self.color = color
        self.midi_note = note  # On utilise midi_note pour matcher l'UI
        self.is_active = False # État pour le son
        self.dragging = False
        self.resizing = False
        self.resize_dir = None
        self.offset = QPoint()

    def draw(self, frame, show_controls=True):
        """Dessine le carré. show_controls=False cache les coins et la croix."""
        x, y, w, h = self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height()
        bgr_color = (self.color.blue(), self.color.green(), self.color.red())
        
        # 1. Le rectangle (toujours visible)
        thickness = 4 if self.is_active else 2
        cv2.rectangle(frame, (x, y), (x + w, y + h), bgr_color, thickness)
        
        # 2. Effet de remplissage si touché
        if self.is_active:
            overlay = frame.copy()
            cv2.rectangle(overlay, (x, y), (x + w, y + h), bgr_color, -1)
            cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

        # 3. Éléments d'édition (UNIQUEMENT si show_controls est True)
        if show_controls:
            # Points aux sommets (Corners)
            corners = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]
            for corner in corners:
                cv2.circle(frame, corner, 5, (0, 255, 0), -1)

            # Bouton de suppression (Croix rouge)
            cx = x + w - self.DELETE_SIZE // 2
            cy = y + self.DELETE_SIZE // 2
            radius = self.DELETE_SIZE // 2

            cv2.circle(frame, (cx, cy), radius, (0, 0, 275), -1)

            cv2.putText(
                frame,
                "x",
                (cx - 5, cy + 5),
                cv2.FONT_HERSHEY_COMPLEX,
                0.5,
                (255, 255, 255),
                1
            )

    def handle_at(self, pos: QPoint):
        r = self.HANDLE_SIZE // 2

        corners = {
            "top_left": self.rect.topLeft(),
            "top_right": self.rect.topRight(),
            "bottom_left": self.rect.bottomLeft(),
            "bottom_right": self.rect.bottomRight()
        }

        for direction, corner in corners.items():
            handle_rect = QRect(
                corner.x() - r,
                corner.y() - r,
                self.HANDLE_SIZE,
                self.HANDLE_SIZE
            )

            if handle_rect.contains(pos):
                return direction

        return None

    def delete_at(self, pos: QPoint):
        cx = self.rect.x() + self.rect.width() - self.DELETE_SIZE // 2
        cy = self.rect.y() + self.DELETE_SIZE // 2
        r = self.DELETE_SIZE // 2

        dx = pos.x() - cx
        dy = pos.y() - cy

        return dx*dx + dy*dy <= r*r