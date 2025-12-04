import pygame
from .Game_Constants import RESIZE_FACTOR
from .Animations import Animation
from utils import resource_path

class Obstacle(pygame.sprite.Sprite):
    """
    Unique class for every static obstacles (can't interact with them)
    All settings are loaded through the dictionary 'data' in __init__
    """
    def __init__(self, data: dict):
        """
        Initialized the obstacles throught the JSON dict
        """
        super().__init__()

        self.data = data
        
        # Identity
        self.id = data.get("id", "NO_ID")
        self.type = data.get("type", "Obstacle")
        
        # Properties physics/render
        self.z_index = int(data.get("z_index", 0))
        self.is_ground = data.get("is_ground", False)
        self.is_passable = data.get("is_passable", False)
        self.resize_factor = float(data.get("resize_factor", RESIZE_FACTOR))
        self.is_hidden = data.get("starts_hidden", False)
        self.interacted_once = False # Obstacles don't interact but it's necessary to use the "is_hidden" property
        # self.used_image = None
        
        # Trigger logic / Events (default values)
        self.trigger_condition = data.get("trigger_condition", "None")
        self.trigger_action = data.get("trigger_action", "None")
        self.trigger_params = data.get("trigger_params", "")

        image_path = data.get("image_path")
        resize_factor = data.get("resize_factor", RESIZE_FACTOR)

        try:
            if not image_path or image_path == "None":
                raise ValueError("Image path is none or is empty")
                
            self.image = pygame.image.load(resource_path(image_path)).convert_alpha()
            
            self.image = pygame.transform.scale(self.image, 
                (int(self.image.get_width() * resize_factor), int(self.image.get_height() * resize_factor))
            )
            
        except Exception as e:
            self.image = pygame.Surface((int(20 * resize_factor), int(20 * resize_factor)))
            self.image.fill((255, 0, 255))
            self.image.set_alpha(150) 
        

        self.is_ground = data.get("is_ground", False)
        
        self.rect = self.image.get_rect(center=(data["x"], data["y"]))


        if data.get("is_passable", False):

            self._collision_rect = pygame.Rect(self.rect.centerx, self.rect.centery, 0, 0)
        else:
            offset = data.get("collision_rect_offset", [0, 0, 0, 0])
            self._collision_rect = pygame.Rect(
                self.rect.left + offset[0],
                self.rect.top + offset[1],
                self.rect.width + offset[2],
                self.rect.height + offset[3]
            )
        
        self.animation = None
        animation_paths = data.get("animation_images")
        if animation_paths:
            try:
                images = [resource_path(p) for p in animation_paths]
                if images:
                    self.animation = Animation(self, images, data.get("animation_speed", 0.1))
            except Exception as e:
                print(f"ERROR: Can't load animation for {data.get('id')}: {e}")

    def update(self):
        """
        This method is called for the sprites group in main_window
        IMPORTANT for animations
        """
        if self.animation:
            self.animation.animate()
    
    def unhide(self):
        """
        "Allows action manager to reveal this object
        """
        self.is_hidden = False

    def hide(self):
        self.is_hidden = True

    @property
    def collision_rect(self):
        """
        Returns the custom hitbox
        """
        return self._collision_rect

    def collides_with(self, other_sprite):
        """
        Checks collision with the custom hitbox
        """
        return self._collision_rect.colliderect(other_sprite.collision_rect)