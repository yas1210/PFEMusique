import cv2
import mediapipe as mp

class PoseEngine:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        # On initialise une seule fois le modèle global
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        return results

    def get_landmarks_pixels(self, results, w, h, mode="MAINS"):
        points = []
        if not results or not results.pose_landmarks:
            return points

        # Définition des filtres par mode (Index MediaPipe Pose)
        if mode == "MAINS":
            # Poignets et doigts uniquement
            target_indices = [15, 16, 17, 18, 19, 20, 21, 22]
        
        elif mode == "VISAGE":
            # Nez, yeux, oreilles, bouche (points 0 à 10)
            target_indices = list(range(0, 11))
            
        elif mode == "MEMBRES_SUP":
            # Épaules, coudes, poignets, mains (points 11 à 22)
            target_indices = list(range(11, 23))
            
        elif mode == "SANS_FILTRE":
            # Tout le corps (points 0 à 32)
            target_indices = list(range(0, 33))
        else:
            target_indices = []

        for idx in target_indices:
            lm = results.pose_landmarks.landmark[idx]
            # On ne garde que les points suffisamment visibles pour éviter les erreurs
            if lm.visibility > 0.5:
                px_x = int(lm.x * w)
                px_y = int(lm.y * h)
                points.append((px_x, px_y))
                
        return points