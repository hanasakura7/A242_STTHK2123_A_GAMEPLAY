import pygame
from menu import show_menu
from gameplay import run_game
import config  # import the config module

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 500))
    pygame.display.set_caption('Bird-Shooter')

    pygame.mixer.init()
    pygame.mixer.music.load("audio/background_music.mp3")
    pygame.mixer.music.set_volume(0.5)

    # Use config.audio_enabled to control music playback
    if config.audio_enabled:
        pygame.mixer.music.play(-1)  # Loop indefinitely
    else:
        pygame.mixer.music.pause()

    show_menu(screen, start_callback=run_game)

if __name__ == "__main__":
    main()
