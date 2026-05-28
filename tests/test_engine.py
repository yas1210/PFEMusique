#vérifie que MediaPipe Pose est bien 
# initialisé avec les bons paramètres.
from unittest.mock import MagicMock, patch
import sys
import cv2
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from core.engine import PoseEngine


@patch("core.engine.mp.solutions.pose")
@patch("core.engine.mp.solutions.drawing_utils")
def test_pose_engine_initialization(mock_drawing, mock_pose):
    fake_pose_instance = MagicMock()
    mock_pose.Pose.return_value = fake_pose_instance

    engine = PoseEngine()

    mock_pose.Pose.assert_called_once_with(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    assert engine.pose == fake_pose_instance
    assert engine.mp_pose == mock_pose
    assert engine.mp_drawing == mock_drawing

#2 veut vérifier deux choses :

#l’image est convertie de BGR vers RGB avec cv2.cvtColor
#l’image convertie est envoyée à self.pose.process()
@patch("core.engine.cv2.cvtColor")
@patch("core.engine.mp.solutions.pose")
@patch("core.engine.mp.solutions.drawing_utils")
def test_process_frame_converts_to_rgb_and_calls_pose(mock_drawing, mock_pose, mock_cvtcolor):
    fake_pose_instance = MagicMock()
    fake_results = MagicMock()
    fake_rgb = MagicMock()

    mock_pose.Pose.return_value = fake_pose_instance
    mock_cvtcolor.return_value = fake_rgb
    fake_pose_instance.process.return_value = fake_results

    engine = PoseEngine()
    fake_frame = MagicMock()

    results = engine.process_frame(fake_frame)

    mock_cvtcolor.assert_called_once_with(fake_frame, cv2.COLOR_BGR2RGB)
    fake_pose_instance.process.assert_called_once_with(fake_rgb)
    assert results == fake_results
# 3.a
@patch("core.engine.mp.solutions.pose")
@patch("core.engine.mp.solutions.drawing_utils")
def test_get_landmarks_pixels_returns_empty_if_no_results(mock_drawing, mock_pose):
    fake_pose_instance = MagicMock()
    mock_pose.Pose.return_value = fake_pose_instance

    engine = PoseEngine()

    assert engine.get_landmarks_pixels(None, 640, 480) == []
# 3.b
@patch("core.engine.mp.solutions.pose")
@patch("core.engine.mp.solutions.drawing_utils")
def test_get_landmarks_pixels_returns_empty_if_no_pose_landmarks(mock_drawing, mock_pose):
    fake_pose_instance = MagicMock()
    mock_pose.Pose.return_value = fake_pose_instance

    engine = PoseEngine()

    fake_results = MagicMock()
    fake_results.pose_landmarks = None

    assert engine.get_landmarks_pixels(fake_results, 640, 480) == []

#4. Test de get_landmarks_pixels() en mode MAINS

@patch("core.engine.mp.solutions.pose")
@patch("core.engine.mp.solutions.drawing_utils")
def test_get_landmarks_pixels_mains_mode_filters_visible_points(mock_drawing, mock_pose):
    fake_pose_instance = MagicMock()
    mock_pose.Pose.return_value = fake_pose_instance

    engine = PoseEngine()

    landmarks = []
    for i in range(33):
        lm = MagicMock()
        lm.x = 0.1 * (i % 5)
        lm.y = 0.2 * (i % 5)
        lm.visibility = 0.9
        landmarks.append(lm)

    landmarks[15].x = 0.5
    landmarks[15].y = 0.25
    landmarks[15].visibility = 0.8

    landmarks[16].x = 0.75
    landmarks[16].y = 0.5
    landmarks[16].visibility = 0.4  # ne doit pas être gardé

    fake_results = MagicMock()
    fake_results.pose_landmarks = MagicMock()
    fake_results.pose_landmarks.landmark = landmarks

    points = engine.get_landmarks_pixels(fake_results, 200, 100, mode="MAINS")

    assert (100, 25) in points
    assert (150, 50) not in points

#5. Test du mode inavalide
@patch("core.engine.mp.solutions.pose")
@patch("core.engine.mp.solutions.drawing_utils")
def test_get_landmarks_pixels_invalid_mode_returns_empty(mock_drawing, mock_pose):
    fake_pose_instance = MagicMock()
    mock_pose.Pose.return_value = fake_pose_instance

    engine = PoseEngine()

    fake_results = MagicMock()
    fake_results.pose_landmarks = MagicMock()
    fake_results.pose_landmarks.landmark = [MagicMock() for _ in range(33)]

    points = engine.get_landmarks_pixels(fake_results, 640, 480, mode="INCONNU")

    assert points == []