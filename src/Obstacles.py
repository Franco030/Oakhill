import pygame
import random
from .Game_Constants import RESIZE_FACTOR

class _Obstacle(pygame.sprite.Sprite):
    """
    Represents the obstacles of the game (e.g. trees, fences, walls, etc.)
    """
    def __init__(self, start_x, start_y, image=None, resize_factor=None):
        """
        Description: Initializes a generic obstacle
        Parameters:
            start_x: The initial x-coordinate of the obstacle
            start_y: The initial y-coordinate of the obstacle
            image: The file path to the obstacle's image, if None, a red square is used as a placeholder
            resize_factor (optional): A specific resize_factor for this obstacle. Defaults to RESIZE_FACTOR from Game_Constants.py if not provided
        Functionality:
            Loads and scales the obstacle image
            Sets the rect (bounding box) of the obstacle
            Creates a _collision_rect, which is a copy of rect by default, but can be modified by subclasses for more precise collision detection
        """
        super().__init__()

        self.resize_factor = resize_factor if resize_factor is not None else RESIZE_FACTOR
        
        # self.collision_type = "default"

        if not image:
            self.image = pygame.Surface((100, 100)) 
            self.image.fill('red')
        else:    
            self.image = pygame.image.load(image).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.resize_factor, self.image.get_height() * self.resize_factor))
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self._collision_rect = self.rect.copy()
        
    def update(self):
        pass

    @property
    def collision_rect(self):
        """
        Returns the _collision_rect
        By default _collision_rect is equal to rect
        Every custom obstacle is going to have a custom _collision_rect
        """
        return self._collision_rect

    def collides_with(self, other_sprite):
        """
        Returns True if the other_sprite collides with the _collision_rect only
        """
        return self._collision_rect.colliderect(other_sprite.collision_rect)


class Tree(_Obstacle):
    images = ['assets/images/tree_0.png', 'assets/images/tree_1.png', 'assets/images/tree_2.png']
    def __init__(self, start_x, start_y, index_image: int):
        
        if index_image >= len(Tree.images):
            index_image = len(Tree.images) - 1
        super().__init__(start_x, start_y, Tree.images[index_image], 6)

        # --- Modify the self._collision_rect to get a better collision system ---
        trunk_width = self.rect.width // 3

        self._collision_rect = pygame.Rect(
            self.rect.left + trunk_width + 2,
            self.rect.top + 60,
            trunk_width,
            self.rect.height - 60 - 30
        )

class Rock(_Obstacle):
    images = ['assets/images/rock_0.png']
    def __init__(self, start_x, start_y, index_image: int):
        if index_image >= len(Rock.images):
            index_image = len(Rock.images) - 1
        super().__init__(start_x, start_y, Rock.images[index_image])

        # --- Modify the self._collision_rect to get a better collision system ---
        self._collision_rect = self.rect.copy()
        self._collision_rect.top = self._collision_rect.top - 20
        self._collision_rect.height = self._collision_rect.height

class Wall(_Obstacle):
    images = ['assets/images/fence_0.png']
    def __init__(self, start_x, start_y, index_image: int):
        if index_image >= len(Wall.images):
            index_image = len(Wall.images) - 1
        super().__init__(start_x, start_y, Wall.images[index_image])

        # --- Modify the self._collision_rect to get a better collision system ---
        self._collision_rect = self.rect.copy()
        self._collision_rect.top = self._collision_rect.top + 10
        self._collision_rect.height = self._collision_rect.height - 10 - 30

class Deco_Wall(Wall):
    def __init__(self, start_x, start_y, index_image = 0):
        super().__init__(start_x, start_y, index_image)

        # For a decorative wall, the collision rectangle should have no dimension
        self._collision_rect = pygame.Rect(
            self.rect.centerx,
            self.rect.centery,
            0,
            0
        )