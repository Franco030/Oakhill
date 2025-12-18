import pygame
from src.utils.Game_Constants import RESIZE_FACTOR
from src.components.Animations import Animation
from src.managers.ResourceManager import resource_manager

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
        self._is_passable = data.get("is_passable", False)
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


        w = int(data.get("width"))
        h = int(data.get("height"))

        image_key = data.get("image_id", data.get("image_path"))
        resize_factor = float(data.get("resize_factor", RESIZE_FACTOR))

        self.image = resource_manager.get_image(image_key)
        if self.image:
            self.image = pygame.transform.scale(self.image, 
                (int(self.image.get_width() * resize_factor), int(self.image.get_height() * resize_factor))
            )
            
        else:
            self.image = pygame.Surface((w, h))
            color = data.get("color", [128, 128, 128])
            self.image.fill(color)

        
        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(center=(data["x"], data["y"]))

        self.is_ground = data.get("is_ground", False)

        if self._is_passable:
            self._collision_rect = pygame.Rect(self.rect.centerx, self.rect.centery, 0, 0)
        else:
            offset = data.get("collision_rect_offset", [0, 0, 0, 0])
            self._collision_rect = pygame.Rect(
                self.rect.left + offset[0],
                self.rect.top + offset[1],
                self.rect.width + offset[2],
                self.rect.height + offset[3]
            )
        
        animation_ids = data.get("animation_images")

        self.animation_auto_play = data.get("animation_auto_play", False)
        self.is_animating = self.animation_auto_play
        self.animation = None
        if animation_ids:
            self.animation = Animation(self, animation_ids, data.get("animation_speed", 0.1))

        self._apply_persistence()

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
    
    @property
    def is_passable(self):
        return self._is_passable

    @is_passable.setter
    def is_passable(self, value):
        self._is_passable = value
        if self._is_passable:
            self._collision_rect = pygame.Rect(self.rect.centerx, self.rect.centery, 0, 0)
        else:
            offset = self.data.get("collision_rect_offset", [0, 0, 0, 0])
            self._collision_rect = pygame.Rect(
                self.rect.left + offset[0],
                self.rect.top + offset[1],
                self.rect.width + offset[2],
                self.rect.height + offset[3]
            )

    def collides_with(self, other_sprite):
        """
        Checks collision with the custom hitbox
        """
        return self._collision_rect.colliderect(other_sprite.collision_rect)
    
    @property
    def x(self):
        return self.rect.centerx

    @x.setter
    def x(self, value):
        self.rect.centerx = int(value)
        
        if self.is_passable:
             self._collision_rect.centerx = self.rect.centerx
        else:
             offset = self.data.get("collision_rect_offset", [0, 0, 0, 0])
             self._collision_rect.x = self.rect.left + offset[0]

    @property
    def y(self):
        return self.rect.centery

    @y.setter
    def y(self, value):
        self.rect.centery = int(value)
        if self.is_passable:
             self._collision_rect.centery = self.rect.centery
        else:
             offset = self.data.get("collision_rect_offset", [0, 0, 0, 0])
             self._collision_rect.y = self.rect.top + offset[1]

    @property
    def visible(self):
        return not self.is_hidden

    @visible.setter
    def visible(self, value):
        self.is_hidden = not value

    @property
    def image_id(self):
        return self.data.get("image_id")

    @image_id.setter
    def image_id(self, new_id):
        new_img = resource_manager.get_image(new_id)
        if new_img:
            self.data["image_id"] = new_id
            w = int(new_img.get_width() * self.resize_factor)
            h = int(new_img.get_height() * self.resize_factor)
            
            self.image = pygame.transform.scale(new_img, (w, h))
            self.original_image = self.image.copy()
            
            old_center = self.rect.center
            self.rect = self.image.get_rect(center=old_center)

    def _apply_persistence(self):
        if not self.id or self.id == "NO_ID": return

        from src.core.GameState import game_state

        prefix = f"OBJ_{self.id}_"
        len_prefix = len(prefix)

        for key, value in game_state.flags.items():
            if key.startswith(prefix):
                prop_name = key[len_prefix:]
                try:
                    setattr(self, prop_name, value)
                except Exception as e:
                    print(f"[Persistence Error] Failed to restore '{prop_name}' in '{self.id}': {e}")