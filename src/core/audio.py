import pygame.midi
import pygame

class MidiManager:
    def __init__(self):
        pygame.midi.init()
        try:
            self.player = pygame.midi.Output(pygame.midi.get_default_output_id())
        except:
            self.player = pygame.midi.Output(0)
        self.sound_playing = {}  # note -> True/False
        pygame.mixer.init()

    def update_notes(self, active_squares, all_squares):
        active_notes = set()
        for sq in active_squares:
            note = sq.midi_note
            active_notes.add(note)
            if not self.sound_playing.get(id(sq), False):
                # Son personnalisé
                if sq.custom_sound:
                    if not sq.sound:
                        sq.sound = pygame.mixer.Sound(sq.custom_sound)
                    sq.sound.play()
                # Son MIDI
                else:
                    self.player.set_instrument(sq.program, sq.channel)
                    self.player.note_on(note,127,sq.channel)
                self.sound_playing[id(sq)] = True

        # Stop notes / sons
        for sq in all_squares:
            if sq.is_active: continue
            if self.sound_playing.get(id(sq), False):
                # stop son personnalisé
                if sq.custom_sound and sq.sound:
                    sq.sound.stop()
                else:
                    self.player.note_off(sq.midi_note,127,sq.channel)
                self.sound_playing[id(sq)] = False

    def close(self):
        for note_id, playing in self.sound_playing.items():
            if playing: self.player.note_off(note_id,127)
        self.player.close()
        pygame.midi.quit()
        pygame.mixer.quit()