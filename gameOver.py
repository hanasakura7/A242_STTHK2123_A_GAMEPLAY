import pygame
import sys
import config
from menu import Button

# part hana: game over screen 
class GameOverScreen:
    def __init__(self, screen, font_path):
        self.screen = screen
        self.font_path = font_path
        self.running = True
        self.choice = None

        self.bg = pygame.image.load("images/bg.png").convert()
        self.bg = pygame.transform.scale(self.bg, (screen.get_width(), screen.get_height()))

        self.panel_width, self.panel_height = 500, 450
        self.panel_rect = pygame.Rect(
            (screen.get_width() - self.panel_width) // 2,
            (screen.get_height() - self.panel_height) // 2,
            self.panel_width, self.panel_height
        )

        self.button_size = (240, 50)
        self.title_font = pygame.font.Font(font_path, 36)
        self.text_font = pygame.font.Font(font_path, 26)

        self.play_again_button = Button("Play Again", (self.panel_rect.centerx, self.panel_rect.top + 230), self.button_size, font_path, self.play_again)
        self.menu_button = Button("Main Menu", (self.panel_rect.centerx, self.panel_rect.top + 290), self.button_size, font_path, self.return_to_menu)
        self.quit_button = Button("Quit Game", (self.panel_rect.centerx, self.panel_rect.top + 350), self.button_size, font_path, self.quit_game)

        self.buttons = [self.play_again_button, self.menu_button, self.quit_button]

    def play_again(self):
        self.choice = "restart"
        self.running = False

    def return_to_menu(self):
        self.choice = "menu"
        self.running = False

    def quit_game(self):
        self.choice = "quit"
        self.running = False

    def show(self, latest_score, highest_score):
        if config.audio_enabled:
            pygame.mixer.fadeout(1000)  # fade out ALL channels including SFX
            pygame.time.delay(1000)
            pygame.mixer.music.load('audio/game_over.mp3')
            pygame.mixer.music.play(-1)

        title_text = self.title_font.render("GAME OVER", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.panel_rect.centerx, self.panel_rect.top + 40))

        score_text = self.text_font.render(f"Your Score: {latest_score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.panel_rect.centerx, self.panel_rect.top + 100))

        high_score_text = self.text_font.render(f"High Score: {highest_score}", True, (255, 255, 255))
        high_score_rect = high_score_text.get_rect(center=(self.panel_rect.centerx, self.panel_rect.top + 150))

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                for btn in self.buttons:
                    btn.check_click(event)

            self.screen.blit(self.bg, (0, 0))
            pygame.draw.rect(self.screen, (44, 62, 80), self.panel_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), self.panel_rect, 3)
            self.screen.blit(title_text, title_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(high_score_text, high_score_rect)

            for btn in self.buttons:
                btn.draw(self.screen)

            pygame.display.flip()

        pygame.mixer.music.stop()
        return self.choice