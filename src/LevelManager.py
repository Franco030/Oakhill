import pygame
from src.Scene_Loader import SceneLoader
from src.GameState import game_state
from src.Game_Constants import MAPS, LEVEL_MUSIC, LEVEL_DARKNESS, SCREEN_WIDTH, SCREEN_HEIGHT, TRANSITION_BIAS, MUSIC_END_EVENT
from utils import resource_path
import random

class LevelManager:
    def __init__(self, sounds):
        self.sounds = sounds

        self.current_scene = None
        self.current_music_path = None

        self.silence_timer = 0
        self.is_in_silence = False

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

    def load_level_from_request(self, level_req, player_sprite):
        if self.current_scene:
            self.current_scene.cleanup()
            
        self.current_scene = SceneLoader.load_from_json(
            level_req["json_path"],
            level_req["map_matrix"],
            level_req["entry_zone"],
            player_sprite,
            self.sounds.get("chase_loop"),
            self.sounds.get("flee_loop"),
            level_req["music_path"],
            level_req["darkness"]
        )

        self.silence_timer = 0
        self.is_in_silence = False

        new_music = level_req["music_path"]
        if new_music and new_music != self.current_music_path:
            print(f"[LevelManager] Changing music to: {new_music}")
            pygame.mixer.music.fadeout(500)
            try:
                pygame.mixer.music.load(resource_path(new_music))
                pygame.mixer.music.play(0)
                pygame.mixer.music.set_endevent(MUSIC_END_EVENT)
                pygame.mixer.music.set_volume(0.5)
            except Exception as e:
                print(f"Error loading music: {e}")
            self.current_music_path = new_music

        self.current_zone = level_req["entry_zone"]
        
        pos = level_req["player_pos"]
        player_sprite.teleport(pos[0], pos[1])
        
        print(f"[LevelManager] Level loaded at zone: {self.current_zone}")

    def on_music_ended(self):
        self.silence_timer = random.randint(90000, 150000)
        self.is_in_silence = True
        print(f"[LevelManager] Music ended. Silence for {self.silence_timer/1000} seconds.")

    def update(self, delta_time):
        if self.current_scene:
            self.current_scene.enemies.update(delta_time)
            self.current_scene.obstacles.update()
            self.current_scene.interactables.update()

        if self.is_in_silence:
            self.silence_timer -= delta_time
            if self.silence_timer <= 0:
                self.is_in_silence = False
                if self.current_music_path:
                    try:
                        print("[LevelManager] Silence over. Replaying music.")
                        pygame.mixer.music.play(0)
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