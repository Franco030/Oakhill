import pygame
from .Obstacles import _Obstacle
from .Game_Constants import RESIZE_FACTOR
from utils import resource_path

class _Interactable(_Obstacle):
    """
    Unique class for every interactable object
    Inherits from _Obstacle
    All logic is here and it's setted through the 'data' dictionary in __init__
    """
    def __init__(self, data: dict):
        """
        Initialices the interactable object 
        """
        super().__init__(data) 
        
        self.interaction_type = data.get("interaction_type", "None")
        self.interaction_data = data.get("interaction_data", None)
        
        self.interacted_once = False
        self.is_hidden = data.get("starts_hidden", False)
        
        # self.is_interacting = False
        self.interaction_duration = data.get("interaction_duration", 60)
        self.current_progress = 0
        # self.interaction_timer = 0
        self.original_image = self.image.copy()

        self.charge_sound = None
        self.is_playing_charge = False
        charge_path = data.get("charge_sound_path", "None")

        if charge_path and charge_path != "None":
            try:
                self.charge_sound = pygame.mixer.Sound(resource_path(charge_path))
                self.charge_sound.set_volume(0.7)
            except Exception as e:
                print(f"Error when loading the sound: {e}")

        self.used_image = None
        used_path = data.get("used_image_path", "None")
        
        if used_path and used_path != "None":
            try:
                loaded_used = pygame.image.load(resource_path(used_path)).convert_alpha()
                self.used_image = pygame.transform.scale(
                    loaded_used, 
                    (int(loaded_used.get_width() * self.resize_factor), int(loaded_used.get_height() * self.resize_factor))
                )
            except Exception as e:
                print(f"Error while loading used image: {e}")
        
        flash_path = data.get("flash_image_path")
        try:
            if not flash_path:
                raise pygame.error("No flash image path provided")
                
            self.flash_image = pygame.image.load(resource_path(flash_path)).convert_alpha()
            self.flash_image = pygame.transform.scale(
                self.flash_image, (self.image.get_width(), self.image.get_height())
            )
        except pygame.error as e:
            print("Can't load image, there's no flash")
            self.flash_image = self.original_image.copy()

    def unhide(self):
        """
        Makes the object visibe, therefore, interactable.
        """
        self.is_hidden = False

    def _stop_sound(self):
        if self.charge_sound and self.is_playing_charge:
            self.charge_sound.stop()
            self.is_playing_charge = False

    def progress_interaction(self):
        """
        Called every frame the player holds contact/attack
        """
        if self.is_hidden or self.interacted_once:
            return None
        
        if self.charge_sound and not self.is_playing_charge:
            self.charge_sound.play(-1)
            self.is_playing_charge = True
        
        self.current_progress += 1
        
        if (self.current_progress // 5) % 2 == 0: 
            self.image = self.flash_image
        else:
            self.image = self.original_image
            
        if self.current_progress >= self.interaction_duration:
            self.image = self.original_image
            self._stop_sound()
            return "finished"
            
        return "progressing"

    def reset_interaction(self):
        """
        Called when the player stops interacting and did not finish
        """
        self._stop_sound()
        if self.current_progress > 0 and not self.interacted_once:
            self.current_progress = 0
            self.image = self.original_image

    def interact(self):
        """
        Starts the interaction
        """
        if self.is_hidden:
            return None
        
        if self.interacted_once or self.is_interacting:
            return None
        
        self.is_interacting = True
        self.interaction_timer = self.interaction_duration
        return "interaction_started"
    
    def read(self):
        """
        Finishes the interaction, auto-destroys (from the sprites group)
        and returns the data of the interaction
        """
        self.interacted_once=True
        if self.used_image:
            self.image = self.used_image
            self.original_image = self.used_image
        else:
            self.kill()
        
        return self.interaction_data
    
    def update(self):
        """
        Updates the state of the object every frame (for animation purposes)
        """
        super().update() 
        
        # if not self.is_interacting:
        #     return None

        # self.interaction_timer -= 1
        # if self.interaction_timer > 0:
        #     if (self.interaction_timer // 10) % 2 == 0: 
        #         self.image = self.flash_image
        #     else:
        #         self.image = self.original_image
        # else:
        #     self.is_interacting = False
        #     self.image = self.original_image
        #     return "interaction_finished"
        
        # return None