import seaborn as sns
import matplotlib.pyplot as plt
import pygame
import random
import numpy as np
import pandas as pd
from datetime import datetime
from matplotlib.pyplot import gcf
from openpyxl import load_workbook, styles


def load_theme_data(excel_path):
    df = pd.read_excel(excel_path, header=None)
    headers = df.iloc[0]
    df = df.iloc[1:]
    df.columns = headers
    df = df.loc[:, df.columns.notna()]
    df = df.dropna(axis=0, how='all')

    theme_picks = []
    for name, themes in df.items():
        themes_counts = themes.value_counts()
        person_picks = [(theme, name, count) for (theme, count) in zip(themes_counts.index, themes_counts)]
        theme_picks = theme_picks + person_picks
    # print(theme_picks)

    wb = load_workbook(excel_path, data_only=True)
    sh = wb['Sheetgo_losowanie']
    colors_hex = [cell.fill.start_color.index[2:] for cell in sh[1][:len(df.columns)]]
    colors_in_rgb = [tuple(float(int(h[i:i+2], 16))/255 for i in (0, 2, 4)) for h in colors_hex]
    names_colors = dict(zip(df.columns, colors_in_rgb))
    return theme_picks, names_colors


def create_wheel(wheel_name, theme_data, colors):
    themes, names, data = zip(*theme_data)
    # labels = [theme+"\n"+name for theme,name in zip(themes,names)]
    sns.set_style("dark")
    fig, ax = plt.subplots()
    ax.axis('equal')

    colours = dict(zip(set(names), sns.color_palette("deep", len(set(names)) + 1)))

    wedges, labels = ax.pie(data, labels=themes, radius=1, labeldistance=0.6, rotatelabels=True, startangle=0,
                            counterclock=False, textprops={'fontsize': 9}, colors=[colors[name] for name in names])

    for ea, eb in zip(wedges, labels):
        mang = (ea.theta1 + ea.theta2) / 2.  # get mean_angle of the wedge
        # print(mang, eb.get_rotation())
        eb.set_rotation(mang + 360)  # rotate the label by (mean_angle + 270)
        eb.set_va("center")
        eb.set_ha("center")

    plt.axis('off')
    plt.box(False)
    gcf().patch.set_visible(False)
    # plt.savefig("wheels/" + wheel_name + ".svg", bbox_inches="tight")
    plt.savefig("wheels/" + wheel_name + ".png", bbox_inches="tight", dpi=96 * 3)
    # plt.show()


def get_winner_label(raw_angle, theme_data):
    labels, names, values = zip(*theme_data)
    cumulative = [x / sum(values) for x in np.cumsum(values)]
    angle = raw_angle % 360
    angle_fraction = angle / 360

    for label, name, frac in zip(labels, names, cumulative):
        if angle_fraction <= frac:
            return label.replace(" ", "\n"), name
    return labels[-1].replace(" ", "\n"), names[-1]


def blit_rotate(surf, image, pos, originPos, angle):
    # offset from pivot to center
    image_rect = image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    # roatated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # roatetd image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)

    # draw rectangle around the image
    pygame.draw.rect(surf, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()), 2)


sample_theme_data = [
    ["Piekło mężczyzn", "Lokator", 1],
    ["Sci-fi", "kaja", 2],
    ["Anime", "xero", 3],
    ["Piekło kobiet", "grzeslaw", 1],
    ["Taktyczny scenariusz", "mateo", 3],
    ["Samuraj", "cheetos", 2]
]

excel_file_path = 'spread.xlsx'
theme_data, colors = load_theme_data(excel_file_path)
random.shuffle(theme_data)
wheel_name = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
create_wheel(wheel_name, theme_data, colors)

pygame.init()
pygame.display.set_caption("Filmowe wtorki - koło fortuny")
icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((1000, 1000))
clock = pygame.time.Clock()

image = pygame.image.load('wheels/' + wheel_name + '.png')
triangle = pygame.image.load('triangle.png')
w, h = image.get_size()

angle = 0
done = False
initial_state = True
spin_activated = False
spin_done = False
spin_start_time = False
current_angle = 0
current_velocity = 0
jerk = 6
MIN_VELOCITY = 1
# current_acceleration = 0

speed_up_acceleration = random.uniform(100, 120)
slow_down_acceleration = random.uniform(-40, -30)
max_velocity = random.randrange(1000, 1500)
min_slow_down_acceleration = random.uniform(-6, -3)
current_acceleration = 0
decelerate_phase = False
speed_up_time = random.randrange(1000, 1500)

while not done:
    clock.tick(360)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.MOUSEBUTTONUP:
            if not spin_activated:
                spin_activated = True
                spin_start_time = pygame.time.get_ticks()
                decelerate_phase = False
                spin_done = False
                initial_state = False
            else:
                current_velocity = 0
                current_acceleration = 0
                decelerate_phase = False
                spin_activated = False
                spin_done = True

    pos = (screen.get_width() / 2, screen.get_height() / 2)

    screen.fill((255, 255, 255))

    blit_rotate(screen, image, pos, (w / 2, h / 2), angle)
    if initial_state:
        current_velocity = 20

    if spin_activated:
        time_since_start = pygame.time.get_ticks() - spin_start_time
        if time_since_start < speed_up_time:
            current_acceleration = speed_up_acceleration
        else:
            if not decelerate_phase:
                decelerate_phase = True
                current_acceleration = slow_down_acceleration

            if current_velocity > MIN_VELOCITY:

                current_acceleration += jerk * (clock.get_time() / 1000)
                current_acceleration = min(min_slow_down_acceleration, current_acceleration)
            else:
                current_velocity = 0
                current_acceleration = 0
                decelerate_phase = False
                spin_activated = False
                spin_done = True

        current_velocity += current_acceleration * (clock.get_time() / 100)
        current_velocity = min(max_velocity, current_velocity)
        # print(speed_up_time, current_velocity, current_acceleration)
    angle += current_velocity * (clock.get_time() / 1000)

    scaled_triangle = pygame.transform.scale_by(triangle, 0.2)
    scaled_triangle_rect = scaled_triangle.get_rect(center=pos)
    screen.blit(scaled_triangle, (w - 581, scaled_triangle_rect[1]))

    if spin_done:
        winning_label, winner_name = get_winner_label(angle, theme_data)


        backdrop = pygame.Surface([w, h], pygame.SRCALPHA)
        backdrop.fill((255,255,230,150))
        screen.blit(backdrop, (0,0))

        x_pos, y_pos = pos
        theme_font = pygame.font.SysFont('Comic Sans', 150)
        winner_color =  [int(col*255) for col in colors[winner_name]]
        line_num = 0
        for i, line in enumerate(winning_label.split("\n")):
            text = theme_font.render(line, True, (0, 15, 23))

            text_rect = text.get_rect(center=(x_pos, y_pos - 200 + 130 * i))

            shadow = theme_font.render(line, True, [min(int(col*255 * 2), 255) for col in colors[winner_name]] )
            shadow_rect = shadow.get_rect(center=(x_pos + 5, y_pos - 200 + 5 + 130 * i))

            screen.blit(shadow, shadow_rect)
            screen.blit(text, text_rect)
            line_num = i

        name_font = pygame.font.SysFont('Comic Sans', 100)
        name_text = name_font.render(winner_name, True, (10, 23, 0))
        name_text_rect = name_text.get_rect(center=(x_pos, y_pos - 200 + 130 * (line_num + 1)))
        name_text_shadow = name_font.render(winner_name, True, winner_color)
        name_text_shadow_rect = name_text.get_rect(center=(x_pos, y_pos - 200 + 5 + 130 * (line_num + 1) + 5))

        screen.blit(name_text_shadow, name_text_shadow_rect)
        screen.blit(name_text, name_text_rect)

        # print(winning_label)

    pygame.display.flip()

pygame.quit()
exit()
