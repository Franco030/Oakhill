import pygame
from .Game_Constants import RESIZE_FACTOR

class Animation:
    """
    Manages a sequence of images to create an animation effect for a given sprite
    """
    def __init__(self, sprite, images: list, velocity):
        """
        Description: Initializes the animation object
        Parameters:
            sprite: The Pygame sprite object to which the animation applies
            images (list): A list of file paths (strings) to the images that make up the animation frames
            velocity: The speed of the animation. A higher value means faster animation.
        Functionality:
            Loads and scales each image from the provided images list using RESIZE_FACTOR from Game_Constants.py
            Sets the initial animation index to 0
        """
        self.images = []
        self.sprite = sprite
        self.velocity = velocity
        self.index = 0
        for image in images:
            image = pygame.image.load(image).convert_alpha()
            image = pygame.transform.scale(image, (image.get_width() * RESIZE_FACTOR, image.get_height() * RESIZE_FACTOR))
            self.images.append(image)

    def animate(self):
        """
        Description: Advances the animation frame
        Functionality:
            Increments the index by velocity
            Resets index to 0 if it exceeds the number of available images, creating a loop
            Updates the image attribute of the associated sprite to the current animation frame
        """
        self.index = self.index + self.velocity
        if self.index >= len(self.images): 
            self.index = 0
        self.sprite.image = self.images[int(self.index)]