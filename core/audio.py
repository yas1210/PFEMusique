import pygame.midi

class MidiManager:
    def __init__(self):
        pygame.midi.init()
        # Initialise la sortie par défaut (0)
        try:
            self.player = pygame.midi.Output(pygame.midi.get_default_output_id())
        except:
            self.player = pygame.midi.Output(0)
        self.sound_playing = {}

    def update_notes(self, active_notes):
        # active_notes est un set des IDs de notes actuellement activées par l'engine
        for note in active_notes:
            if not self.sound_playing.get(note, False):
                self.player.note_on(note, 127)
                self.sound_playing[note] = True
        
        # Arrêter les notes qui ne sont plus actives
        to_stop = [n for n, playing in self.sound_playing.items() if playing and n not in active_notes]
        for note in to_stop:
            self.player.note_off(note, 127)
            self.sound_playing[note] = False

    def close(self):
        for note, playing in self.sound_playing.items():
            if playing: self.player.note_off(note, 127)
        self.player.close()
        pygame.midi.quit()