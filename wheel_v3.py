import pygame
import sys
import random
import pandas as pd

pygame.init()

WIDTH, HEIGHT = 1200, 700  
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Vertical Wheel of Fortune")

BACKGROUND_COLOR_TOP = (201, 218, 167) 
BACKGROUND_COLOR_BOTTOM = (201, 218, 167)  
TEXT_COLOR = (106, 77, 139)
BUTTON_COLOR = (70, 70, 70)
CONFETTI_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
TRIANGLE_COLOR = (225, 15, 15)  

font = pygame.font.Font(None, 74)
button_font = pygame.font.Font(None, 50)

df = pd.read_excel("spread.xlsx", header=None)
headers = df.iloc[0]
df = df.iloc[1:]
df.columns = headers
df = df.loc[:, df.columns.notna()]
df = df.dropna(axis=0, how='all')

theme_picks = []
unpacked_theme_picks = []
for name, themes in df.items():
    themes_counts = themes.value_counts()
    person_picks = [(theme, name, count) for (theme, count) in zip(themes_counts.index, themes_counts)]
    theme_picks += person_picks
    if name in ["mikołaj"]:
        for i in range(3):
            person_picks = [("ddduuppaaa", "dupa", 1) for (theme, count) in zip(themes_counts.index, themes_counts)]
            theme_picks += person_picks

for theme, name, count in theme_picks:
    for _ in range(count):
        if name not in ['rafal', 'grzeslaw', 'lokator', 'staska', 'ewa', 'renata', 'wik']:
            unpacked_theme_picks.append((theme, name))

random.shuffle(unpacked_theme_picks)

def render_text(text, opacity, y_pos):
    text_surface = font.render(f"{text[0]} by: {text[1]}", True, TEXT_COLOR)
    text_surface.set_alpha(opacity)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, y_pos))
    screen.blit(text_surface, text_rect)

def draw_gradient_background():
    for i in range(HEIGHT):
        color = [
            BACKGROUND_COLOR_TOP[j] + (BACKGROUND_COLOR_BOTTOM[j] - BACKGROUND_COLOR_TOP[j]) * i // HEIGHT
            for j in range(3)
        ]
        pygame.draw.line(screen, color, (0, i), (WIDTH, i))

def draw_wheel(center_index, offset_y):
    draw_gradient_background()
    positions = [-3, -2, -1, 0, 1, 2, 3]
    opacities = [15, 30, 90, 255, 90, 30, 15]

    for i, pos in enumerate(positions):
        pick_index = (center_index + pos) % len(unpacked_theme_picks)
        y_pos = HEIGHT // 2 + pos * 80 + offset_y
        render_text(unpacked_theme_picks[pick_index], opacities[i], y_pos)
    
    triangle_width = 40
    triangle_height = 20
    border_offset = 500
    pygame.draw.polygon(screen, TRIANGLE_COLOR, [
        (WIDTH // 2 - border_offset - triangle_width, HEIGHT // 2 - triangle_height),
        (WIDTH // 2 - border_offset - triangle_width, HEIGHT // 2 + triangle_height),
        (WIDTH // 2 - border_offset - triangle_width + 20, HEIGHT // 2)
    ])
    pygame.draw.polygon(screen, TRIANGLE_COLOR, [
        (WIDTH // 2 + border_offset + triangle_width, HEIGHT // 2 - triangle_height),
        (WIDTH // 2 + border_offset + triangle_width, HEIGHT // 2 + triangle_height),
        (WIDTH // 2 + border_offset + triangle_width - 20, HEIGHT // 2)
    ])

def draw_confetti():
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(HEIGHT // 2 - 50, HEIGHT // 2 + 50)
        color = random.choice(CONFETTI_COLORS)
        pygame.draw.circle(screen, color, (x, y), 5)

def draw_button():
    button_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 100, 150, 50)
    pygame.draw.rect(screen, BUTTON_COLOR, button_rect)
    text_surface = button_font.render("START", True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)
    return button_rect

def easing_function(t, b, c, d):
    t /= d / 2
    if t < 1:
        return c / 2 * t * t + b
    t -= 1
    return -c / 2 * (t * (t - 2) - 1) + b

clock = pygame.time.Clock()
center_index = 0
is_spinning = False
spin_count = 0
spin_goal = 0
winning_pick = None
button_rect = None
max_speed = 60  # Max speed for smoother animation
min_speed = 300  # Larger min speed for slower end
total_iterations = 0
speed = min_speed 
offset_y = 0  # This will be used to animate the transition

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and not is_spinning:
            if button_rect and button_rect.collidepoint(event.pos):
                is_spinning = True
                spin_goal = random.randint(120, 210)
                winning_pick = None
                spin_count = 0
                total_iterations = spin_goal
                offset_y = 0

    if is_spinning:
        progress = spin_count / total_iterations
        if total_iterations - spin_count <= 20:
            speed = 35
        if total_iterations - spin_count <= 6:
            speed = 20
        else:
            speed = easing_function(progress, min_speed, max_speed - min_speed, 1)
        
        offset_y += speed / 13  # Slow down the offset movement for a smoother transition
        
        if offset_y >= 80:  # If text has moved one full slot
            center_index = (center_index - 1) % len(unpacked_theme_picks)
            offset_y = 0
            spin_count += 1

        if spin_count >= spin_goal:
            is_spinning = False
            winning_pick = unpacked_theme_picks[center_index]

    draw_wheel(center_index, -offset_y)

    if winning_pick:
        draw_confetti()

    if not is_spinning:
        button_rect = draw_button()

    pygame.display.flip()
    clock.tick(120)  # Higher frame rate for smoother animation
