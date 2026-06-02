"""
  - Windows : pygame.midi
  - macOS   : FluidSynth via pyfluidsynth + soundfont .sf2
  - Fallback : si aucun backend MIDI n'est disponible, les sons custom
               (pygame.mixer) continuent de fonctionner.

Dépendances supplémentaires pour macOS :
  brew install fluidsynth
  pip install pyfluidsynth
  # Télécharger une soundfont GeneralUser GS (gratuite) :
  # https://schristiancollins.com/generaluser.php
  # Placer le fichier .sf2 dans src/data/GeneralUser.sf2
"""

import platform
import pygame
import pygame.mixer
import os
os.environ["DYLD_LIBRARY_PATH"] = "/opt/homebrew/lib"
# Détection de la plateforme
_SYSTEM = platform.system()  # "Windows", "Darwin" (macOS), "Linux"

# Chemin vers la soundfont (pour FluidSynth sur macOS/Linux)
_SF2_PATHS = [
    os.path.join(os.path.dirname(__file__), "..", "data", "GeneralUser.sf2"),
    os.path.join(os.path.dirname(__file__), "..", "data", "soundfont.sf2"),
    # Chemins système courants sur macOS avec brew
    "/usr/local/share/fluidsynth/GeneralUser.sf2",
    "/opt/homebrew/share/fluidsynth/GeneralUser.sf2",
    # Chemin système courant sur Linux
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
]

def _find_sf2():
    for path in _SF2_PATHS:
        if os.path.isfile(path):
            return path
    return None


# Backend pygame.midi (Windows / Linux avec synthé MIDI système) 
class _MidiBackend:
    """Utilise pygame.midi — fonctionne nativement sur Windows."""

    def __init__(self):
        pygame.midi.init()
        try:
            self.player = pygame.midi.Output(pygame.midi.get_default_output_id())
        except Exception:
            self.player = pygame.midi.Output(0)

    def set_instrument(self, program, channel):
        self.player.set_instrument(program, channel)

    def note_on(self, note, velocity, channel):
        self.player.note_on(note, velocity, channel)

    def note_off(self, note, velocity, channel):
        self.player.note_off(note, velocity, channel)

    def close(self):
        self.player.close()
        pygame.midi.quit()


#  Backend FluidSynth (macOS, et Linux sans synthé MIDI système)
class _FluidSynthBackend:
    """
    Utilise pyfluidsynth pour synthétiser les sons MIDI en interne,
    sans périphérique externe.

    Pré-requis :
      - fluidsynth installé (brew install fluidsynth / apt install fluidsynth)
      - pyfluidsynth installé (pip install pyfluidsynth)
      - Un fichier .sf2 accessible (voir _SF2_PATHS)
    """

    def __init__(self, sf2_path):
        import fluidsynth
        self.fs = fluidsynth.Synth()
        self.fs.start(driver="coreaudio" if _SYSTEM == "Darwin" else "alsa")
        self.sfid = self.fs.sfload(sf2_path)
        # Initialiser tous les canaux avec le programme 0 (Piano)
        for ch in range(16):
            self.fs.program_select(ch, self.sfid, 0, 0)

    def set_instrument(self, program, channel):
        # bank 0 pour General MIDI standard
        self.fs.program_select(channel, self.sfid, 0, program)

    def note_on(self, note, velocity, channel):
        self.fs.noteon(channel, note, velocity)

    def note_off(self, note, velocity, channel):
        self.fs.noteoff(channel, note)

    def close(self):
        self.fs.delete()


# Sélection automatique du backend
def _create_backend():
    """
    Choisit le meilleur backend disponible selon la plateforme.
    Retourne (backend, nom_backend) ou (None, "none") si aucun n'est dispo.
    """
    if _SYSTEM == "Windows":
        # Windows : pygame.midi fonctionne out-of-the-box
        try:
            backend = _MidiBackend()
            print("[Audio] Backend : pygame.midi (Windows GS Wavetable)")
            return backend, "midi"
        except Exception as e:
            print(f"[Audio] pygame.midi indisponible sur Windows : {e}")

    # macOS ou Linux : on tente FluidSynth en priorité
    sf2 = _find_sf2()
    if sf2:
        try:
            backend = _FluidSynthBackend(sf2)
            print(f"[Audio] Backend : FluidSynth ({sf2})")
            return backend, "fluidsynth"
        except Exception as e:
            print(f"[Audio] FluidSynth indisponible : {e}")
    else:
        print("[Audio] Aucune soundfont .sf2 trouvée pour FluidSynth.")

    # Dernier recours sur Linux : pygame.midi (peut fonctionner avec timidity)
    if _SYSTEM == "Linux":
        try:
            backend = _MidiBackend()
            print("[Audio] Backend : pygame.midi (Linux)")
            return backend, "midi"
        except Exception as e:
            print(f"[Audio] pygame.midi indisponible sur Linux : {e}")

    print("[Audio] ⚠ Aucun backend MIDI disponible. Seuls les sons custom fonctionneront.")
    return None, "none"


# ── Classe principale (interface identique à l'original) ─────────────────────
class MidiManager:
    """
    Gestionnaire audio cross-platform.
    L'interface publique est identique à la version originale :
      - update_notes(active_squares, all_squares)
      - close()
    """

    def __init__(self):
        pygame.mixer.init()
        self._backend, self._backend_name = _create_backend()
        self.sound_playing = {}  # id(sq) -> bool

    @property
    def midi_available(self):
        return self._backend is not None

    def update_notes(self, active_squares, all_squares):
        # ── Déclencher les sons des zones qui deviennent actives ──────────────
        for sq in active_squares:
            if not self.sound_playing.get(id(sq), False):
                if sq.custom_sound:
                    # Son personnalisé (pygame.mixer) — fonctionne sur tous les OS
                    if not sq.sound:
                        sq.sound = pygame.mixer.Sound(sq.custom_sound)
                    sq.sound.play()
                elif self._backend:
                    # Son MIDI via le backend disponible
                    self._backend.set_instrument(sq.program, sq.channel)
                    self._backend.note_on(sq.midi_note, 127, sq.channel)
                self.sound_playing[id(sq)] = True

        # ── Arrêter les sons des zones qui deviennent inactives ───────────────
        for sq in all_squares:
            if sq.is_active:
                continue
            if self.sound_playing.get(id(sq), False):
                if sq.custom_sound and sq.sound:
                    sq.sound.stop()
                elif self._backend:
                    self._backend.note_off(sq.midi_note, 127, sq.channel)
                self.sound_playing[id(sq)] = False

    def close(self):
        """Libère proprement toutes les ressources audio."""
        if self._backend:
            # Éteindre toutes les notes encore actives
            for sq_id, playing in self.sound_playing.items():
                if playing:
                    try:
                        self._backend.note_off(sq_id, 127, 0)
                    except Exception:
                        pass
            self._backend.close()
        pygame.mixer.quit()
