import pygame
import random
import os
import sys

# ============================================================
# INITIALIZATION & PYINSTALLER PATH FIX
# ============================================================

pygame.init()

try:
    pygame.mixer.init()
except:
    pass

if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# [ANDROID UPDATE] Dynamic Screen Resolution
infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h

# Fullscreen mode for Android
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Cyber Blocks Breaker - Pro Touch Edition")

clock = pygame.time.Clock()
FPS = 60

# ============================================================
# COLORS & FONTS
# ============================================================
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (148, 0, 211)
RED = (255, 50, 50)
GOLD = (255, 215, 0)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
ORANGE = (255, 140, 0)
LIGHT_BLUE = (0, 191, 255)
BLUE = (50, 100, 255)
DARK_BLUE = (20, 30, 100)
PINK = (255, 50, 180)

font = pygame.font.SysFont("Arial", 28, bold=True)
small_font = pygame.font.SysFont("Arial", 22, bold=True)
medium_font = pygame.font.SysFont("Arial", 38, bold=True)
big_font = pygame.font.SysFont("Arial", 60, bold=True)
huge_font = pygame.font.SysFont("Arial", 75, bold=True)

# ============================================================
# BACKGROUND IMAGE
# ============================================================
has_bg_image = True
try:
    # Ensure this matches the EXACT file name (case-sensitive)
    bg_image = pygame.image.load(os.path.join(BASE_DIR, "imageS.jpg")).convert()
    bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
except Exception as e:
    has_bg_image = False

def draw_background():
    if has_bg_image:
        screen.blit(bg_image, (0, 0))
    else:
        screen.fill(DARK_BLUE)

# ============================================================
# SOUNDS & MUSIC
# ============================================================
has_sounds = True
try:
    catch_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "m.mp3"))
    gameover_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, "gameover.wav"))
except:
    has_sounds = False

has_bg_music = True
try:
    pygame.mixer.music.load(os.path.join(BASE_DIR, "block braker.mp3"))
    pygame.mixer.music.set_volume(0.3)
except:
    has_bg_music = False

# ============================================================
# GAME STATES & VARIABLES
# ============================================================
MENU = "menu"
HOW_TO_PLAY = "how_to_play"
PLAYING = "playing"
GAME_OVER = "game_over"
LEVEL_CLEAR = "level_clear"
VICTORY = "victory"

game_state = MENU
is_paused = False

current_level = 1
MAX_LEVELS = 10
score = 0
high_score = 0
lives = 5
combo = 0
combo_timer = 0
COMBO_TIME = 90

HIGH_SCORE_FILE = os.path.join(BASE_DIR, "highscore.txt")

def load_high_score():
    global high_score
    try:
        with open(HIGH_SCORE_FILE, "r") as file:
            high_score = int(file.read())
    except:
        high_score = 0

def save_high_score():
    try:
        with open(HIGH_SCORE_FILE, "w") as file:
            file.write(str(high_score))
    except:
        pass

load_high_score()

# ============================================================
# PLAYER, BALL & BLOCKS
# ============================================================
basket_width = 150
basket_height = 20
basket_x = 0
basket_y = SCREEN_HEIGHT - 65

def setup_paddle():
    global basket_width, basket_x
    basket_width = max(160 - (current_level * 4), 120)
    basket_x = (SCREEN_WIDTH - basket_width) // 2

ball_radius = 12
base_ball_speed = 5
ball_x = 0
ball_y = 0
ball_dx = 0
ball_dy = 0

def reset_ball_on_paddle():
    global ball_x, ball_y, ball_dx, ball_dy
    ball_x = basket_x + basket_width // 2
    ball_y = basket_y - ball_radius - 2
    speed = base_ball_speed
    ball_dx = random.choice([-speed, speed])
    ball_dy = -speed

block_width = int(SCREEN_WIDTH * 0.06)
block_height = 28
block_padding = 8
BLOCK_COLS = 13
block_offset_top = int(SCREEN_HEIGHT * 0.15)
blocks = []

def create_blocks(level):
    rows = 4 if level <= 2 else (5 if level <= 4 else (6 if level <= 6 else (7 if level <= 8 else 8)))
    blocks_list = []
    total_width = BLOCK_COLS * block_width + (BLOCK_COLS - 1) * block_padding
    start_x = (SCREEN_WIDTH - total_width) // 2

    for row in range(rows):
        for col in range(BLOCK_COLS):
            x = start_x + col * (block_width + block_padding)
            y = block_offset_top + row * (block_height + block_padding)

            rand_num = random.randint(1, 100)
            if level >= 3 and rand_num <= 10:
                b_type, health = "strong", 2
            elif level >= 5 and rand_num <= 18:
                b_type, health = "gold", 3
            elif level >= 2 and rand_num <= 25:
                b_type, health = "power", 1
            else:
                b_type, health = "normal", 1

            blocks_list.append({
                "rect": pygame.Rect(x, y, block_width, block_height),
                "type": b_type,
                "health": health,
                "max_health": health
            })
    return blocks_list

# ============================================================
# BOSS & POWER-UPS
# ============================================================
boss = None

def create_boss():
    global boss
    boss_w = int(SCREEN_WIDTH * 0.4)
    boss = {
        "rect": pygame.Rect(SCREEN_WIDTH // 2 - (boss_w//2), int(SCREEN_HEIGHT*0.18), boss_w, 70),
        "health": 25,
        "max_health": 25,
        "direction": 1,
        "speed": 4
    }

powerups = []
extra_balls = []
particles = []

def create_powerup(x, y):
    powerups.append({
        "x": x, "y": y,
        "type": random.choice(["big_paddle", "multi_ball", "extra_life", "slow_ball", "fire_ball"]),
        "speed": 4, "size": 18
    })

def create_extra_ball():
    extra_balls.append({
        "x": ball_x, "y": ball_y,
        "dx": random.choice([-base_ball_speed, base_ball_speed]),
        "dy": -base_ball_speed,
        "radius": ball_radius
    })

def create_particles(x, y, color):
    for _ in range(10):
        particles.append({
            "x": x, "y": y,
            "dx": random.uniform(-3, 3), "dy": random.uniform(-3, 3),
            "life": random.randint(20, 35), "color": color, "size": random.randint(2, 4)
        })

def update_particles():
    for p in particles[:]:
        p["x"] += p["dx"]
        p["y"] += p["dy"]
        p["life"] -= 1
        if p["life"] <= 0:
            particles.remove(p)

def draw_particles():
    for p in particles:
        pygame.draw.circle(screen, p["color"], (int(p["x"]), int(p["y"])), p["size"])

# ============================================================
# LOGIC FUNCTIONS
# ============================================================
def setup_level(level):
    global blocks, base_ball_speed, boss
    base_ball_speed = 5 + level * 0.4
    setup_paddle()
    blocks = create_blocks(level)
    powerups.clear()
    extra_balls.clear()
    global combo, combo_timer
    combo = 0
    combo_timer = 0
    boss = None
    if level == MAX_LEVELS:
        create_boss()
    reset_ball_on_paddle()

def start_game():
    global score, lives, current_level, game_state, is_paused
    score = 0
    lives = 5
    current_level = 1
    is_paused = False
    setup_level(current_level)
    game_state = PLAYING
    if has_bg_music:
        pygame.mixer.music.play(-1)

def add_score(amount):
    global score, high_score
    score += amount
    if score > high_score:
        high_score = score
        save_high_score()

def get_block_color(b):
    if b["type"] == "normal": return CYAN
    elif b["type"] == "strong": return RED
    elif b["type"] == "gold": return GOLD
    elif b["type"] == "power": return PURPLE
    return WHITE

def hit_block(block):
    global combo, combo_timer
    block["health"] -= 1
    combo += 1
    combo_timer = COMBO_TIME
    add_score(10 * combo)
    create_particles(block["rect"].centerx, block["rect"].centery, get_block_color(block))

    if block["health"] <= 0:
        if block["type"] == "power":
            create_powerup(block["rect"].centerx, block["rect"].centery)
        if block["type"] == "gold": add_score(20)
        elif block["type"] == "strong": add_score(15)
        else: add_score(10)
        blocks.remove(block)

def activate_powerup(p_type):
    global basket_width, lives, ball_dx, ball_dy
    if p_type == "big_paddle": basket_width = min(basket_width + 60, int(SCREEN_WIDTH*0.4))
    elif p_type == "extra_life": lives += 1
    elif p_type == "slow_ball": ball_dx *= 0.6; ball_dy *= 0.6
    elif p_type == "multi_ball": create_extra_ball()
    elif p_type == "fire_ball": ball_dx *= 1.4; ball_dy *= 1.4

def complete_level():
    global current_level, game_state
    if current_level == MAX_LEVELS:
        game_state = VICTORY
        if has_bg_music: pygame.mixer.music.stop()
    else:
        game_state = LEVEL_CLEAR

# ============================================================
# UI BUTTON RECTANGLES (Dynamic sizing for Android)
# ============================================================
btn_play_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 40, 360, 60)
btn_how_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 50, 360, 60)
btn_close_rect = pygame.Rect(SCREEN_WIDTH - 70, 30, 45, 45)
btn_pause_icon_rect = pygame.Rect(SCREEN_WIDTH - 65, 15, 45, 45)

btn_resume_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 80, 300, 55)
btn_newgame_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 55)
btn_exit_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 80, 300, 55)

# ============================================================
# UPDATES & DRAWING
# ============================================================
def update_game():
    global basket_x, ball_x, ball_y, ball_dx, ball_dy, lives, game_state, combo, combo_timer, boss

    mouse_x, _ = pygame.mouse.get_pos()
    basket_x = mouse_x - basket_width // 2
    basket_x = max(0, min(basket_x, SCREEN_WIDTH - basket_width))

    ball_x += ball_dx
    ball_y += ball_dy

    if ball_x - ball_radius <= 0:
        ball_x = ball_radius
        ball_dx *= -1
    if ball_x + ball_radius >= SCREEN_WIDTH:
        ball_x = SCREEN_WIDTH - ball_radius
        ball_dx *= -1
    if ball_y - ball_radius <= 0:
        ball_y = ball_radius
        ball_dy *= -1

    paddle_rect = pygame.Rect(basket_x, basket_y, basket_width, basket_height)
    ball_rect = pygame.Rect(int(ball_x - ball_radius), int(ball_y - ball_radius), ball_radius * 2, ball_radius * 2)

    if ball_rect.colliderect(paddle_rect) and ball_dy > 0:
        paddle_center = basket_x + basket_width / 2
        normalized = (ball_x - paddle_center) / (basket_width / 2)
        ball_dx = normalized * base_ball_speed * 1.4
        ball_dy = -abs(base_ball_speed)
        if has_sounds: catch_sound.play()

    for block in blocks[:]:
        if ball_rect.colliderect(block["rect"]):
            ball_dy *= -1
            hit_block(block)
            break

    if boss is not None:
        boss["rect"].x += boss["speed"] * boss["direction"]
        if boss["rect"].left <= 80: boss["direction"] = 1
        if boss["rect"].right >= SCREEN_WIDTH - 80: boss["direction"] = -1
        if ball_rect.colliderect(boss["rect"]):
            ball_dy *= -1
            boss["health"] -= 1
            add_score(50)
            create_particles(ball_x, ball_y, RED)
            if boss["health"] <= 0:
                boss = None
                add_score(1000)
                complete_level()

    if ball_y > SCREEN_HEIGHT:
        lives -= 1
        combo = 0
        combo_timer = 0
        if lives <= 0:
            game_state = GAME_OVER
            if has_sounds: gameover_sound.play()
            if has_bg_music: pygame.mixer.music.stop()
        else:
            reset_ball_on_paddle()

    for p in powerups[:]:
        p["y"] += p["speed"]
        rect = pygame.Rect(p["x"] - p["size"], p["y"] - p["size"], p["size"] * 2, p["size"] * 2)
        if rect.colliderect(paddle_rect):
            activate_powerup(p["type"])
            create_particles(p["x"], p["y"], GOLD)
            powerups.remove(p)
        elif p["y"] > SCREEN_HEIGHT:
            powerups.remove(p)

    for extra in extra_balls[:]:
        extra["x"] += extra["dx"]
        extra["y"] += extra["dy"]
        if extra["x"] <= 0 or extra["x"] >= SCREEN_WIDTH: extra["dx"] *= -1
        if extra["y"] <= 0: extra["dy"] *= -1

        rect = pygame.Rect(int(extra["x"] - extra["radius"]), int(extra["y"] - extra["radius"]), extra["radius"] * 2, extra["radius"] * 2)
        if rect.colliderect(paddle_rect) and extra["dy"] > 0:
            extra["dy"] *= -1

        for block in blocks[:]:
            if rect.colliderect(block["rect"]):
                extra["dy"] *= -1
                hit_block(block)
                break
        if extra["y"] > SCREEN_HEIGHT:
            extra_balls.remove(extra)

def draw_hud():
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {current_level}/{MAX_LEVELS}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, RED)
    
    screen.blit(score_text, (20, 15))
    screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 15))
    screen.blit(lives_text, (SCREEN_WIDTH - 180, 15))

    pygame.draw.rect(screen, DARK_BLUE, btn_pause_icon_rect, border_radius=8)
    pygame.draw.rect(screen, CYAN, btn_pause_icon_rect, 2, border_radius=8)
    pause_icon_txt = font.render("||", True, CYAN)
    screen.blit(pause_icon_txt, (btn_pause_icon_rect.centerx - pause_icon_txt.get_width() // 2, btn_pause_icon_rect.centery - pause_icon_txt.get_height() // 2))

def draw_game():
    draw_background()
    draw_hud()
    for block in blocks:
        color = get_block_color(block)
        pygame.draw.rect(screen, color, block["rect"], border_radius=5)
        pygame.draw.rect(screen, WHITE, block["rect"], 2, border_radius=5)
    
    if boss is not None:
        pygame.draw.rect(screen, RED, boss["rect"], border_radius=15)
        pygame.draw.rect(screen, BLACK, boss["rect"], 4, border_radius=15)
        bar_width = boss["rect"].width - 40
        hp_pct = boss["health"] / boss["max_health"]
        pygame.draw.rect(screen, BLACK, (boss["rect"].centerx - bar_width // 2, boss["rect"].centery + 45, bar_width, 10))
        pygame.draw.rect(screen, RED, (boss["rect"].centerx - bar_width // 2, boss["rect"].centery + 45, int(bar_width * hp_pct), 10))

    for p in powerups:
        pygame.draw.circle(screen, GREEN, (int(p["x"]), int(p["y"])), 16)
        txt = small_font.render("P", True, BLACK)
        screen.blit(txt, (int(p["x"]) - txt.get_width() // 2, int(p["y"]) - txt.get_height() // 2))

    draw_particles()
    pygame.draw.rect(screen, ORANGE, (basket_x, basket_y, basket_width, basket_height), border_radius=7)
    pygame.draw.rect(screen, WHITE, (basket_x, basket_y, basket_width, basket_height), 2, border_radius=7)

    pygame.draw.circle(screen, BLUE, (int(ball_x), int(ball_y)), ball_radius)
    pygame.draw.circle(screen, WHITE, (int(ball_x), int(ball_y)), ball_radius, 2)

    for extra in extra_balls:
        pygame.draw.circle(screen, CYAN, (int(extra["x"]), int(extra["y"])), extra["radius"])

def draw_screens():
    draw_background()
    if game_state == MENU:
        title = huge_font.render("CYBER BLOCKS BREAKER", True, CYAN)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 180))
        pygame.draw.rect(screen, GREEN, btn_play_rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, btn_play_rect, 3, border_radius=12)
        play_txt = medium_font.render("PLAY", True, BLACK)
        screen.blit(play_txt, (btn_play_rect.centerx - play_txt.get_width() // 2, btn_play_rect.centery - play_txt.get_height() // 2))
        
        pygame.draw.rect(screen, BLUE, btn_how_rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, btn_how_rect, 3, border_radius=12)
        how_txt = medium_font.render("How to play", True, WHITE)
        screen.blit(how_txt, (btn_how_rect.centerx - how_txt.get_width() // 2, btn_how_rect.centery - how_txt.get_height() // 2))
    elif game_state == LEVEL_CLEAR:
        title = huge_font.render(f"LEVEL {current_level} CLEARED!", True, GREEN)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        next_txt = font.render("Tap anywhere for Next Level", True, WHITE)
        screen.blit(next_txt, (SCREEN_WIDTH // 2 - next_txt.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
    elif game_state == GAME_OVER:
        title = huge_font.render("GAME OVER", True, RED)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        r_txt = font.render("Tap anywhere to Restart", True, WHITE)
        screen.blit(r_txt, (SCREEN_WIDTH // 2 - r_txt.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

# ============================================================
# MAIN LOOP
# ============================================================
running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if game_state == MENU:
                if btn_play_rect.collidepoint(mouse_pos): start_game()
                elif btn_how_rect.collidepoint(mouse_pos): game_state = HOW_TO_PLAY
            elif game_state == HOW_TO_PLAY:
                if btn_close_rect.collidepoint(mouse_pos): game_state = MENU
            elif game_state == PLAYING:
                if not is_paused and btn_pause_icon_rect.collidepoint(mouse_pos):
                    is_paused = True
                    if has_bg_music: pygame.mixer.music.pause()
                elif is_paused:
                    if btn_resume_rect.collidepoint(mouse_pos):
                        is_paused = False
                        if has_bg_music: pygame.mixer.music.unpause()
                    elif btn_newgame_rect.collidepoint(mouse_pos):
                        is_paused = False
                        start_game()
                    elif btn_exit_rect.collidepoint(mouse_pos):
                        is_paused = False
                        game_state = MENU
                        if has_bg_music: pygame.mixer.music.stop()
            elif game_state == LEVEL_CLEAR:
                current_level += 1
                lives += 2
                setup_level(current_level)
                game_state = PLAYING
            elif game_state in [GAME_OVER, VICTORY]:
                start_game()

    if game_state == PLAYING and not is_paused:
        update_game()
        update_particles()
        if combo_timer > 0: combo_timer -= 1
        else: combo = 0
        
        if current_level != MAX_LEVELS and len(blocks) == 0: complete_level()
        elif current_level == MAX_LEVELS and boss is None: game_state = VICTORY

    if game_state == PLAYING:
        draw_game()
        if is_paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(190)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            pygame.draw.rect(screen, GREEN, btn_resume_rect, border_radius=10)
            res_txt = font.render("Resume", True, BLACK)
            screen.blit(res_txt, (btn_resume_rect.centerx - res_txt.get_width() // 2, btn_resume_rect.centery - res_txt.get_height() // 2))
            pygame.draw.rect(screen, BLUE, btn_newgame_rect, border_radius=10)
            new_txt = font.render("New Game", True, WHITE)
            screen.blit(new_txt, (btn_newgame_rect.centerx - new_txt.get_width() // 2, btn_newgame_rect.centery - new_txt.get_height() // 2))
            pygame.draw.rect(screen, RED, btn_exit_rect, border_radius=10)
            exit_txt = font.render("Exit to Menu", True, WHITE)
            screen.blit(exit_txt, (btn_exit_rect.centerx - exit_txt.get_width() // 2, btn_exit_rect.centery - exit_txt.get_height() // 2))
    else:
        draw_screens()

    pygame.display.flip()

pygame.quit()
sys.exit()