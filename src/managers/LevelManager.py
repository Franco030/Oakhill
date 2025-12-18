import pygame
from src.scenes.Scene_Loader import SceneLoader
from .ResourceManager import resource_manager
from .TweenManager import tween_manager
from src.utils.Game_Constants import MAPS, LEVEL_MUSIC, LEVEL_DARKNESS, SCREEN_WIDTH, SCREEN_HEIGHT, TRANSITION_BIAS, MUSIC_END_EVENT
from src.utils.utils import resource_path
from src.utils.Game_Enums import Colors
import random

class LevelManager:
    def __init__(self, retro_effects):
        self.retro_effects = retro_effects

        self.ambience_ids = [
            key for key in resource_manager.asset_map.keys() 
            if key.startswith("amb_")
        ]
        print(f"{Colors.BRIGHT_CYAN}[LevelManager]{Colors.RESET} Detected {len(self.ambience_ids)} ambience tracks IDs.")

        self.current_scene = None
        self.current_music_path = None

        self.silence_timer = 0
        self.is_in_silence = False

        self.ambience_timer = 0

        self.current_zone = (0, 0)

        self.light_mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.light_radius = 250
        self.flashlight_texture = self._generate_flashlight_texture()

    def _generate_flashlight_texture(self):
        texture = pygame.Surface((self.light_radius * 2, self.light_radius * 2))
        for r in range(self.light_radius, 0, -2):
            intensity = int(255 * (1 - (r / self.light_radius)))
            pygame.draw.circle(texture, (intensity, intensity, intensity), (self.light_radius, self.light_radius), r)
        return texture
    
    def reset_music_state(self):
        self.current_music_path = None
        pygame.mixer.music.stop()
        self.silence_timer = 0
        self.is_in_silence = False
        self.ambience_timer = 0

    def load_level_from_request(self, level_req, player_sprite):
        if self.current_scene:
            self.current_scene.cleanup()

        json_path = level_req.get("json_path")
        map_matrix = level_req.get("map_matrix")
        entry_zone = level_req.get("entry_zone")
        player_pos = level_req.get("player_pos")
        music_path = level_req.get("music_path")
        darkness = level_req.get("darkness", False)

        chase_snd = resource_manager.get_sound("sfx_chase_loop")
        flee_snd = resource_manager.get_sound("sfx_flee_loop")

        self.current_scene = SceneLoader.load_from_json(
            json_path, 
            map_matrix, 
            entry_zone, 
            player_sprite, 
            chase_snd,
            flee_snd,
            music_path=music_path, 
            has_darkness=darkness
        )
        self.silence_timer = 0
        self.is_in_silence = False

        if player_pos:
            player_sprite.teleport(player_pos[0], player_pos[1])

        if music_path:
            # music_path es un ID (ej: "bgm_forest"), play_music ya sabe manejarlo
            # music_path is an ID, play_music knows how to handle it
            resource_manager.play_music(music_path, fade_ms=1000)
            self.current_music_path = music_path

        self.current_zone = level_req["entry_zone"]

        tween_manager.clear()

        print(f"{Colors.BRIGHT_CYAN}[LevelManager]{Colors.RESET} Level loaded at zone: {self.current_zone}")

    def on_music_ended(self):
        self.silence_timer = random.randint(80000, 100000)
        self.is_in_silence = True
        self.ambience_timer = random.randint(15000, 30000)
        print(f"{Colors.BRIGHT_CYAN}[LevelManager]{Colors.RESET} Music ended. Silence for {self.silence_timer/1000} seconds.")

    def update(self, delta_time):
        if self.current_scene:
            self.current_scene.enemies.update(delta_time)
            self.current_scene.obstacles.update()
            self.current_scene.interactables.update()
            
        tween_manager.update(delta_time/1000)
        if self.is_in_silence:
            self.silence_timer -= delta_time
            self.ambience_timer -= delta_time


            if self.ambience_timer <= 0:
                if self.ambience_ids:
                    random_id = random.choice(self.ambience_ids)
                    sound = resource_manager.get_sound(random_id)
                    
                    if sound:
                        vol = random.uniform(0.5, 1)
                        sound.set_volume(vol)
                        sound.play()
                        print(f"{Colors.BRIGHT_CYAN}[Ambience]{Colors.RESET} Played '{random_id}' at vol {vol:.2f}")
                        self.retro_effects.add_trauma(1)

                self.ambience_timer = random.randint(15000, 30000)

            if self.silence_timer <= 0:
                self.is_in_silence = False
                if self.current_music_path:
                    try:
                        print(f"{Colors.BRIGHT_CYAN}[LevelManager]{Colors.RESET} Silence over. Replaying music.")
                        resource_manager.play_music(self.current_music_path, loops=0, fade_ms=0)
                        pygame.mixer.music.set_endevent(MUSIC_END_EVENT)
                    except Exception as e:
                        print(f"Error replaying music: {e}")

    def draw(self, screen, player_sprite):
        if self.current_scene:
            self.current_scene.draw(screen, player_sprite)
            
            if self.current_scene.has_darkness:
                self.light_mask.fill((50, 50, 50))
                light_x = player_sprite.rect.centerx - self.light_radius
                light_y = player_sprite.rect.centery - self.light_radius
                
                self.light_mask.blit(self.flashlight_texture, (light_x, light_y), special_flags=pygame.BLEND_ADD)
                
                screen.blit(self.light_mask, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

    def handle_zone_transition(self, player_sprite):
        if not self.current_scene: return

        y_cord, x_cord = self.current_zone
        transition_occurred = False
        
        if player_sprite.rect.left > SCREEN_WIDTH + TRANSITION_BIAS:
            if self.current_scene.check_zone((y_cord, x_cord + 1)):
                x_cord += 1
                player_sprite.rect.left = -10
                transition_occurred = True
            else:
                player_sprite.rect.left = -10
                player_sprite.pos = pygame.Vector2(player_sprite.rect.center)

        elif player_sprite.rect.right < -TRANSITION_BIAS:
            if self.current_scene.check_zone((y_cord, x_cord - 1)):
                x_cord -= 1
                player_sprite.rect.right = SCREEN_WIDTH + 10
                transition_occurred = True
            else:
                player_sprite.rect.right = SCREEN_WIDTH + 10
                player_sprite.pos = pygame.Vector2(player_sprite.rect.center)

        elif player_sprite.rect.top > SCREEN_HEIGHT + TRANSITION_BIAS:
            if self.current_scene.check_zone((y_cord + 1, x_cord)):
                y_cord += 1
                player_sprite.rect.top = -10
                transition_occurred = True
            else:
                player_sprite.rect.top = -10
                player_sprite.pos = pygame.Vector2(player_sprite.rect.center)

        elif player_sprite.rect.bottom < 0:
            if self.current_scene.check_zone((y_cord - 1, x_cord)):
                y_cord -= 1
                player_sprite.rect.bottom = SCREEN_HEIGHT + 10
                transition_occurred = True
            else:
                player_sprite.rect.bottom = SCREEN_HEIGHT + 10
                player_sprite.pos = pygame.Vector2(player_sprite.rect.center)

        if transition_occurred:
            self.current_zone = (y_cord, x_cord)
            self.current_scene.set_location(self.current_zone)
            player_sprite.pos = pygame.Vector2(player_sprite.rect.center)