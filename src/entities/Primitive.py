import pygame
from .Obstacles import Obstacle


class Primitive(Obstacle):
    """
    A basic object (rectangle) defined via code, not via image.
    Unlike Obstacle, Primitive doesn't use an image, it creates one.
    """
    def __init__(self, data):
        super().__init__(data)

        self.width = int(data.get("width", 50))
        self.height = int(data.get("height", 50))
        self.color = data.get("color", (255, 255, 255))
        self.border_width = data.get("border_width", 0)

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if self.border_width == 0:
            self.image.fill(self.color)
        else:
            pygame.draw.rect(self.image, self.color, (0, 0, self.width, self.height), self.border_width)
        
        self.rect = self.image.get_rect(center=(data.get("x", 0), data.get("y", 0)))

        if self.is_passable:
            self._collision_rect = pygame.Rect(self.rect.centerx, self.rect.centery, 0, 0)
        else:
            offset = data.get("collision_rect_offset", [0, 0, 0, 0])
            self._collision_rect = pygame.Rect(
                self.rect.left + offset[0],
                self.rect.top + offset[1],
                self.rect.width + offset[2],
                self.rect.height + offset[3]
            )

        self._apply_persistence()

    # @property
    # def color(self):
    #     return self._color

    # @color.setter
    # def color(self, value):
    #     self._color = value
    #     self._redraw()

    # @property
    # def size(self):
    #     return pygame.math.Vector2(self.width, self.height)

    # @size.setter
    # def size(self, value):
    #     if hasattr(value, "x"):
    #         self.width, self.height = int(value.x), int(value.y)
    #     elif isinstance(value, (list, tuple)):
    #         self.width, self.height = int(value[0]), int(value[1])
            
    #     self._redraw()
    #     old_center = self.rect.center
    #     self.rect = self.image.get_rect(center=old_center)
    #     self._update_collision_rect()