import pygame
from src.Game_Constants import RESIZE_FACTOR, SCREEN_WIDTH, SCREEN_HEIGHT, TRANSITION_BIAS
from src.Behaviour import *
from src.Animations import Animation
from utils import resource_path

class _Enemy(pygame.sprite.Sprite):
    """
    Represents the base _Enemy class, which serves as a blueprint for all enemy types in the game
    Parameters:
        start_x: The initial x-coordinate of the enemy
        start_y: The initial y-coordinate of the enemy
        image: The file path to the enemy's image.
        health: The amount of health the enemy has.
        behaviour: How will the enemy behave?
        resize_factor (optional): A specific resize_factor for this enemy. Defaults to RESIZE_FACTOR from Game_Constants.py if not provided.
    """
    def __init__(self, start_x, start_y, image, health, behaviours, resize_factor = None):
        super().__init__()

        self.resize_factor = resize_factor if resize_factor is not None else RESIZE_FACTOR

        self.x = start_x
        self.y = start_y

        self.health = health

        self.y_offset = 0
        self.x_offset = 0
        
        self.behaviours = behaviours

        self.image = pygame.image.load(image).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * self.resize_factor, self.image.get_height() * self.resize_factor))
        self.original_image_path = image
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(center=(start_x, start_y))
        self._collision_rect = self.rect.copy() # Default collision_rect adjust in sub_classes

        # Flashing properties
        self.is_flashing = False
        self.flash_duration = 500
        self.flash_timer = 0
        self.flash_color = (255, 255, 255)



    @property
    def current_y(self):
        return self.y + self.y_offset
    
    @property
    def current_x(self):
        return self.x + self.x_offset
    
    @property
    def collision_rect(self):
        return self._collision_rect
    
    def collides_with(self, other_sprite):
        """
        Returns True if the other_sprite collides with the _collision_rect only
        """
        return self._collision_rect.colliderect(other_sprite.collision_rect)
    
    def start_flash(self):
        self.is_flashing = True
        self.flash_timer = self.flash_duration

    def while_attacked(self):
        pass

    def reset_state(self):
        if hasattr(self.behaviours, "reset"):
            self.behaviours.reset()

        # We don't need this now, we may need it later
        # self.is_flashing = False
        # self.image = self.original_image

    def update_behaviour(self, behaviour):
        self.behaviours.append(behaviour)

    def update(self, delta_time):
        """
        Updates the enemy's state by applying all its registered behaviours
        This method will tipically be called once per frame
        """
        # for behaviour in self.behaviours:
        self.behaviours.apply(self, delta_time)
        self.rect.centerx = self.x + self.x_offset
        self.rect.centery = self.y + self.y_offset
        self._collision_rect.centerx = self.x + self.x_offset
        self._collision_rect.centery = self.y + self.y_offset

        if self.is_flashing:
            self.flash_timer -= delta_time
            if self.flash_timer > 0:
                if (self.flash_timer // 50) % 2 == 0:
                    flash_surface = self.original_image.copy()
                    flash_surface.fill(self.flash_color, special_flags=pygame.BLEND_RGBA_MULT)
                    self.image = flash_surface
                else:
                    self.image = self.original_image
            else:
                self.is_flashing = False
                self.image = self.original_image

        if self.health < 0:
            self.kill()

class Red_Ghost(_Enemy):
    
    def __init__(self, start_x, start_y, health, behaviours):
        super().__init__(start_x, start_y, resource_path("assets/images/enemy.png"), health, behaviours, 5)

        # --- Modify the self._collision_rect to get a better collision system ---
        self._collision_rect = pygame.Rect(
            self.rect.left,
            self.rect.top,
            self.rect.width - 50,
            self.rect.height - 50
        )
        self.animation = Animation(self, [resource_path(f"assets/animations/Red_Ghost/red_ghost_{i}.png") for i in range (1, 5)], 0.07)

    def while_attacked(self, amount):
        self.health -= amount
        self.start_flash()

    def update(self, delta_time):
        """
        We override the update method so that we can add custom animations
        Conditionally apply behaviours
        Apply extra logic
        """
        if self.rect.left > SCREEN_WIDTH + (TRANSITION_BIAS*2) or self.rect.right < 0 - (TRANSITION_BIAS*2):
            self.behaviours.reverse()

        self.animation.animate()
        
        super().update(delta_time)

class Stalker_Ghost(_Enemy):
    def __init__(self, start_x, start_y, health, behaviours):
        # We changed the sprite for another one
        # super().__init__(start_x, start_y, resource_path("assets/images/ghost.png"), health, behaviours, 5)
        super().__init__(start_x, start_y, resource_path("assets/animations/Stalker/stalker_0.png"), health, behaviours, 3)
        # --- Modify the self._collision_rect to get a better collision system ---
        self._collision_rect = pygame.Rect(
            self.rect.left,
            self.rect.top,
            self.rect.width - 30,
            self.rect.height - 20
        )

        self.animation = Animation(self, [resource_path(f"assets/animations/Stalker/stalker_{i}.png") for i in range (0, 4)], 0.10)

    def while_attacked(self):
        if self.is_flashing:
            return
        
        self.start_flash()
        self.behaviours.shoo(self)


    def update(self, delta_time):
        """
        We override the update method so that we can add custom animations
        """
        super().update(delta_time)
        self.animation.animate()