import pygame
import sys
from settings import show_settings_menu 

# Utility function to scale an image proportionally by width
def scale_image(image, new_width):
    image_scale = new_width / image.get_rect().width
    new_height = image.get_rect().height * image_scale
    scaled_size = (new_width, new_height)
    return pygame.transform.scale(image, scaled_size)

# Button class with configurable font and background color, with optional icon support
class Button:
    def __init__(self, text, pos, size, font_path, callback, font_size=26, text_color=(255, 255, 255), bg_color=(155, 89, 182), hover_color=(175, 115, 205), icon_path=None):
        self.text = text
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = pos
        self.callback = callback
        self.font_path = font_path
        self.font_size = font_size
        self.font = pygame.font.Font(self.font_path, self.font_size) if font_path else None
        self.text_color = text_color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.icon_path = icon_path
        self.icon = None

        if self.icon_path:
            try:
                self.icon = pygame.image.load(self.icon_path).convert_alpha()
                icon_size = min(self.rect.width - 10, self.rect.height - 10)
                self.icon = pygame.transform.scale(self.icon, (icon_size, icon_size))
            except pygame.error:
                print(f"Could not load icon: {self.icon_path}")
                self.icon = None

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()

        if self.icon and not self.text:
            icon_rect = self.icon.get_rect(center=self.rect.center)
            surface.blit(self.icon, icon_rect)
        else:
            color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.bg_color
            pygame.draw.rect(surface, color, self.rect)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)

            if self.icon:
                icon_rect = self.icon.get_rect(center=self.rect.center)
                surface.blit(self.icon, icon_rect)
            elif self.text and self.font:
                text_surf = self.font.render(self.text, True, self.text_color)
                text_rect = text_surf.get_rect(center=self.rect.center)
                surface.blit(text_surf, text_rect)

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()

# Quit game function
def quit_game():
    pygame.quit()
    sys.exit()

# Open settings
def open_audio_settings():
    screen = pygame.display.get_surface()
    show_settings_menu(screen)

# Main menu
def show_menu(screen, start_callback):
    pygame.init()

    font_path = "fonts/Pixel Emulator.otf"

    bg = pygame.image.load('images/bg.png').convert()
    bg = scale_image(bg, screen.get_width())

    title_font = pygame.font.Font(font_path, 40)
    title_main = title_font.render("BIRD-SHOOTER", True, (155, 89, 182))
    title_outline_color = (0, 0, 0)
    title_rect = title_main.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 130))

    def draw_title_with_outline(surface):
        outline_offsets = [(-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (-2, 2), (2, -2), (2, 2)]
        for dx, dy in outline_offsets:
            outline_text = title_font.render("BIRD-SHOOTER", True, title_outline_color)
            surface.blit(outline_text, title_rect.move(dx, dy))
        surface.blit(title_main, title_rect)

    button_size = (250, 60)
    start_button = Button("Start Game", (screen.get_width() // 2, screen.get_height() // 2 - 40), button_size, font_path, start_callback)
    quit_button = Button("Quit Game", (screen.get_width() // 2, screen.get_height() // 2 + 40), button_size, font_path, quit_game)

    settings_button_size = (90, 90)
    settings_button = Button(
        text="",
        pos=(screen.get_width() - settings_button_size[0] // 2 - 10, settings_button_size[1] // 2 - 10),
        size=settings_button_size,
        font_path=font_path,
        callback=open_audio_settings,
        icon_path="images/icons/s.png"
    )

    menu_running = True
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False
                return
            start_button.check_click(event)
            quit_button.check_click(event)
            settings_button.check_click(event)

        if not pygame.display.get_init():
            return

        screen.blit(bg, (0, 0))
        draw_title_with_outline(screen)
        start_button.draw(screen)
        quit_button.draw(screen)
        settings_button.draw(screen)
        pygame.display.flip()