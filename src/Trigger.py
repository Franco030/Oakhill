import pygame

class Trigger(pygame.sprite.Sprite):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.id = data.get("id")
        self.condition = data.get("trigger_condition", "OnEnter")
        self.action = data.get("trigger_action", "None")
        self.params = data.get("trigger_params", "")
        
        x = data.get("x", 0)
        y = data.get("y", 0)
        

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

    def update(self):
        pass