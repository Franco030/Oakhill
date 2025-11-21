# This script stores global constants used throughout the game.
from utils import resource_path

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 780
PLAYER_SPEED = 4
RESIZE_FACTOR = 4
TRANSITION_BIAS = 20
FPS = 60
DEATH_DELAY = 3000
INITIAL_ZONE = (5, 2)
Y_CORD, X_CORD = INITIAL_ZONE

WORLD_MAP_LEVEL = [
        [0, 0, 1, 1, 1, 1], 
        [0, 1, 1, 0, 0, 0], 
        [0, 1, 0, 0, 0, 0], 
        [0, 1, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0]  
    ]

# Initial location for level_editor purposes will be (4, 2)
SCHOOL_MAP_LEVEL = [
    [0, 1, 0, 0, 0],
    [1, 1, 1, 0, 1],
    [0, 0, 1, 1, 1],
    [1, 1, 1, 0, 1],
    [1, 0, 1, 0, 1]
]

MAPS = {
    "forest": WORLD_MAP_LEVEL,
    "school": SCHOOL_MAP_LEVEL
}

LEVEL_MUSIC = {
    "forest": resource_path("assets/sounds/background_sound.wav"),
    "school": resource_path("assets/sounds/inside_schoolbuilding_loop.wav")
}

LEVEL_DARKNESS = {
    "forest": False,
    "school": True
}

# player sprite is 8 x 25
# most resizes must be around 4 times the original size
# player sprite will be 32 x 100


# Every inside wall has a border of 16 x 5 pixels
# And we simulate a wall with 16 x 11 pixels
# This means if we use Grid 16 x 16 it'll be:
#   -
#   | 5 squares
#   -
#   |   11 squares
#   |
#   - 
#