import pygame
from .Game_Constants import RESIZE_FACTOR
from .Animations import Animation
from .ResourceManager import resource_manager
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
        self.sort_offset_y = int(data.get("sort_offset_y", 0))
        self.is_ground = data.get("is_ground", False)
        self.is_passable = data.get("is_passable", False)
        self.resize_factor = float(data.get("resize_factor", RESIZE_FACTOR))
        self.collision_rect_offset = list(data.get("collision_rect_offset", [0, 0, 0, 0]))
        self.is_hidden = data.get("starts_hidden", False)
        self.interacted_once = False # Obstacles don't interact but it's necessary to use the "is_hidden" property
        # self.used_image = None
        
        # Trigger logic / Events (default values)
        # We have to retrieve it so that the Interactable class has this attributes
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

        self.animation_auto_play = data.get("animation_auto_play", False)
        self.is_animating = self.animation_auto_play

        if animation_paths:
            try:
                images = [resource_path(p) for p in animation_paths]
                if images:
                    self.animation = Animation(self, images, data.get("animation_speed", 0.1))
            except Exception as e:
                print(f"ERROR: Can't load animation for {data.get('id')}: {e}")

    def update(self):
        if self.animation and self.is_animating:
            self.animation.animate()

    def start_animation(self):
        self.is_animating = True

    def stop_animation(self):
        self.is_animating = False
        self.image = self.animation.images[0]
    
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
    
    def modify(self, new_properties):
        if hasattr(self, 'data') and isinstance(self.data, dict):
            for key, value in new_properties.items():
                self.data[key] = value

        for key, value in new_properties.items():
            if key in ["interaction_blocked", "is_passable", "z_index"]:
                setattr(self, key, value)
            
            elif hasattr(self, key):
                setattr(self, key, value)

        if "image_path" in new_properties or "resize_factor" in new_properties:
            img_path = new_properties.get("image_path", getattr(self, "image_path", "None"))
            factor = float(new_properties.get("resize_factor", getattr(self, "resize_factor", 1.0)))
            
            new_img = resource_manager.get_image(img_path)
            if new_img:
                w = int(new_img.get_width() * factor)
                h = int(new_img.get_height() * factor)
                self.image = pygame.transform.scale(new_img, (w, h))
                self.original_image = self.image.copy()
                
                old_center = self.rect.center
                self.rect = self.image.get_rect(center=old_center)
                
                if hasattr(self, 'width'): self.width = w
                if hasattr(self, 'height'): self.height = h
                if hasattr(self, 'data'):
                    self.data['width'] = w
                    self.data['height'] = h

        if "collision_rect_offset" in new_properties or "image_path" in new_properties:
            if hasattr(self, 'collision_rect'):
                offset = new_properties.get("collision_rect_offset", getattr(self, "collision_rect_offset", [0,0,0,0]))
                if isinstance(offset, list) and len(offset) >= 4:
                    self.collision_rect.x = self.rect.x + offset[0]
                    self.collision_rect.y = self.rect.y + offset[1]
                    self.collision_rect.width = self.rect.width + offset[2]
                    self.collision_rect.height = self.rect.height + offset[3]

        if "flash_image_path" in new_properties:
            path = new_properties["flash_image_path"]
            if path in ["None", "", None]:
                self.flash_image = None
            else:
                factor = getattr(self, "resize_factor", 1.0)
                raw_flash = resource_manager.get_image(path)
                if raw_flash:
                     w = int(raw_flash.get_width() * factor)
                     h = int(raw_flash.get_height() * factor)
                     self.flash_image = pygame.transform.scale(raw_flash, (w, h))

        if "charge_sound_path" in new_properties:
            path = new_properties["charge_sound_path"]
            if path in ["None", "", None]:
                self.charge_sound = None
            else:
                try:
                    import os
                    from utils import resource_path
                    full = resource_path(path)
                    if os.path.exists(full):
                        self.charge_sound = pygame.mixer.Sound(full)
                except:
                    self.charge_sound = None
        