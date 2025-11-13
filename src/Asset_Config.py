import pygame
from .Obstacles import *
from .Interactable import *


# This is the ground truth for obstacle configuration used both in the level editor and in the game
OBSTACLE_CONFIG = {
    'Tree': {
        'class': Tree,
        'indexes': range(len(Tree.images)),
        'key': pygame.K_1,
    },
    'Rock': {
        'class': Rock,
        'indexes': range(len(Rock.images)),
        'key': pygame.K_2,
    },
    'Wall': {
        'class': Wall,
        'indexes': range(len(Wall.images)),
        'key': pygame.K_3,
    },
    'Deco_Wall': {
        'class': Deco_Wall,
        'indexes': range(len(Deco_Wall.images)),
        'key': pygame.K_4
    },
    'Note': {
        'class': Note,
        'indexes': range(len(Note.images)),
        'key': pygame.K_5
    },
    'SchoolBuilding': {
        'class': SchoolBuilding,
        'indexes': range(len(SchoolBuilding.images)),
        'key': pygame.K_6
    },
    'Scarecrow': {
        'class': Scarecrow,
        'indexes': range(len(Scarecrow.images)),
        'key': pygame.K_7,
    },
    'LoreImage': {
        'class': Image,
        'indexes': range(len(Image.images)),
        'key': pygame.K_8,
    }
    # 'Door': {
    #     'class': Door,
    #     'indexes': range(len(Door.images)),
    #     'key': pygame.K_8
    # },
}


# In the future, we may want to have a similar config for enemies
# ENEMY_CONFIG = {}