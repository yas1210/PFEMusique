import cv2
from PyQt6.QtCore import QRect, QPoint
from PyQt6.QtGui import QColor
import numpy as np

NOTE_NAMES = ["Do","Do#","Re","Re#","Mi","Fa","Fa#","Sol","Sol#","La","La#","Si"]
NOTE_TO_OFFSET = {name: i for i, name in enumerate(NOTE_NAMES)}

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

    def __init__(self, x1, y1, x2, y2, color=QColor(255,0,0), note=60,
                 instrument="Piano", program=0, custom_sound=None):
        self.rect = QRect(x1, y1, x2-x1, y2-y1)
        self.color = color
        self.midi_note = note
        self.instrument = instrument
        self.program = program
        self.channel = 0
        self.custom_sound = custom_sound
        self.is_active = False
        self.dragging = False
        self.resizing = False
        self.resize_dir = None
        self.offset = QPoint()
        self.sound = None  # Pour son custom chargé

    def draw(self, frame, show_controls=True):
        x, y, w, h = self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height()
        bgr_color = (self.color.blue(), self.color.green(), self.color.red())
        thickness = 4 if self.is_active else 2

        # Forme selon l'instrument
        if self.instrument == "Piano":
            cv2.rectangle(frame, (x, y), (x+w, y+h), bgr_color, thickness)
        elif self.instrument == "Guitare":
            cv2.circle(frame, (x+w//2, y+h//2), min(w,h)//2, bgr_color, thickness)
        elif self.instrument == "Flute":
            cv2.ellipse(frame, (x+w//2, y+h//2), (w//2,h//3), 0,0,360, bgr_color, thickness)
        elif self.instrument == "Violon":
            pts = np.array([[x,y+h//2],[x+w//2,y],[x+w,y+h//2],[x+w//2,y+h]], np.int32)
            cv2.polylines(frame,[pts],True,bgr_color,thickness)
        else:
            cv2.rectangle(frame, (x,y),(x+w,y+h), bgr_color, thickness)

        # Texte du label
        # Pour les sons customs, on affiche uniquement le nom
        if self.custom_sound:
            label = str(self.instrument)
        # Pour les instruments MIDI, on garde le format "Piano : Do3"
        else:
            note_name = NOTE_NAMES[self.midi_note % 12]
            octave = (self.midi_note // 12) - 1
            label = f"{self.instrument} : {note_name}{octave}"

        # Affichage sur l'image
        cv2.putText(frame, label, (x+5, y-5),
        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)

        # Remplissage si actif
        if self.is_active:
            overlay = frame.copy()
            cv2.rectangle(overlay,(x,y),(x+w,y+h),bgr_color,-1)
            cv2.addWeighted(overlay,0.3,frame,0.7,0,frame)

        # Éléments d'édition
        if show_controls:
            corners = [(x,y),(x+w,y),(x,y+h),(x+w,y+h)]
            for cx,cy in corners:
                cv2.circle(frame,(cx,cy),5,(0,255,0),-1)
            # bouton delete
            cx, cy = x+w-self.DELETE_SIZE//2, y+self.DELETE_SIZE//2
            r = self.DELETE_SIZE//2
            cv2.circle(frame,(cx,cy),r,(0,0,255),-1)
            cv2.putText(frame,"x",(cx-5,cy+5),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)

    def handle_at(self,pos:QPoint):
        r = self.HANDLE_SIZE//2
        corners = {"top_left":self.rect.topLeft(),"top_right":self.rect.topRight(),
                   "bottom_left":self.rect.bottomLeft(),"bottom_right":self.rect.bottomRight()}
        for dir, corner in corners.items():
            handle_rect = QRect(corner.x()-r, corner.y()-r, self.HANDLE_SIZE, self.HANDLE_SIZE)
            if handle_rect.contains(pos): return dir
        return None

    def delete_at(self,pos:QPoint):
        cx = self.rect.x()+self.rect.width()-self.DELETE_SIZE//2
        cy = self.rect.y()+self.DELETE_SIZE//2
        r = self.DELETE_SIZE//2
        dx, dy = pos.x()-cx, pos.y()-cy
        return dx*dx+dy*dy <= r*r