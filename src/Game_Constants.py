# This script stores global constants used throughout the game.
from utils import resource_path
import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 800
PLAYER_SPEED = 2
RESIZE_FACTOR = 4
TRANSITION_BIAS = 20
FPS = 60
DEATH_DELAY = 3000
INITIAL_ZONE = (5, 2)
Y_CORD, X_CORD = INITIAL_ZONE

WORLD_MAP_LEVEL = [
        [0, 0, 1, 1, 1, 1], 
        [0, 1, 1, 0, 0, 0], 
        [0, 1, 0, 1, 1, 1], 
        [0, 1, 1, 1, 0, 0],
        [0, 0, 1, 0, 1, 0],
        [0, 1, 1, 1, 0, 0]  
    ]

# (4, 4) is a special room dedicated to a shack in the outside world, it'll be a single room so a Teleport(4, 4, x, y) in the entrance of the shack will be good
# That's why it is not connected to the main "island"

# Resolución (Width x Height) | How many 32px tiles fit?

# 256 x 160                   |          8 x 5
# 512 x 320                   |          16 x 10
# 768 x 480                   |          24 x 15
# 1024 x 640                  |          32 x 20
# 1280 x 800                  |          40 x 25

# Resolución (Width x Height) | How many 16px tiles fit?

# 128 x 80                    |          8 x 5
# 256 x 160                   |          16 x 10
# 384 x 240                   |          24 x 15
# 512 x 320                   |          32 x 20
# 640 x 400                   |          40 x 25
# 768 x 480                   |          48 x 30
# 896 x 560                   |          56 x 35
# 1024 x 640                  |          64 x 40
# 1152 x 720                  |          72 x 45
# 1280 x 800                  |          80 x 50

SCHOOL_MAP_LEVEL = [
    [1, 1, 0, 1, 0],
    [1, 0, 1, 1, 1],
    [1, 0, 1, 1, 1],
    [1, 1, 1, 0, 1],
    [1, 0, 1, 0, 1]
]

BASEMENT_MAP_LEVEL = [
    []
]

MAPS = {
    "forest": WORLD_MAP_LEVEL,
    "school": SCHOOL_MAP_LEVEL
}

LEVEL_MUSIC = {
    "forest": resource_path("assets/music/MAIN_SONG.wav"),
    "school": resource_path("assets/music/INSIDE_SCHOOL.wav")
}

LEVEL_DARKNESS = {
    "forest": False,
    "school": True
}

MUSIC_END_EVENT = pygame.USEREVENT + 1

AMBIENCE_SOUNDS = [

]

# player sprite is 8 x 25
# most resizes must be around 4 times the original size
# player sprite will be 32 x 100
