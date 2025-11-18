import pygame
from pygame.locals import *
from PIL import Image
import random
from menu import Button, scale_image
from gameplaySettings import show_gameplay_settings
import config
from config import global_sound_manager
from gameOver import GameOverScreen

def show_tutorial(screen, font_path):
    bg = pygame.image.load('images/bg.png').convert()
    bg = pygame.transform.scale(bg, (screen.get_width(), screen.get_height()))
    
    # Load button icons
    up_icon = scale_image(pygame.image.load('images/up.png').convert_alpha(), 50)
    down_icon = scale_image(pygame.image.load('images/down.png').convert_alpha(), 50)
    space_icon = scale_image(pygame.image.load('images/space.png').convert_alpha(), 150)
    
    # Create fonts
    title_font = pygame.font.Font(font_path, 40)
    instruction_font = pygame.font.Font(font_path, 24)
    
    # Create text surfaces
    title_text = title_font.render("START GAMEPLAY", True, (0, 0, 0))
    score_text = instruction_font.render("SCORE: 0", True, (0, 0, 0))
    instruction_text = instruction_font.render("Press key to move up or down", True, (0, 0, 0))
    shoot_text = instruction_font.render("Press SPACE to shoot", True, (0, 0, 0))
    
    # Positions
    center_x = screen.get_width() // 2
    title_pos = (center_x, 100)
    score_pos = (center_x, 160)
    instruction_pos = (center_x, 220)
    up_pos = (center_x - 100, 300)
    down_pos = (center_x, 300)
    space_pos = (center_x + 100, 300)
    shoot_text_pos = (center_x, 370)
    
    # Display tutorial
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return False
            if event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                waiting = False
        
        screen.blit(bg, (0, 0))
        
        # Draw title and instructions
        screen.blit(title_text, (title_pos[0] - title_text.get_width() // 2, title_pos[1]))
        screen.blit(score_text, (score_pos[0] - score_text.get_width() // 2, score_pos[1]))
        screen.blit(instruction_text, (instruction_pos[0] - instruction_text.get_width() // 2, instruction_pos[1]))
        
        # Draw control icons
        screen.blit(up_icon, (up_pos[0] - up_icon.get_width() // 2, up_pos[1]))
        screen.blit(down_icon, (down_pos[0] - down_icon.get_width() // 2, down_pos[1]))
        screen.blit(space_icon, (space_pos[0] - space_icon.get_width() // 2, space_pos[1]))
        
        # Draw shoot instruction
        screen.blit(shoot_text, (shoot_text_pos[0] - shoot_text.get_width() // 2, shoot_text_pos[1]))
        
        pygame.display.flip()
    
    return True

# Main game loop
def run_game():
    pygame.init()
    pygame.mixer.init()
    global_sound_manager.play('helicopter_continuous', loop=True)
    # Initialize high score
    high_score = 0

    # Game settings
    game_width, game_height = 800, 500
    padding_y = 50
    bullet_cooldown = 500
    font_path = "fonts/Pixel Emulator.otf"

    difficulty_level = 0
    bird_spawn_interval = 1000
    initial_bird_speed = 2
    bird_speed = initial_bird_speed
    max_clouds_allowed = 0 # Start with 0 clouds allowed before difficulty_level 1
    cloud_spawn_interval = 3000 # Increased initial interval for spawning cloud bursts

    screen_size = (game_width, game_height)
    game_window = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Bird-Shooter')

    if not show_tutorial(game_window, font_path):
        return 

    settings_button = Button(
        text="",
        pos=(game_width - 45, 25),
        size=(90, 90),
        font_path=font_path,
        callback=lambda: show_gameplay_settings(game_window, play_again_callback=reset_game),
        icon_path="images/icons/s.png"
    )

    # Load images
    bg = scale_image(pygame.image.load('images/bg.png').convert_alpha(), game_width)
    airplane_images = [scale_image(pygame.image.load(f'images/player/fly{i}.png').convert_alpha(), 70) for i in range(2)]
    heart_images = [scale_image(pygame.image.load(f'images/hearts/heart{i}.png').convert_alpha(), 30) for i in range(8)]
    bird_images = {
        color: [
            pygame.transform.flip(scale_image(pygame.image.load(f'images/birds/{color}{i}.png').convert_alpha(), 50), True, False)
            for i in range(4)
        ] for color in ['blue', 'grey', 'red', 'yellow']
    }
    cloud_img = scale_image(pygame.image.load('images/cloud.png').convert_alpha(), 100)
    explosion_img = scale_image(pygame.image.load('images/explosion.png').convert_alpha(), 100)
    level_up_img = scale_image(pygame.image.load('images/level_up.png').convert_alpha(), 200)
    heart_pickup_img = scale_image(pygame.image.load(f'images/hearts/heart0.png').convert_alpha(), 30)
    pick_up_effect_img = scale_image(pygame.image.load('images/pick_up effect.png').convert_alpha(), 30)

    # Sprite classes
    class Explosion(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = explosion_img
            self.rect = self.image.get_rect(center=(x, y))
            self.timer = pygame.time.get_ticks()

        def update(self):
            if pygame.time.get_ticks() - self.timer > 300:
                self.kill()

    class Player(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.x, self.y, self.lives, self.score, self.image_index, self.image_angle = x, y, 3, 0, 0, 0

            self.image = airplane_images[0]  # Use first frame as initial image
            self.rect = self.image.get_rect(topleft=(self.x, self.y))
        
        def update(self):
            self.image_index = (self.image_index + 1) % len(airplane_images)
            self.image = pygame.transform.rotate(airplane_images[self.image_index], self.image_angle)
            self.rect = self.image.get_rect(topleft=(self.x, self.y))
            if pygame.sprite.spritecollide(self, bird_group, True):
                explosion_group.add(Explosion(self.rect.centerx, self.rect.centery))
                self.lives -= 1
                global_sound_manager.play('collision')

    class Bullet(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.frames = self.load_gif_frames('images/Bullet.gif')
            self.frame_index, self.rect = 0, pygame.Rect(x, y, 20, 20)

        def load_gif_frames(self, path):
            pil_gif, frames = Image.open(path), []
            try:
                while True:
                    frame = pil_gif.convert('RGBA')
                    pygame_image = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
                    frames.append(pygame.transform.scale(pygame_image, (20, 20)))
                    pil_gif.seek(pil_gif.tell() + 1)
            except EOFError:
                pass
            return frames

        def update(self):
            self.rect.x += 4
            self.frame_index = (self.frame_index + 0.2) % len(self.frames)
            self.image = self.frames[int(self.frame_index)]
            if self.rect.x > game_width:
                self.kill()
            if pygame.sprite.spritecollide(self, bird_group, True):
                explosion_group.add(Explosion(self.rect.centerx, self.rect.centery))
                player.score += 1
                global_sound_manager.play('hit_bird')
                self.kill()

        def draw(self):
            game_window.blit(self.image, self.rect)

    class Bird(pygame.sprite.Sprite):
        def __init__(self, speed):
            super().__init__()
            self.x, self.y, self.color, self.image_index = game_width, random.randint(padding_y, game_height - padding_y * 2), random.choice(['blue', 'grey', 'red', 'yellow']), 0
            self.image, self.speed = bird_images[self.color][0], speed
            self.rect = self.image.get_rect(topleft=(self.x, self.y))

        def update(self):
            self.x -= 2
            self.rect.x -= self.speed
            self.image_index = (self.image_index + 0.25) % len(bird_images[self.color])
            self.image = bird_images[self.color][int(self.image_index)]
            if self.x < 0:
                self.kill()

    class Cloud(pygame.sprite.Sprite):
        def __init__(self, offset_x=0): # Added offset_x for burst spawning
            super().__init__()
            # Randomize y position for each cloud in a burst
            self.x, self.y = game_width + offset_x, random.randint(padding_y, game_height - padding_y * 2)
            self.image, self.speed = cloud_img, bird_speed - 1 if bird_speed > 1 else 1
            self.rect = self.image.get_rect(topleft=(self.x, self.y))

        def update(self):
            self.x -= self.speed
            self.rect.x = self.x
            if self.x < -self.image.get_width():
                self.kill()

    class HeartPickup(pygame.sprite.Sprite):
        def __init__(self):
            super().__init__()
            self.x, self.y = game_width, random.randint(padding_y, game_height - padding_y * 2)
            self.image, self.speed = heart_pickup_img, 2
            self.rect = self.image.get_rect(topleft=(self.x, self.y))

        def update(self):
            self.x -= self.speed
            self.rect.x = self.x
            if self.x < 0:
                self.kill()

    class PickUpEffect(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__()
            self.image = pick_up_effect_img.copy()
            self.rect = self.image.get_rect(center=(x, y))
            self.alpha = 255
            self.fade_speed = 5
            self.y_speed = -1

        def update(self):
            self.alpha -= self.fade_speed
            self.rect.y += self.y_speed
            if self.alpha <= 0:
                self.kill()
            else:
                self.image.set_alpha(self.alpha)


    def increase_difficulty():
        nonlocal difficulty_level, bird_spawn_interval, bird_speed, max_clouds_allowed, cloud_spawn_interval
        difficulty_level += 1
        bird_spawn_interval = max(500, bird_spawn_interval - 50)
        if difficulty_level >= 1:
            bird_speed += 1
            # Increase max clouds allowed only after level 20 (difficulty_level 1)
            if max_clouds_allowed < 10: # Cap max clouds to prevent too many
                max_clouds_allowed += 1
            cloud_spawn_interval = max(1500, cloud_spawn_interval - 200) # Faster cloud bursts

    def reset_game():
        nonlocal player, last_bullet_time, next_bird, next_heart_pickup, difficulty_level, bird_spawn_interval, bird_speed, max_clouds_allowed, cloud_spawn_interval, next_cloud, running
        player_group.empty(), bullet_group.empty(), bird_group.empty(), cloud_group.empty(), explosion_group.empty(), heart_pickup_group.empty(), pick_up_effect_group.empty()
        player = Player(30, game_height // 2)
        player_group.add(player)
        last_bullet_time, next_bird, next_heart_pickup = pygame.time.get_ticks(), pygame.time.get_ticks(), pygame.time.get_ticks()
        global_sound_manager.stop_all()
        global_sound_manager.play('helicopter_continuous', loop=True)
        difficulty_level = 0
        bird_spawn_interval = 1000
        bird_speed = initial_bird_speed
        max_clouds_allowed = 0 # Reset to 0 clouds allowed
        cloud_spawn_interval = 3000 # Reset cloud spawn interval
        next_cloud = pygame.time.get_ticks() + random.randint(500, cloud_spawn_interval)
        running = True

    # Groups
    player_group, bullet_group, bird_group, cloud_group = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group()
    explosion_group, heart_pickup_group = pygame.sprite.Group(), pygame.sprite.Group()
    pick_up_effect_group = pygame.sprite.Group()

    player = Player(30, game_height // 2)
    player_group.add(player)

    clock, fps = pygame.time.Clock(), 120
    heart_image_index, bg_scroll, running = 0, 0, True
    last_bullet_time, next_bird, next_heart_pickup = pygame.time.get_ticks(), pygame.time.get_ticks(), pygame.time.get_ticks()
    next_cloud = pygame.time.get_ticks() + random.randint(500, cloud_spawn_interval)

    while running:
        current_time = pygame.time.get_ticks()

        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            settings_button.check_click(event)

        keys = pygame.key.get_pressed()
        if keys[K_UP] and player.rect.top > padding_y:
            player.y -= 2
            player.image_angle = 15
        elif keys[K_DOWN] and player.rect.bottom < game_height - padding_y:
            player.y += 2
            player.image_angle = -15
        else:
            player.image_angle = 0

        if keys[K_SPACE] and last_bullet_time + bullet_cooldown < current_time:
            bullet_group.add(Bullet(player.x + airplane_images[0].get_width(), player.y + airplane_images[0].get_height() // 2))
            last_bullet_time = current_time
            global_sound_manager.play('bullet')

        if current_time > next_bird:
            bird_group.add(Bird(bird_speed))
            next_bird = current_time + bird_spawn_interval + random.randint(-200, 200)

        if player.lives < 3 and current_time > next_heart_pickup:
            heart_pickup_group.add(HeartPickup())
            next_heart_pickup = current_time + random.randint(4000, 7000)

        # Cloud Spawning Logic (after difficulty level 1, in bursts)
        if difficulty_level >= 1 and len(cloud_group) < max_clouds_allowed and current_time > next_cloud:
            num_clouds_to_spawn = random.randint(3, 5)
            # Ensure we don't exceed max_clouds_allowed with the burst
            num_clouds_to_spawn = min(num_clouds_to_spawn, max_clouds_allowed - len(cloud_group))
            
            for i in range(num_clouds_to_spawn):
                # Offset new clouds slightly to spread them out
                cloud_group.add(Cloud(offset_x=i * random.randint(50, 100))) # Randomize spread
            next_cloud = current_time + random.randint(1500, cloud_spawn_interval) # Next burst timer

        # Level up logic
        if player.score > 0 and player.score % 20 == 0 and difficulty_level < (player.score // 20):
            increase_difficulty()

        # Update
        player_group.update()
        bullet_group.update()
        bird_group.update()
        cloud_group.update()
        explosion_group.update()
        heart_pickup_group.update()
        pick_up_effect_group.update()

        for heart in pygame.sprite.spritecollide(player, heart_pickup_group, True):
            player.lives = min(player.lives + 1, 3)
            global_sound_manager.play('pickup_heart')
            pick_up_effect = PickUpEffect(heart.rect.centerx, heart.rect.centery)
            pick_up_effect_group.add(pick_up_effect)

        for cloud in pygame.sprite.spritecollide(player, cloud_group, True):
            player.lives -= 1
            explosion_group.add(Explosion(cloud.rect.centerx, cloud.rect.centery))
            global_sound_manager.play('collision')

        # Draw
        for offset in [0, game_width]:
            game_window.blit(bg, (offset - bg_scroll, 0))
        bg_scroll = (bg_scroll + 1) % game_width

        player_group.draw(game_window)
        for bullet in bullet_group:
            bullet.draw()
        bird_group.draw(game_window)
        cloud_group.draw(game_window)
        explosion_group.draw(game_window)
        heart_pickup_group.draw(game_window)
        pick_up_effect_group.draw(game_window)

        if player.score in [20, 40, 60]:
            game_window.blit(level_up_img, (game_width // 2 - level_up_img.get_width() // 2, game_height // 2 - level_up_img.get_height() // 2 -35))

        for i in range(player.lives):
            game_window.blit(heart_images[int(heart_image_index)], (10 + i * 40, 10))
        heart_image_index = (heart_image_index + 0.1) % len(heart_images)

        font = pygame.font.Font(None, 25)
        score_text = font.render(f'Score: {player.score}', True, (0, 0, 0))
        game_window.blit(score_text, (190, 15))

        settings_button.draw(game_window)
        pygame.display.update()

        # Game Over
        if player.lives <= 0:
            global_sound_manager.stop_all()

            if player.score > high_score:
                high_score = player.score

            game_over_screen = GameOverScreen(game_window, "fonts/Pixel Emulator.otf")
            choice = game_over_screen.show(latest_score=player.score, highest_score=high_score)

            if choice == "restart":
                if config.audio_enabled:
                    if not pygame.mixer.music.get_busy():
                        try:
                            pygame.mixer.music.load("audio/background_music.mp3")
                            pygame.mixer.music.play(-1, fade_ms=1000)
                        except Exception as e:
                            print("Error loading background music:", e)
                    else:
                        pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.pause()
                reset_game()


            elif choice == "menu":
                if config.audio_enabled:
                    if not pygame.mixer.music.get_busy():
                        try:
                            pygame.mixer.music.load("audio/background_music.mp3")
                            pygame.mixer.music.play(-1, fade_ms=1000)
                        except Exception as e:
                            print("Error loading background music:", e)
                    else:
                        pygame.mixer.music.unpause()
                else:
                    pygame.mixer.music.pause()
                return

            elif choice == "quit":
                running = False

    pygame.quit()
