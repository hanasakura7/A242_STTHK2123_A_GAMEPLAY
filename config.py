import pygame
pygame.init()
pygame.mixer.init()

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.continuous_sound = None
        self.load_sounds()

    def load_sounds(self):
        sound_paths = {
            'bullet': 'sound effect/bullet.mp3',
            'game_start': 'sound effect/helikopter game start.MP3',
            'helicopter_continuous': 'sound effect/helikopter continuos.MP3',
            'collision': 'sound effect/plane clash.MP3',
            'hit_bird': 'sound effect/hit bird.mp3',
            'game_over': 'sound effect/explosion.mp3',
            'pickup_heart': 'sound effect/heartpickup.mp3'
        }

        for name, path in sound_paths.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
                volume = 1.0 if name == 'pickup_heart' else 0.7
                self.sounds[name].set_volume(volume)
            except Exception as e:
                print(f"Failed to load sound {path}: {str(e)}")
                self.sounds[name] = None

    def play(self, name, loop=False):
        if not sound_enabled or name not in self.sounds or not self.sounds[name]:
            return
        if loop:
            if self.continuous_sound:
                self.continuous_sound.stop()
            self.sounds[name].play(-1)
            self.continuous_sound = self.sounds[name]
        else:
            self.sounds[name].play()

    def stop_all(self):
        if self.continuous_sound:
            self.continuous_sound.stop()
            self.continuous_sound = None

# Shared flag variables
sound_enabled = True
audio_enabled = True
music_is_paused = False
background_music_loaded = False


# Shared sound manager
global_sound_manager = SoundManager()
