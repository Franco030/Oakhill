import pygame
from .Obstacles import _Obstacle

class Mirror(_Obstacle):
    """
    A special obstacle that reflects the player
    Requires a png transparent or semitransparent
    """

    def __init__(self, data, player):
        super().__init__(data)

        self.player = player

        self.clean_image = self.image.copy()

        self.reflection_offset_y = int(data.get("reflection_offset_y", 0))

    def update(self):
        self.image = self.clean_image.copy()
        
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery

        if dy < 0 or dy > 800: 
            return

        prefix = ""
        if getattr(self.player, 'is_attacking', False):
            prefix = "attack_"
        
        current_facing = self.player.facing
        target_facing = current_facing 

        if current_facing == "down": target_facing = "up"
        elif current_facing == "up": target_facing = "down"
        elif current_facing == "left": target_facing = "right"
        elif current_facing == "right": target_facing = "left"

        current_key = f"{prefix}{current_facing}"
        target_key = f"{prefix}{target_facing}"

        player_sprite = self.player.image
        should_flip = True 

        if hasattr(self.player, "animations"):
            found_frame = False
            frame_index = 0
            
            try:
                if current_key in self.player.animations:
                    current_anim = self.player.animations[current_key]
                    frame_index = current_anim.images.index(self.player.image)
                    found_frame = True
            except ValueError:
                pass


            if not found_frame:
                for key, anim in self.player.animations.items():
                    if self.player.image in anim.images:
                        frame_index = anim.images.index(self.player.image)
                        found_frame = True
                        break
            
            if found_frame and target_key in self.player.animations:
                target_anim = self.player.animations[target_key]
                player_sprite = target_anim.images[frame_index % len(target_anim.images)]
                
 
                if current_facing in ["up", "down"]:
                    should_flip = False 

        if should_flip:
            reflection_sprite = pygame.transform.flip(player_sprite, True, False)
        else:
            reflection_sprite = player_sprite.copy()
            
        reflection_sprite.set_alpha(150)

        local_x = (self.rect.width // 2) + dx - (player_sprite.get_width() // 2)
        local_y = (self.rect.height // 2) - dy - (player_sprite.get_height() // 2) + self.reflection_offset_y

        # if self.haunted_image:
        #     ghost_sprite = self.haunted_image.copy()
        #     ghost_sprite.set_alpha(150)
        #     g_x = local_x + (reflection_sprite.get_width() - ghost_sprite.get_width()) // 2
        #     g_y = local_y + (reflection_sprite.get_height() - ghost_sprite.get_height()) // 2 - 20
        #     self.image.blit(ghost_sprite, (g_x, g_y))

        self.image.blit(reflection_sprite, (local_x, local_y))