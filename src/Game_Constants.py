# This script stores global constants used throughout the game.

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 780
PLAYER_SPEED = 4
RESIZE_FACTOR = 4
TRANSITION_BIAS = 20
FPS = 60
DEATH_DELAY = 3000
INITIAL_ZONE = (5, 2)

WORLD_MAP_LEVEL = [
        [0, 0, 1, 1, 1, 1], 
        [0, 1, 1, 0, 0, 0], 
        [0, 1, 0, 0, 0, 0], 
        [0, 1, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0]  
    ]



# player sprite is 8 x 25
# most resizes must be around 4 times the original size
# player sprite will be 32 x 100
