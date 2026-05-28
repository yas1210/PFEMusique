from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
#1.Vérifier l’initialisation du gestionnaire MIDI
from core.audio import MidiManager


@patch("core.audio.pygame.midi.get_default_output_id", return_value=1)
@patch("core.audio.pygame.midi.Output")
@patch("core.audio.pygame.midi.init")
def test_midi_manager_initialization(mock_init, mock_output, mock_default_id):
    fake_player = MagicMock()
    mock_output.return_value = fake_player

    manager = MidiManager()

    mock_init.assert_called_once()
    mock_output.assert_called_once_with(1)
    assert manager.player == fake_player
    assert manager.sound_playing == {}
#2. activation d’une note
@patch("core.audio.pygame.midi.get_default_output_id", return_value=1)
@patch("core.audio.pygame.midi.Output")
@patch("core.audio.pygame.midi.init")
def test_update_notes_turns_note_on(mock_init, mock_output, mock_default_id):
    fake_player = MagicMock()
    mock_output.return_value = fake_player

    manager = MidiManager()

    manager.update_notes({60})

    fake_player.note_on.assert_called_once_with(60, 127)
    assert manager.sound_playing[60] is True

#3.Ne pas redéclencher une note déjà active
@patch("core.audio.pygame.midi.get_default_output_id", return_value=1)
@patch("core.audio.pygame.midi.Output")
@patch("core.audio.pygame.midi.init")
def test_update_notes_ne_joue_pas_la_meme_note(mock_init, mock_output, mock_default_id):
    fake_player = MagicMock()
    mock_output.return_value = fake_player

    manager = MidiManager()

    manager.update_notes({60})
    fake_player.note_on.reset_mock()

    manager.update_notes({60})

    fake_player.note_on.assert_not_called()
    assert manager.sound_playing[60] is True
#4. Vérifier que si une note jouait avant mais 
# n’est plus présente dans active_notes
@patch("core.audio.pygame.midi.get_default_output_id", return_value=1)
@patch("core.audio.pygame.midi.Output")
@patch("core.audio.pygame.midi.init")
def test_arret_des_notes_non_demandees (mock_init, mock_output, mock_default_id):
    fake_player = MagicMock()
    mock_output.return_value = fake_player

    manager = MidiManager()

    manager.update_notes({60, 64})
    fake_player.reset_mock()

    manager.update_notes({64})

    fake_player.note_off.assert_called_once_with(60, 127)
    assert manager.sound_playing[60] is False
    assert manager.sound_playing[64] is True
# Fonction close
@patch("core.audio.pygame.midi.quit")
@patch("core.audio.pygame.midi.get_default_output_id", return_value=1)
@patch("core.audio.pygame.midi.Output")
@patch("core.audio.pygame.midi.init")
def test_fermeture_du_gestionnaire_audio(mock_init, mock_output, mock_default_id, mock_quit):

    fake_player = MagicMock()
    mock_output.return_value = fake_player

    manager = MidiManager()

    manager.update_notes({60,64})
    fake_player.reset_mock()

    manager.close()

    fake_player.note_off.assert_any_call(60,127)
    fake_player.note_off.assert_any_call(64,127)
    fake_player.close.assert_called_once()
    mock_quit.assert_called_once()