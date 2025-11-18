import pygame
import sys
import config 

print(config.audio_enabled)  # debug print current value

class ToggleButton:
    def __init__(self, pos, size, font_path, initial_state=True, callback=None):
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.state = initial_state
        self.callback = callback
        self.font = pygame.font.Font(font_path, 26)
        self.text_color = (255, 255, 255)

    def draw(self, surface, label, label_pos, label_max_width):
        text_surf = self.font.render(label, True, self.text_color)
        text_rect = text_surf.get_rect(midleft=label_pos)
        if text_rect.width > label_max_width:
            ellipsis = "..."
            for i in range(len(label), 0, -1):
                short_label = label[:i] + ellipsis
                short_surf = self.font.render(short_label, True, self.text_color)
                if short_surf.get_width() <= label_max_width:
                    text_surf = short_surf
                    text_rect = text_surf.get_rect(midleft=label_pos)
                    break
        surface.blit(text_surf, text_rect)

        bg_color = (46, 204, 113) if self.state else (192, 57, 43)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=20)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 3, border_radius=20)

        knob_radius = self.rect.height // 2 - 5
        knob_x = self.rect.left + knob_radius + 5 if not self.state else self.rect.right - knob_radius - 5
        knob_center = (knob_x, self.rect.centery)
        pygame.draw.circle(surface, (255, 255, 255), knob_center, knob_radius)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.state = not self.state
            if self.callback:
                self.callback(self.state)

class Button:
    def __init__(self, text, pos, size, font_path, callback, font_size=26,
                 text_color=(255, 255, 255), bg_color=(155, 89, 182), hover_color=(175, 115, 205)):
        self.text = text
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = pos
        self.callback = callback
        self.font = pygame.font.Font(font_path, font_size)
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.bg_color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

def quit_game():
    pygame.quit()
    sys.exit()

def show_settings_menu(screen):
    font_path = "fonts/Pixel Emulator.otf"
    bg = pygame.image.load("images/bg.png").convert()
    bg = pygame.transform.scale(bg, (screen.get_width(), screen.get_height()))

    panel_width, panel_height = 450, 400
    panel_rect = pygame.Rect(
        (screen.get_width() - panel_width) // 2,
        (screen.get_height() - panel_height) // 2,
        panel_width, panel_height
    )

    def audio_toggle_callback(state):
        config.audio_enabled = state
        if state:
            if not pygame.mixer.music.get_busy():
                try:
                    pygame.mixer.music.load("audio/background_music.mp3")
                    pygame.mixer.music.play(-1, fade_ms=1000)
                except Exception as e:
                    print("Failed to load music:", e)
            else:
                pygame.mixer.music.unpause()
        else:
            pygame.mixer.music.pause()

    def sound_toggle_callback(state):
        config.sound_enabled = state  # update config variable
        # handle sound effects mute/unmute here

    toggle_size = (70, 40)
    toggle_padding_right = 30
    label_padding_left = 30

    # MUSIC TOGGLE
    music_y = panel_rect.top + 90
    music_x = panel_rect.right - toggle_padding_right - toggle_size[0]
    music_label_pos = (panel_rect.left + label_padding_left, music_y + toggle_size[1] // 2)
    music_label_max_width = music_x - label_padding_left - panel_rect.left
    music_toggle = ToggleButton((music_x, music_y), toggle_size, font_path, config.audio_enabled, audio_toggle_callback)

    # SOUND EFFECT TOGGLE
    sound_y = music_y + 60
    sound_x = panel_rect.right - toggle_padding_right - toggle_size[0]
    sound_label_pos = (panel_rect.left + label_padding_left, sound_y + toggle_size[1] // 2)
    sound_label_max_width = sound_x - label_padding_left - panel_rect.left
    sound_toggle = ToggleButton((sound_x, sound_y), toggle_size, font_path, config.sound_enabled, sound_toggle_callback)

    button_size = (260, 50)

    def back_to_menu():
        show_settings_menu.running = False

    back_btn = Button("Back to Menu", (panel_rect.centerx, panel_rect.top + 250), button_size, font_path, back_to_menu)
    quit_btn = Button("Quit Game", (panel_rect.centerx, panel_rect.top + 310), button_size, font_path, quit_game)

    buttons = [back_btn, quit_btn]

    title_font = pygame.font.Font(font_path, 36)
    title_text = title_font.render("Settings", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(panel_rect.centerx, panel_rect.top + 40))

    show_settings_menu.running = True
    while show_settings_menu.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            music_toggle.handle_event(event)
            sound_toggle.handle_event(event)
            for btn in buttons:
                btn.check_click(event)

        screen.blit(bg, (0, 0))
        pygame.draw.rect(screen, (44, 62, 80), panel_rect)
        pygame.draw.rect(screen, (255, 255, 255), panel_rect, 3)
        screen.blit(title_text, title_rect)

        music_label = "Music ON" if music_toggle.state else "Music OFF"
        sound_label = "Sound FX ON" if sound_toggle.state else "Sound FX OFF"

        music_toggle.draw(screen, music_label, music_label_pos, music_label_max_width)
        sound_toggle.draw(screen, sound_label, sound_label_pos, sound_label_max_width)

        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
