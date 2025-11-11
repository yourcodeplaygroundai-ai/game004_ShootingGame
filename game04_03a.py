import pygame
import random
import os
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 1024, 1024
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jet Fighter Game")
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paths
BASE_PATH = os.path.dirname(__file__)
BG_PATH = os.path.join(BASE_PATH, "background")
PIC_PATH = os.path.join(BASE_PATH, "pic")
SOUND_PATH = os.path.join(BASE_PATH, "sound")

# Load assets
def load_image(folder, filename, size=None):
    path = os.path.join(BASE_PATH, folder, filename)
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

def load_sound(filename):
    path = os.path.join(SOUND_PATH, filename)
    return pygame.mixer.Sound(path)

# Player
player_img = load_image("pic", "player.png", (120, 120))
player_rect = player_img.get_rect()
player_rect.centerx = WIDTH // 2
player_rect.bottom = HEIGHT - 50
player_speed = 8
player_base_speed = 8

# Bullets
bullet_img = pygame.Surface((10, 20), pygame.SRCALPHA)
pygame.draw.polygon(bullet_img, (255, 255, 0), [(0,0), (10,0), (5,20)])
bullet_img = pygame.transform.scale(bullet_img, (15, 30))
bullets = []
BULLET_SPEED = 15
multi_bullet = False

# Enemies
enemy_images = [
    load_image("pic", f"enemy0{i}.png", (120, 120)) for i in range(1, 7)
]
boss_images = [
    load_image("pic", f"enemy3{i}.png", (250, 250)) for i in range(1, 4)
]
enemies = []
bosses = []

# Sounds
bg_music = None
current_bg_music = None
bingo1_sound = load_sound("bingo1.mp3")
bingo2_sound = load_sound("bingo2.mp3")
gameover_sound = load_sound("gameover.mp3")

# Backgrounds
bg_images = {
    "low": load_image("background", "bg01.jpeg", (WIDTH, HEIGHT)),
    "mid": load_image("background", "bg02.jpeg", (WIDTH, HEIGHT)),
    "high": load_image("background", "bg03.jpeg", (WIDTH, HEIGHT))
}
current_bg = bg_images["low"]

# Game variables
score = 0
game_over = False
font = pygame.font.SysFont("Arial", 60)
small_font = pygame.font.SysFont("Arial", 40)

# Spawn timers
enemy_spawn_timer = 0
boss_spawn_timer = 0

# Boss health (hits needed)
boss_health = {boss: 5 for boss in range(len(boss_images))}

# Functions
def play_background_music(level):
    global current_bg_music
    music_file = None
    if level <= 2:
        music_file = "background01.mp3"
    elif level <= 4:
        music_file = "background02.mp3"
    else:
        music_file = "background03.mp3"
    
    if current_bg_music != music_file:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(os.path.join(SOUND_PATH, music_file))
        pygame.mixer.music.play(-1)
        current_bg_music = music_file

def update_background():
    global current_bg
    if score <= 2:
        current_bg = bg_images["low"]
    elif score <= 4:
        current_bg = bg_images["mid"]
    else:
        current_bg = bg_images["high"]
    play_background_music(score)

def spawn_enemy():
    img = random.choice(enemy_images)
    rect = img.get_rect()
    side = random.choice(["top", "bottom", "left", "right"])
    if side == "top":
        rect.bottom = 0
        rect.x = random.randint(0, WIDTH - rect.width)
    elif side == "bottom":
        rect.top = HEIGHT
        rect.x = random.randint(0, WIDTH - rect.width)
    elif side == "left":
        rect.right = 0
        rect.y = random.randint(0, HEIGHT - rect.height)
    else:
        rect.left = WIDTH
        rect.y = random.randint(0, HEIGHT - rect.height)
    
    speed = random.uniform(1.5, 3.5)
    angle = random.uniform(-0.1, 0.1)
    enemies.append({"rect": rect, "img": img, "speed": speed, "angle": angle})

def spawn_boss():
    if score > 4 and random.random() < 0.003:
        img = random.choice(boss_images)
        scaled_img = pygame.transform.scale(img, (250, 250))
        rect = scaled_img.get_rect()
        side = random.choice(["top", "left", "right"])
        if side == "top":
            rect.bottom = 0
            rect.x = random.randint(100, WIDTH - 350)
        elif side == "left":
            rect.right = 0
            rect.y = random.randint(100, HEIGHT - 350)
        else:
            rect.left = WIDTH
            rect.y = random.randint(100, HEIGHT - 350)
        speed = random.uniform(0.8, 1.8)
        bosses.append({"rect": rect, "img": scaled_img, "orig_img": img, "speed": speed, "hits": 5, "id": bosses[-1]["id"] + 1 if bosses else 0})

def reset_game():
    global player_rect, bullets, enemies, bosses, score, game_over, player_speed, multi_bullet
    player_rect.centerx = WIDTH // 2
    player_rect.bottom = HEIGHT - 50
    bullets = []
    enemies = []
    bosses = []
    score = 0
    game_over = False
    player_speed = player_base_speed
    multi_bullet = False
    update_background()

# Main game loop
running = True
update_background()

while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()
            if event.key == pygame.K_SPACE and not game_over:
                if multi_bullet and score > 4:
                    # Triple bullet
                    for angle in [-0.3, 0, 0.3]:
                        bullets.append({
                            "rect": bullet_img.get_rect(centerx=59+player_rect.centerx, top=player_rect.top),
                            "angle": angle
                        })
                else:
                    bullets.append({
                        "rect": bullet_img.get_rect(centerx=player_rect.centerx, top=player_rect.top),
                        "angle": 0
                    })

    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
            player_rect.x += player_speed
        if keys[pygame.K_UP] and player_rect.top > 0:
            player_rect.y -= player_speed
        if keys[pygame.K_DOWN] and player_rect.bottom < HEIGHT:
            player_rect.y += player_speed

        # Update background & music
        update_background()

        # Speed boost at score 4+
        if score >= 4:
            player_speed = player_base_speed * 1.5
            multi_bullet = True
        else:
            player_speed = player_base_speed
            multi_bullet = False

        # Spawn enemies
        enemy_spawn_timer += 1
        if enemy_spawn_timer > (60 if score <= 4 else 40):
            spawn_enemy()
            enemy_spawn_timer = 0

        # Spawn bosses rarely
        spawn_boss()

        # Update bullets
        for bullet in bullets[:]:
            bullet["rect"].y -= BULLET_SPEED * (1 + abs(bullet["angle"]) * 0.5)
            bullet["rect"].x += int(BULLET_SPEED * bullet["angle"] * 10)
            if bullet["rect"].bottom < 0:
                bullets.remove(bullet)

        # Update enemies
        for enemy in enemies[:]:
            dx = player_rect.centerx - enemy["rect"].centerx
            dy = player_rect.centery - enemy["rect"].centery
            dist = (dx**2 + dy**2)**0.5
            if dist > 0:
                enemy["rect"].x += dx / dist * enemy["speed"]
                enemy["rect"].y += dy / dist * enemy["speed"]

        # Update bosses
        for boss in bosses[:]:
            dx = player_rect.centerx - boss["rect"].centerx
            dy = player_rect.centery - boss["rect"].centery
            dist = (dx**2 + dy**2)**0.5
            if dist > 50:
                boss["rect"].x += dx / dist * boss["speed"]
                boss["rect"].y += dy / dist * boss["speed"]

        # Collision: bullet vs enemy
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if bullet["rect"].colliderect(enemy["rect"]):
                    if bullet in bullets:
                        bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 1
                    bingo1_sound.play()
                    break

            # Bullet vs boss
            for boss in bosses[:]:
                if bullet["rect"].colliderect(boss["rect"]):
                    if bullet in bullets:
                        bullets.remove(bullet)
                    boss["hits"] -= 1
                    # Shrink boss
                    new_size = int(250 * (0.9 ** (5 - boss["hits"])))
                    new_size = max(100, new_size)
                    boss["img"] = pygame.transform.scale(boss["orig_img"], (new_size, new_size))
                    boss["rect"] = boss["img"].get_rect(center=boss["rect"].center)
                    
                    if boss["hits"] <= 0:
                        bosses.remove(boss)
                        score += 1
                        bingo2_sound.play()
                    else:
                        bingo2_sound.play()
                    break

        # Collision: player vs enemy
        for enemy in enemies:
            if player_rect.colliderect(enemy["rect"]):
                game_over = True
                gameover_sound.play()
                pygame.mixer.music.stop()

        for boss in bosses:
            if player_rect.colliderect(boss["rect"]):
                game_over = True
                gameover_sound.play()
                pygame.mixer.music.stop()

    # Draw
    screen.blit(current_bg, (0, 0))
    
    if not game_over:
        screen.blit(player_img, player_rect)
        
        for bullet in bullets:
            screen.blit(bullet_img, bullet["rect"])
        
        for enemy in enemies:
            screen.blit(enemy["img"], enemy["rect"])
        
        for boss in bosses:
            screen.blit(boss["img"], boss["rect"])
        
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))
    
    else:
        gameover_text = font.render("GAME OVER", True, WHITE)
        restart_text = small_font.render("Press R to restart", True, WHITE)
        screen.blit(gameover_text, (WIDTH//2 - gameover_text.get_width()//2, HEIGHT//2 - 100))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 20))

    pygame.display.flip()

pygame.quit()
sys.exit()