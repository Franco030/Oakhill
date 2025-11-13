import pygame
from .Obstacles import _Obstacle
from .Game_Constants import RESIZE_FACTOR
from .Note_Content import ALL_NOTE_TEXTS
from .Lore_Image_Content import ALL_LORE_IMAGES
from utils import resource_path

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


class _NoteHolder(_Interactable):
    """
    Base class for interactable objects that hold notes.
    """
    def __init__(self, start_x, start_y, image_path, flash_image_path, note_content_list, resize_factor=None):
        super().__init__(start_x, start_y, image_path, resize_factor)
        
        self.note_text_content = note_content_list
        self.original_image = self.image.copy()

        try:
            self.flash_image = pygame.image.load(flash_image_path).convert_alpha()
            self.flash_image = pygame.transform.scale(
                self.flash_image, (self.image.get_width(), self.image.get_height())
            )
        except pygame.error:
            print(f"ADVERTENCIA: No se pudo cargar '{flash_image_path}'. Usando destello blanco.")
            self.flash_image = self.original_image.copy()
            self.flash_image.fill((255, 255, 255), special_flags=pygame.BLEND_RGBA_ADD)

        self.is_interacting = False
        self.interaction_duration = 30
        self.interaction_timer = 0

    def interact(self):
        if self.interacted_once or self.is_interacting:
            return None
        self.is_interacting = True
        self.interaction_timer = self.interaction_duration

        return "interaction_started"
    
    def read(self):
        self.interacted_once = True
        self.kill() 
        return self.note_text_content
    
    def update(self):
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
    
class Note(_NoteHolder):
    """
    Una nota estándar que usa el banco de textos.
    """
    image_path = resource_path('assets/images/note.png')
    flash_image_path = resource_path('assets/images/note_flash.png')
    images = [image_path]

    def __init__(self, start_x, start_y, index_image=0):
        if index_image >= len(ALL_NOTE_TEXTS):
            index_image = 0
        note_text = ALL_NOTE_TEXTS[index_image]
        
        super().__init__(start_x, start_y, self.image_path, self.flash_image_path, note_text, RESIZE_FACTOR)
        self._collision_rect = self.rect.inflate(20, 20)


class Scarecrow(_NoteHolder):
    """
    A scarecrow that holds a specific note.
    """
    images = [resource_path("assets/images/scarecrow.png")]
    flash_images = [resource_path('assets/images/scarecrow_flash.png')]

    note_text_content = [
        "El espantapajaros",
        "Sentí una presencia terrible",
        "en la vieja escuela.",
        "Sera K`3`1093`~!@?"
    ]

    def __init__(self, start_x, start_y, index_image=0):
        if index_image >= len(self.images):
            index_image = 0
            

        image_path = self.images[index_image]
        flash_image_path = self.flash_images[index_image]
        
        super().__init__(start_x, start_y, image_path, flash_image_path, self.note_text_content, RESIZE_FACTOR)
        
        trunk_width = self.rect.width // 3
        self._collision_rect = pygame.Rect(
            self.rect.left + trunk_width + 2,
            self.rect.top + 60,
            trunk_width,
            self.rect.height - 60 - 30
        )

class Image(_NoteHolder):
    """
    When interacted shows an image
    """
    image_path = resource_path('assets/images/note.png')
    flash_image_path = resource_path('assets/images/note_flash.png')
    images = [image_path]

    def __init__(self, start_x, start_y, index_image=0):
        if index_image >= len(ALL_LORE_IMAGES):
            index_image = 0
        self.lore_image_path = ALL_LORE_IMAGES[index_image]

        super().__init__(start_x, start_y, self.image_path, self.flash_image_path, None, RESIZE_FACTOR)
        self._collision_rect = self.rect.inflate(20, 20)

    def read(self):
        """
        Overrides "read" to return an image_path
        """
        self.interacted_once = True
        self.kill()
        return self.lore_image_path
        
class Door(_Interactable):
    """
    Teleports the player to another scene when interacted with.
    """

    image_path = resource_path('assets/images/rock_0.png')  # Placeholder image
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