"""
Camera stuff
"""
import sys
import csv_reader
from classes import *

pygame.display.set_caption('To The Stars!')
clock = pygame.time.Clock()
background = pygame.transform.smoothscale(pygame.image.load('graphics/background.jpg'), (screen_width, screen_height))
x_position, speed = 0, 1

# Reading csv data
galaxy_stars = csv_reader.read_dataset('stars_dataset/final.csv')
galaxy, stars = galaxy_stars[0], galaxy_stars[1]
ship.current_star = stars[0]
stars.sort(key=lambda x: x.distance)

# Initialize star positions
initialize_star_positions(stars)

# create the music
pygame.mixer.music.load('music/ninja tuna.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# line stuff



def collisions(player_ship: Ship, stars: list[Star]):
    for star in stars:
        if player_ship.rect.colliderect(star.rect):
            player_ship.current_star = star
            sound_effect = pygame.mixer.Sound('music/star ding.mp3')
            sound_effect.play()
            print(player_ship.current_star)

while True:
    # Background scrolling
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        x_position += speed
    elif keys[pygame.K_RIGHT]:
        x_position -= speed
    else:
        pass

    relative_x_pos = x_position % screen_width
    if relative_x_pos > 0:
        relative_x_pos_2 = relative_x_pos - screen_width
    else:
        relative_x_pos_2 = relative_x_pos + screen_width

    screen.blit(background, (relative_x_pos, 0))
    screen.blit(background, (relative_x_pos_2, 0))

    # Blitting all other sprites
    camera_group.custom_draw(ship)
    camera_group.update()

    collisions(ship, stars)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN and event.key == ord('r'):
            galaxy.create_paths()
            stars_in_path = galaxy.radius_path(ship.current_star, set())
            stars_in_path.insert(0, ship.current_star)
            # coordinates = [(star.rect.x, star.rect.y) for star in stars_in_path]
            # pygame.draw.lines(points=coordinates, closed=False, color=(255, 255, 255), surface=screen, width=5)
            line = Line(camera_group, stars_in_path)

    pygame.display.update()
    clock.tick(60)
