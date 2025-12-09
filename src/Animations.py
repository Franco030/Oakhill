import pygame
from .Game_Constants import RESIZE_FACTOR
from .ResourceManager import resource_manager

class Animation:
    """
    Manages a sequence of images to create an animation effect for a given sprite.
    Uses ResourceManager to fetch images by ID.
    """
    def __init__(self, sprite, image_ids: list, velocity, custom_resize_factor=None):
        """
        Description: Initializes the animation object
        Parameters:
            sprite: The Pygame sprite object to which the animation applies
            image_ids (list): A list of ASSET IDs (strings from assets.json) 
            velocity: The speed of the animation.
            custom_resize_factor: Optional override for global RESIZE_FACTOR
        """
        self.images = []
        self.sprite = sprite
        self.velocity = velocity
        self.index = 0
        
        factor = custom_resize_factor if custom_resize_factor is not None else RESIZE_FACTOR

        raw_images = resource_manager.load_images_from_list(image_ids)
        
        for image in raw_images:
            scaled_image = pygame.transform.scale(
                image, 
                (image.get_width() * factor, image.get_height() * factor)
            )
            self.images.append(scaled_image)

    def animate(self):
        """
        Description: Advances the animation frame
        """
        if not self.images:
            return

        self.index += self.velocity
        if self.index >= len(self.images): 
            self.index = 0
        
        self.sprite.image = self.images[int(self.index)]