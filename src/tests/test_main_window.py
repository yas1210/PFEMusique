import pytest
import numpy as np
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow


class DummyMidi:
    pass


class DummyPose:
    pass

#Créer un objet réutilisable dans plusieurs tests
#qtbot simulate user interaction with Qt widgets
@pytest.fixture
def main_window(qtbot):
    midi = DummyMidi()
    pose = DummyPose()

    window = MainWindow(midi, pose)
    qtbot.addWidget(window)

    return window#instance de MainWindow à tester

#Vérifier que la fenêtre est correctement initialisée
def test_initialization(main_window):
    assert main_window.windowTitle() == "MPipophone Pro"
    assert main_window.squares == []
    assert main_window.active_square is None

#Vérifier l'état de la fenetre après le clic sur bouton config
def test_toggle_config(main_window):
    initial_state = main_window.config_minimized

    main_window.toggle_config()

    assert main_window.config_minimized != initial_state

#Vérifier si ajout d'un carré se fait correctement
def test_add_square(main_window):
    main_window.note_combo.setCurrentIndex(0)
    main_window.octave_spin.setValue(4)

    main_window.add_square()

    assert len(main_window.squares) == 1


def test_choose_color(main_window, monkeypatch):
    from PyQt6.QtWidgets import QColorDialog

    def fake_get_color():
        return QColor(255, 0, 0)

    monkeypatch.setattr(QColorDialog, "getColor", fake_get_color)
    #QColorDialog.getColor()  # appelle fake_get_color() à la place
    main_window.choose_color()

    assert main_window.current_color == QColor(255, 0, 0)


def test_update_video_display(main_window):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    main_window.update_video_display(frame)

    assert main_window.video_label.pixmap() is not None