"""
Contains all the classes used in the program.
"""
from __future__ import annotations
import pygame
import random

pygame.init()
screen_width, screen_height = 800, 400
screen = pygame.display.set_mode((screen_width, screen_height))


class CameraGroup(pygame.sprite.Group):
    """Moves all sprites' positions relative to the current position of the ship."""
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        # camera offset
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

        # box setup
        self.camera_borders = {'left': 500, 'right': 500, 'top': 0, 'bottom': 0}
        l, t = self.camera_borders['left'], self.camera_borders['top']
        w = self.display_surface.get_size()[0] - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.display_surface.get_size()[1] - (self.camera_borders['top'] + self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(l, t, w, h)

    def center_target_camera(self, target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def box_target_camera(self, target):
        if target.rect.left < self.camera_rect.left:
            self.camera_rect.left = target.rect.left
        if target.rect.right > self.camera_rect.right:
            self.camera_rect.right = target.rect.right
        if target.rect.top < self.camera_rect.top:
            self.camera_rect.top = target.rect.top
        if target.rect.bottom > self.camera_rect.bottom:
            self.camera_rect.bottom = target.rect.bottom

        self.offset.x = self.camera_rect.left - self.camera_borders['left']
        self.offset.y = self.camera_rect.top - self.camera_borders['top']

    def custom_draw(self, player):
        # self.center_target_camera(player)
        self.box_target_camera(player)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)


class Line(pygame.sprite.Sprite):
    """Draws lines and stuff"""
    def __init__(self, group: CameraGroup, stars_in_path: list[Star]):
        super().__init__(group)
        # coordinates = [(star.rect.x, star.rect.y) for star in stars_in_path]
        # self.image = pygame.draw.lines(points=coordinates, closed=False, color=(255, 255, 255), surface=screen)
        # self.rect = self.image
        self.rect = pygame.rect.


class Star(pygame.sprite.Sprite):
    """A representation of an individual star.

    This is analogus to the node data class for the graph AST that we learned in
    lecture.

    Instance Attributes:
        - name: the name of the star
        - distance: the distance between Earth and the star
        - mass: the mass of the star
        - radius: the radius of the star
        - pin: A bool value that corresponds to if the star is pinned by the user or not. True means that the star
         is pinned, while False means that the star is not pinned.

        Representation Invariants:
        - self.name !== ''
        - self.distance > 0
        - self.mass > 0
    """
    def __init__(self, group: CameraGroup, name: str, distance: float, mass: float, radius: float):
        super().__init__(group)
        image = pygame.image.load('graphics/Star.png')
        image = pygame.transform.scale(image, (50, 50))
        image = pygame.transform.rotate(image, 270)
        self.image = image.convert_alpha()
        # Note: self.rect is initalized outside of __init__

        # Actual star attributes
        self.name = name
        self.distance = distance
        self.mass = mass
        self.radius = radius
        self.closest_stars = {}
        self.rect = None


class Path:
    """A class that represents the paths between stars.
    """
    endpoints: tuple[Star, Star]

    def __init__(self, star1: Star, star2: Star) -> None:
        self.endpoints = star1, star2
        star1.closest_stars[star2.name] = self
        star2.closest_stars[star1.name] = self

    def get_other_endpoint(self, star: Star) -> Star:
        if self.endpoints[0] == star:
            return self.endpoints[1]
        else:
            return self.endpoints[0]


class Ship(pygame.sprite.Sprite):
    """Representation of the user and their current position within the galaxy

    Instance Attributes:
        - source: The current star that the ship is at
        - destination: the name of the star where the user wants to go
        - next_stop: the next star that the ship will go to

    Representation Invariants:
        - self.source != ''
        - self.destination
        - self.source != self.destination
    """
    def __init__(self, pos, group):
        super().__init__(group)
        image = pygame.image.load('graphics/Ship.png')
        image = pygame.transform.scale(image, (50, 50))
        image = pygame.transform.rotate(image, 270)
        self.image = image.convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.visited = set()
        self.current_star = None

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def update(self):
        self.input()
        self.rect.center += self.direction * self.speed


class Galaxy:
    """An abstract class for a network of stars.

    Private Instance Attributes:
        - _stars: A mapping from star name to Star in this network.

    Representation Invariants:
        - self._stars != {}
    """
    _stars: dict[str, Star]

    def __init__(self, *sprites) -> None:
        """Initialize an empty Galaxy."""
        super().__init__(*sprites)
        self._stars = {}

    def add_star(self, name: str, distance: float, mass: float, radius: float) -> Star:

        """Add a new star to this galaxy and return it.

        Preconditions:
            - star_name not in self._stars
        """
        # initalize a new star with the given attributes
        new_star = Star(camera_group, name, distance, mass, radius)

        # add the star to the galaxy's collection of stars
        self._stars[new_star.name] = new_star

        return new_star

    def create_paths(self) -> None:
        """Create the paths between all the stars (i.e., with their two closest neighbour stars
        """
        # create a new list of all the stars, and order it in ascending order from their distance
        ordered_stars = [self._stars[star] for star in self._stars]
        ordered_stars.sort(key=lambda x: x.distance)

        # connect the stars, except the last ad second last stars
        for i in range(0, len(ordered_stars) - 2):
            Path(ordered_stars[i], ordered_stars[i + 1])
            Path(ordered_stars[i], ordered_stars[i + 2])

        # connec the last and second last star
        Path(ordered_stars[len(ordered_stars) - 1], ordered_stars[len(ordered_stars) - 2])

    def radius_path(self, starting_star: Star, visited: set[Star]) -> list[Star]:
        """Return a list of the stars in the galaxy, filtered by their luminosity.
        """
        visited.add(starting_star)

        # get a list of the closest stars
        closest_stars = [starting_star.closest_stars[star].get_other_endpoint(starting_star) for star in
                         starting_star.closest_stars]

        # create a mapping of the radii of the closest stars to its star if the star isn't in visited
        radii = {star.radius: star for star in closest_stars if star not in visited}

        # the base case: all the stars are in visited
        if len(radii) == 0:
            return []

        else:
            stars_so_far = []
            lowest_radius_star = radii[min(radii)]
            stars_so_far.append(lowest_radius_star)
            stars_so_far.extend(self.radius_path(lowest_radius_star, visited))

        return stars_so_far


def pin_star(self, ship) -> Star:
    """Pin the star that the ship is currently at (ie., the star with the same address
    as the ship's source attribute), and then return it.

    Preconditions:
        -
    """
    current_star = None
    # find the star that the ship is currently at
    for star in self._stars:
        if star == ship.source:
            current_star = self._stars[star]

    # pin the star
    current_star.pin = True

    return current_star


def initialize_star_positions(stars: list[Star]) -> None:
    """Initalizes star.rect for star in stars"""
    increasing_inverval = screen_width // 10
    new_x = 0

    for star in stars:
        new_x += increasing_inverval
        star.rect = star.image.get_rect(topleft=(new_x, random.randrange(0, 350)))
        new_x += increasing_inverval


camera_group = CameraGroup()
ship = Ship((50, 200), camera_group)
