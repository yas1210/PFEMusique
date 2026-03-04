import cv2
import mediapipe as mp

class PoseEngine:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        return results

    def get_landmarks_pixels(self, results, w, h):
        points = []
        if results.pose_landmarks:
            # On suit principalement les mains (poignets et doigts)
            target_indices = [15, 16, 17, 18, 19, 20, 21, 22]
            for idx in target_indices:
                lm = results.pose_landmarks.landmark[idx]
                points.append((int(lm.x * w), int(lm.y * h)))
        return points