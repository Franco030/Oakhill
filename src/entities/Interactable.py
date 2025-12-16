import pygame
from .Obstacles import Obstacle
from src.core.GameState import game_state
from src.managers.ResourceManager import resource_manager
from src.utils.utils import resource_path

class Interactable(Obstacle):
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

        self.script = data.get("script")
        self.function = data.get("function")
        
        self.interacted_once = False
        self.is_hidden = data.get("starts_hidden", False)
        
        self.interaction_duration = data.get("interaction_duration", 120)
        self.interaction_blocked = data.get("interaction_blocked", False)
        self.current_progress = 0
        self.original_image = self.image.copy()

        self.charge_sound = None
        self.is_playing_charge = False

        charge_key = data.get("charge_sound_id", data.get("charge_sound_path", "None"))

        if charge_key and charge_key != "None":
            self.charge_sound = resource_manager.get_sound(charge_key)
            if self.charge_sound:
                self.charge_sound.set_volume(0.85)

        self.used_image = None
        used_key = data.get("used_image_id", data.get("used_image_path", "None"))

        if used_key and used_key != "None":
            raw_used = resource_manager.get_image(used_key)
            if raw_used:
                self.used_image = pygame.transform.scale(
                    raw_used, 
                    (int(raw_used.get_width() * self.resize_factor), int(raw_used.get_height() * self.resize_factor))
                )
        

        flash_key = data.get("flash_image_id", data.get("flash_image_path"))
        raw_flash = resource_manager.get_image(flash_key)

        if raw_flash:
            self.flash_image = pygame.transform.scale(
                raw_flash, (self.image.get_width(), self.image.get_height())
            )
        else:
            self.flash_image = self.original_image.copy()

        if game_state.has_interacted(self.id):
            self.interacted_once = True
            if self.used_image:
                self.image = self.used_image
                self.original_image = self.used_image

    @property
    def blocked(self):
        return self.interaction_blocked

    @blocked.setter
    def blocked(self, value):
        self.interaction_blocked = value
        
    @property
    def script_name(self):
        return self.script

    @script_name.setter
    def script_name(self, value):
        self.script = value

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
        game_state.register_interaction(self.id)
        if self.used_image:
            self.image = self.used_image
            self.original_image = self.used_image
        else:
            self.kill()
        
    
    def update(self):
        """
        Updates the state of the object every frame (for animation purposes)
        """
        super().update() 
        