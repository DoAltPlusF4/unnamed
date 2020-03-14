"""Contains class objects for Room."""

import random
from itertools import product

from pyglet import image
from pyglet.sprite import Sprite

from . import getBitValue, getUV, prefabs, tilesets


class Room:
    """Room class for dungeon."""

    def __init__(self, window, room_type=0, doors={0: True, 1: True, 2: True, 3: True}, tileset=tilesets.basic()):  # noqa: E501
        """Initialise the Room class."""
        self.type = room_type
        self.doors = doors
        self.ground_tiles = {}
        self.tiles = {}
        self.cleared = room_type == 0

        border_image = image.load("resources/border.png")
        border_image.anchor_x = border_image.width // 2
        border_image.anchor_y = border_image.height // 2

        border_x, border_y = window.worldToScreen(7.5, 7.5)
        self.border = Sprite(
            border_image,
            x=border_x, y=border_y,
            batch=window.BATCH,
            group=window.UI_LAYERS[0]
        )
        self.border.scale = window.scaleFactor()

        types = {
            0: tilesets.startRoom(),
            1: tileset,
            2: tilesets.treasureRoom(),
            3: tilesets.bossRoom(),
            4: tilesets.basic()
        }

        self.ground_tiles = types[room_type]

        self.createSprites(window)

    def __str__(self):
        string = ""
        for y in range(15):
            for x in range(15):
                y = 14 - y
                string += f"{self.ground_tiles[(x, y)]} "
            string += "\n"
        return string

    def createSprites(self, window):
        """Creates all the tile sprites."""
        style = 0
        room_tiles = self.ground_tiles
        borders = {
            (-1, -1): 2,
            (-1, 15): 8,
            (15, -1): 128,
            (15, 15): 32,
            (-1, None): 14,
            (15, None): 224,
            (None, -1): 131,
            (None, 15): 56
        }
        doors = self.doors
        if doors[0]:
            door_tiles = {
                (5, 17): 14, (6, 17): 0, (7, 17): 0, (8, 17): 0, (9, 17): 224,
                (5, 16): 14, (6, 16): 0, (7, 16): 0, (8, 16): 0, (9, 16): 224,
                (5, 15): 62, (6, 15): 0, (7, 15): 0, (8, 15): 0, (9, 15): 248,
            }
            borders.update(door_tiles)
        if doors[1]:
            door_tiles = {
                (15, 9): 248, (16, 9): 56, (17, 9): 56,
                (15, 8): 0, (16, 8): 0, (17, 8): 0,
                (15, 7): 0, (16, 7): 0, (17, 7): 0,
                (15, 6): 0, (16, 6): 0, (17, 6): 0,
                (15, 5): 227, (16, 5): 131, (17, 5): 131,
            }
            borders.update(door_tiles)
        if doors[2]:
            door_tiles = {
                (5, -1): 143, (6, -1): 0, (7, -1): 0, (8, -1): 0, (9, -1): 227,
                (5, -2): 14, (6, -2): 0, (7, -2): 0, (8, -2): 0, (9, -2): 224,
                (5, -3): 14, (6, -3): 0, (7, -3): 0, (8, -3): 0, (9, -3): 224,
            }
            borders.update(door_tiles)
        if doors[3]:
            door_tiles = {
                (-3, 9): 56, (-2, 9): 56, (-1, 9): 62,
                (-3, 8): 0, (-2, 8): 0, (-1, 8): 0,
                (-3, 7): 0, (-2, 7): 0, (-1, 7): 0,
                (-3, 6): 0, (-2, 6): 0, (-1, 6): 0,
                (-3, 5): 131, (-2, 5): 131, (-1, 5): 143,
            }
            borders.update(door_tiles)

        for x, y in product(range(-3, 18), repeat=2):
            if (x, y) in borders.keys() and borders[(x, y)] > 0:
                value = borders[(x, y)]
                tile_type = 1
            elif (x, y) in borders.keys() and borders[(x, y)] == 0:
                value = random.randint(0, 9)
                tile_type = 0
            elif (x, None) in borders.keys() and -1 <= y and y <= 15:
                value = borders[(x, None)]
                tile_type = 1
            elif (None, y) in borders.keys() and -1 <= x and x <= 15:
                value = borders[(None, y)]
                tile_type = 1
            elif (x, y) in room_tiles.keys():
                tile_type = room_tiles[(x, y)]
                if tile_type == 0:
                    value = random.randint(0, 9)
                else:
                    value = getBitValue(room_tiles, x, y)
            else:
                continue

            image_path = f"resources/tilesets/{style}/{tile_type}.png"
            tile_image = image.load(image_path)
            tile_image.anchor_x = 0
            tile_image.anchor_y = 0

            tile_region = tile_image.get_region(
                *getUV(tile_type, value)
            )

            tile = prefabs.Tile(
                window,
                x, y,
                tile_type,
                tile_region
            )
            self.tiles[(x, y)] = tile

    def update(self, window):
        border_x, border_y = window.worldToScreen(7.5, 7.5, True)
        self.border.update(
            x=border_x,
            y=border_y
        )
        for x, y in product(range(-3, 18), repeat=2):
            if (x, y) in self.tiles.keys():
                self.tiles[(x, y)].update(window)

    def resize(self, window):
        border_x, border_y = window.worldToScreen(7.5, 7.5, True)
        self.border.update(
            x=border_x,
            y=border_y
        )
        self.border.scale = window.scaleFactor()
        for x, y in product(range(-3, 18), repeat=2):
            if (x, y) in self.tiles.keys():
                self.tiles[(x, y)].resize(window)


class Dungeon:
    """Dungeon class, contains rooms."""

    def __init__(self, window):
        self.rooms = {}
        self.style = 0

        self.rooms[(0, 0)] = Room(window)
