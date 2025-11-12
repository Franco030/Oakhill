import pygame
from .Obstacles import _Obstacle
from .Game_Constants import RESIZE_FACTOR
from .Note_Content import ALL_NOTE_TEXTS

class _Interactable(_Obstacle):
    """
    Base class for interactable objects in the game.
    Inherits from _Obstacle to be visible.
    """
    def __init__(self, start_x, start_y, image, resize_factor=None):
        super().__init__(start_x, start_y, image, resize_factor)
        self.interacted_once = False

    def interact(self):
        """
        Method to be overridden by subclasses to define interaction behavior.
        """
        pass

    def update(self):
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
    flash_image_path = 'assets/images/note_flash.png'
    images = [image_path] # Requirement for Asset_Config

    def __init__(self, start_x, start_y, index_image=0):
        super().__init__(start_x, start_y, self.image_path, RESIZE_FACTOR)


        # Index image is called since JSON already stores it
        # This index corresponds to the note text content NOT the image itself (not ideal, but it works)
        # Maybe we change this, maybe we don't
        if index_image >= len(ALL_NOTE_TEXTS):
            index_image = 0

        self.note_text_content = ALL_NOTE_TEXTS[index_image]

        self.original_image = self.image.copy()
        
        try:
            self.flash_image = pygame.image.load(self.flash_image_path).convert_alpha()
            self.flash_image = pygame.transform.scale(
                self.flash_image, (self.image.get_width(), self.image.get_height())
            )
        except pygame.error:
            print(f"ADVERTENCIA: No se pudo cargar '{self.flash_image_path}'. Usando destello blanco.")
            self.flash_image = self.original_image.copy()
            self.flash_image.fill((255, 255, 255), special_flags=pygame.BLEND_RGBA_ADD)

        self.is_interacting = False
        self.interaction_duration = 60
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
        return self.note_text_content
    
    def update(self):
        """
        Controls the flashing effect when the note is being interacted with.
        """
        if not self.is_interacting:
            return None
        
        self.interaction_timer -= 1

        if self.interaction_timer > 0:
            if (self.interaction_timer // 10) % 2 == 0:
                self.image = self.flash_image
            else:
                self.image = self.original_image
        else:
            self.is_interacting = False
            self.image = self.original_image
            return "interaction_finished"
        
        return None
        
class Door(_Interactable):
    """
    Teleports the player to another scene when interacted with.
    """

    image_path = 'assets/images/rock_0.png'  # Placeholder image
    images = [image_path]  # Requirement for Asset_Config

    def __init__(self, start_x, start_y, target_scene, target_x, target_y, index_image=0):
        super().__init__(start_x, start_y, self.image_path, RESIZE_FACTOR)

        self._collision_rect = self.rect.inflate(10, 10)  # Slightly larger collision area

        self.target_scene = "school_interior"  # Placeholder target scene
        self.target_start_pos = (300, 600) # The player will be teleported here

    def interact(self):
        """
        Returns a command to teleport the player to the target scene and position.
        """

        return None # Placeholder for future implementation