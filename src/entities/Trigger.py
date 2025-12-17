import pygame
from src.utils.Game_Enums import Conditions

class Trigger(pygame.sprite.Sprite):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.id = data.get("id")

        self.script = data.get("script") # Name of the script
        self.function = data.get("function") # function of the script to execute

        self.condition = data.get("trigger_condition", Conditions.ON_STAY)
        self.action = data.get("trigger_action", "None")
        self.params = data.get("trigger_params", "")
        
        x = data.get("x", 0)
        y = data.get("y", 0)

        self.is_hidden = data.get("starts_hidden", False)

        self.image = pygame.Surface((64, 64)) 
        self.image.fill((255, 0, 255))
        self.image.set_alpha(0)
        
        offset = data.get("collision_rect_offset", [0, 0, 0, 0])

        base_w, base_h = 64, 64
        
        final_w = base_w + offset[2]
        final_h = base_h + offset[3]
        
        self.rect = pygame.Rect(0, 0, final_w, final_h)
        
        sprite_left = x - (base_w / 2)
        sprite_top = y - (base_h / 2)
        
        self.rect.x = sprite_left + offset[0]
        self.rect.y = sprite_top + offset[1]

        self._apply_persistence()

    @property
    def enabled(self):
        return not self.is_hidden

    @enabled.setter
    def enabled(self, value):
        self.is_hidden = not value
        # NOTE: Hidden triggers don't go into EventManager,
        # so this efectively turns them off/on

    @property
    def script_name(self):
        return self.script

    @script_name.setter
    def script_name(self, value):
        self.script = value

    @property
    def function_name(self):
        return self.function
    
    @function_name.setter
    def function_name(self, value):
        self.function = value

    def hide(self):
        self.is_hidden = True

    def unhide(self):
        self.is_hidden = False

    def update(self):
        pass

    def _apply_persistence(self):
        if not self.id: return
        
        from src.core.GameState import game_state
        prefix = f"OBJ_{self.id}_"
        len_prefix = len(prefix)

        for key, value in game_state.flags.items():
            if key.startswith(prefix):
                prop_name = key[len_prefix:]
                try:
                    setattr(self, prop_name, value)
                except Exception as e:
                    print(f"[Trigger Persistence Error] {self.id}.{prop_name}: {e}")