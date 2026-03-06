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
    POINT_RADIUS = 5
    DELETE_SIZE = 12

    def __init__(self, x1, y1, x2, y2, color=QColor(255,0,0), note=60):
        self.rect = QRect(x1, y1, x2-x1, y2-y1)
        self.color = color
        self.note = note
        self.dragging = False
        self.resizing = False
        self.resize_dir = None
        self.offset = QPoint()

    def handle_at(self, pos: QPoint):
        rect = self.rect
        handles = {
            "top_left": QRect(rect.topLeft(), QPoint(rect.topLeft().x()+self.HANDLE_SIZE, rect.topLeft().y()+self.HANDLE_SIZE)),
            "top_right": QRect(rect.topRight()-QPoint(self.HANDLE_SIZE,0), QPoint(rect.topRight().x()+1, rect.topRight().y()+self.HANDLE_SIZE)),
            "bottom_left": QRect(rect.bottomLeft()-QPoint(0,self.HANDLE_SIZE), QPoint(rect.bottomLeft().x()+self.HANDLE_SIZE, rect.bottomLeft().y()+1)),
            "bottom_right": QRect(rect.bottomRight()-QPoint(self.HANDLE_SIZE,self.HANDLE_SIZE), rect.bottomRight())
        }
        for dir, handle_rect in handles.items():
            if handle_rect.contains(pos): return dir
        return None

    def delete_at(self, pos: QPoint):
        rect = QRect(self.rect.topRight()-QPoint(self.DELETE_SIZE,0),
                     QPoint(self.rect.topRight().x(), self.rect.topRight().y()+self.DELETE_SIZE))
        return rect.contains(pos)