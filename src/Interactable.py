import pygame
from .Obstacles import _Obstacle
from .Game_Constants import RESIZE_FACTOR

class _Interactable(_Obstacle):
    """
    Base class for interactable objects in the game.
    Inherits from _Obstacle to be visible.
    """
    def __init__(self, start_x, start_y, image, resize_factor=None):
        super().__init__(start_x, start_y, image, resize_factor)
        self.interacted_once = False

    def interact():
        """
        Method to be overridden by subclasses to define interaction behavior.
        """
        pass

    def update():
        """
        Update method for the interactable object.
        Can be overridden by subclasses if needed.
        """
        pass


class Note(_Interactable):
    """
    An interactable object representing a note that the player can read.
    """
    image_path = 'assets/images/note.png' 
    images = [image_path] # Requirement for Asset_Config

    def __init__(self, start_x, start_y, index_image=0):
        super().__init__(start_x, start_y, self.image_path, RESIZE_FACTOR)

        self.note_text_content = [
            "Línea 1: El fantasma blanco es... tímido.",
            "Línea 2: Parece que se asusta cuando le 'hablas'.",
            "~~-.`-.1`.1.-~~",
            "Línea 4: ...pero siempre vuelve."
        ]

        self.original_image = self.image.copy()
        self.is_interacting = False
        self.interaction_duration = 30
        self.interaction_timer = 0

    def interact(self):
        """
        Initiates interaction with the note.
        """

        if self.interacted_once or self.is_interacting:
            return None
        
        self.is_interacting = True
        self.interaction_timer = self.interaction_duration
        return "interaction_started"
    
    
    def read(self):
        """
        Returns the text and autodestroys the note after reading.
        """
        self.interacted_once = True
        self.kill()
        return self.note_text_content
    
    def update(self):
        """
        Controls the flashing effect when the note is being interacted with.
        """
        if not self.is_interacting:
            return None
        
        self.interaction_timer -= 1

        if self.interaction_timer > 0:
            # Flashing effect
            if (self.interaction_timer // 5) % 2 == 0:
                flash_surface = self.original_image.copy()
                flash_surface.fill((255, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
                self.image = flash_surface
            else:
                self.image = self.original_image
        else:
            self.is_interacting = False
            self.image = self.original_image
            return "interaction_finished"
        
        return None
        
