import pygame
import sys
from src.Game_Constants import *
from src.Player import Player
from src.ResourceManager import ResourceManager
from src.UIManager import UIManager
from src.ActionManager import ActionManager
from src.EventManager import EventManager
from src.LevelManager import LevelManager
from src.GameState import game_state
from src.Game_Enums import Actions, Conditions
from src.Effects import RetroEffects
from utils import resource_path

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.RESIZABLE | pygame.FULLSCREEN | pygame.DOUBLEBUF, vsync=1)
        pygame.display.set_caption('Oakhill')
        self.clock = pygame.time.Clock()

        self._load_resources()

        self.retro_effects = RetroEffects()
        
        self.action_manager = ActionManager(self.sounds)
        self.event_manager = EventManager(self.action_manager)
        self.ui_manager = UIManager(self.sounds, self.retro_effects)
        self.level_manager = LevelManager(self.sounds, self.retro_effects)
        
        self.state = "MAIN_MENU"
        self.game_over_sound_played = False
        self.death_screen_delay = DEATH_DELAY

        self.transition_state = "NONE"
        self.transition_timer = 0
        self.transition_duration = 500
        self.pending_level_req = None

        self.last_frame_triggers = set()
        
        self.debug_mode = False

        self.player_group = pygame.sprite.GroupSingle()
        self.player = Player(0, 0)
        self.player_group.add(self.player)

    def _load_resources(self):
        try:
            icon = pygame.image.load(resource_path("assets/images/logo.png"))
            pygame.display.set_icon(icon)
        except: pass

        self.sounds = ResourceManager.load_all_sounds("assets/sounds")
        self.images = ResourceManager.load_all_images("assets/images")

        if self.sounds.get("chase_loop"): self.sounds["chase_loop"].set_volume(0.5)
        if self.sounds.get("flee_loop"): self.sounds["flee_loop"].set_volume(0.5)

    def run(self):
        while self.state != "QUIT":
            if self.state == "MAIN_MENU":
                self._menu_loop()
            elif self.state == "GAMEPLAY":
                self._game_loop()
        
        pygame.quit()
        sys.exit()

    def _menu_loop(self):
        title_font = ResourceManager.get_font(90)
        btn_font = ResourceManager.get_font(60)

        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(resource_path("assets/music/MENU.wav"))
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.6)
        except: pass

        title_surf = title_font.render("OAKHILL", True, (255, 255, 0))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
        
        play_rect = pygame.Rect(0,0,200,80); play_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)
        quit_rect = pygame.Rect(0,0,200,80); quit_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = "QUIT"
                    return
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if play_rect.collidepoint(event.pos):
                            pygame.mixer.music.stop()
                            self._start_new_game()
                            self.state = "GAMEPLAY"
                            return
                        if quit_rect.collidepoint(event.pos):
                            self.state = "QUIT"
                            return

            self.screen.fill('black')
            m_pos = pygame.mouse.get_pos()
            
            col_play = (255, 255, 255) if play_rect.collidepoint(m_pos) else (200, 200, 200)
            col_quit = (255, 255, 255) if quit_rect.collidepoint(m_pos) else (200, 200, 200)
            
            txt_play = btn_font.render("Jugar", True, col_play)
            txt_quit = btn_font.render("Salir", True, col_quit)
            
            self.screen.blit(title_surf, title_rect)
            self.screen.blit(txt_play, txt_play.get_rect(center=play_rect.center))
            self.screen.blit(txt_quit, txt_quit.get_rect(center=quit_rect.center))
            
            pygame.display.flip()
            self.clock.tick(60)

    def _start_new_game(self):
        game_state.reset()
        self.game_over_sound_played = False
        self.death_screen_delay = DEATH_DELAY
        self.ui_manager.close()

        self.level_manager.reset_music_state()

        self.player.is_defeated = False
        self.player.cancel_attack()
        self.player.direction = pygame.math.Vector2(0,0)
        self.player.velocity = pygame.math.Vector2(0,0)
        self.player.facing = "down"
        self.player.image = self.player.animations["down"].images[0]
        
        start_req = {
            "json_path": resource_path("data/forest.json"),
            "map_matrix": WORLD_MAP_LEVEL,
            "entry_zone": INITIAL_ZONE,
            "player_pos": (600, 300),
            "music_path": LEVEL_MUSIC.get("forest"),
            "darkness": False
        }
        self.level_manager.load_level_from_request(start_req, self.player)

    def _game_loop(self):
        while self.state == "GAMEPLAY":
            self.screen.fill('black')
            delta_time = self.clock.get_time()

            self._handle_input_events()
            self.ui_manager.update(delta_time)

            if self.transition_state != "NONE":
                self._update_transition(delta_time)
            else:
                request_handled = self._check_game_requests()
                if not request_handled:
                    self._update_gameplay(delta_time)

            self._draw(delta_time)

            pygame.display.flip()
            self.clock.tick(60)


    def _handle_input_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = "QUIT"
                return

            if event.type == MUSIC_END_EVENT:
                self.level_manager.on_music_ended()

            if self.transition_state != "NONE":
                continue

            if self.ui_manager.handle_input(event):
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: self.player.attack()
                elif event.key == pygame.K_ESCAPE: self._handle_pause_or_exit()
                elif event.key == pygame.K_F11: pygame.display.toggle_fullscreen()
                elif event.key == pygame.K_F1: self.debug_mode = not self.debug_mode
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE: self.player.stop_attack()

    def _check_game_requests(self):
        teleport_req = game_state.consume_teleport()
        if teleport_req:
            self.pending_teleport = teleport_req
            self.transition_state = "OUT"
            self.transition_timer = 0
            print("[Game] Starting Teleport Transition")
            return True 
        
        level_req = game_state.consume_level_change()
        if level_req:
            self.screen.fill((0, 0, 0)); pygame.display.flip()
            self.level_manager.load_level_from_request(level_req, self.player)
            self.retro_effects.set_transition(0.0)
            return True
            
        return False

    def _update_transition(self, delta_time):
        self.transition_timer += delta_time
        
        progress = min(1.0, self.transition_timer / self.transition_duration)

        if self.transition_state == "OUT":
            self.retro_effects.set_transition(progress)

            if progress >= 1.0:
                
                if hasattr(self, 'pending_teleport') and self.pending_teleport:
                    data = self.pending_teleport
                    if data["zone"] and data["zone"] != "None":
                        self.level_manager.current_scene.change_zone_by_string(data["zone"])
                    self.player.teleport(data["x"], data["y"])
                    self.pending_teleport = None
                    print("[Game] Teleport executed mid-transition")

                self.transition_state = "IN"
                self.transition_timer = 0 
                self.retro_effects.set_transition(1.0) 
        
        elif self.transition_state == "IN":
            inverse_progress = 1.0 - progress
            self.retro_effects.set_transition(inverse_progress)

            if progress >= 1.0:
                self.transition_state = "NONE"
                self.retro_effects.set_transition(0.0)
                print("[Game] Transition finished")

    def _update_gameplay(self, delta_time):
        if not self.ui_manager.active or not self.ui_manager.is_blocking:
            seq_result = self.event_manager.update(delta_time, self.player, self.level_manager.current_scene)
            if seq_result: self._handle_event_result(seq_result)

            if not self.event_manager.is_blocking:
                self.player_group.update(self.level_manager.current_scene.obstacles)
            else:
                self.player.stop_attack()

            
            self.level_manager.update(delta_time)
            self.level_manager.handle_zone_transition(self.player)
            
            self._handle_collisions_and_triggers() 

            if self.player.is_defeated:
                self.death_screen_delay -= delta_time
                if self.death_screen_delay <= 0 and not self.game_over_sound_played:
                    if self.sounds.get("game_over_sound"): self.sounds["game_over_sound"].play()
                    self.game_over_sound_played = True

    def _draw(self, delta_time):
        if self.player.is_defeated and self.death_screen_delay <= 0:
            self.level_manager.draw(self.screen, self.player)
            UIManager.draw_game_over(self.screen, self.images.get("death_pic"))
            self.retro_effects.update_and_draw(self.screen, delta_time)
        else:
            self.level_manager.draw(self.screen, self.player)

            if self.debug_mode:
                self._debug_draw_collisions()

            self.ui_manager.draw(self.screen)
            if self.event_manager.current_image:
                self.ui_manager.show_image(self.event_manager.current_image)
            self.retro_effects.update_and_draw(self.screen, delta_time)    

    def _handle_pause_or_exit(self):
        if self.player.is_defeated:
            pygame.mixer.music.stop()
            
            if self.sounds.get("game_over_sound"): 
                self.sounds["game_over_sound"].stop()
            
            if self.sounds.get("death_sound"): 
                self.sounds["death_sound"].stop()
            
            self.state = "MAIN_MENU"

    def _handle_collisions_and_triggers(self):
        scene = self.level_manager.current_scene
        if not scene: return

        hits = pygame.sprite.spritecollide(
            self.player, 
            scene._triggers, 
            False, 
            collided=lambda p, t: p.collision_rect.colliderect(t.rect)
        )
        
        current_triggers_set = set(hits)

        for trig in current_triggers_set:
            should_execute = False

            if trig.condition in [Conditions.ON_STAY, Conditions.IF_FLAG]:
                should_execute = True

            elif trig.condition == Conditions.ON_ENTER:
                if trig not in self.last_frame_triggers:
                    should_execute = True

            if should_execute:
                res = self.event_manager.process_trigger(trig, self.player, scene)
                self._handle_event_result(res)

        self.last_frame_triggers = current_triggers_set

        # for trig in hits:
        #     if trig.condition in [Conditions.ON_STAY, Conditions.IF_FLAG]:
        #         res = self.event_manager.process_trigger(trig, self.player, scene)
        #         self._handle_event_result(res)
        
        processed = False
        for obj in scene.interactables:
            contact = False
            
            if obj.trigger_condition == Conditions.ON_STAY:
                if self.player.collision_rect.colliderect(obj.rect):
                    if obj.progress_interaction() != "finished": 
                        obj.current_progress = obj.interaction_duration
                    contact = True

            elif obj.trigger_condition == Conditions.ON_ENTER:
                if self.player.collision_rect.colliderect(obj.rect):
                    if obj.progress_interaction() != "finished": 
                        obj.current_progress = obj.interaction_duration
                    contact = True
            
            elif obj.trigger_condition in [Conditions.ON_INTERACT, "None"]:
                if self.player.is_attacking and self.player.attack_rect.colliderect(obj.rect):
                    contact = True
            
            if contact and not processed:
                status = obj.progress_interaction()
                if status == "finished":
                    processed = True
                    res = self.event_manager.process_trigger(obj, self.player, scene)
                    self._handle_event_result(res)
                    obj.read()
                    
                    if self.player.is_attacking: 
                        self.player.cancel_attack()
            else:
                obj.reset_interaction()

        if self.player.is_attacking:
            for enemy in scene.enemies:
                if enemy.collision_rect.colliderect(self.player.attack_rect) and hasattr(enemy, 'while_attacked'):
                    enemy.while_attacked()

        for enemy in scene.enemies:
            if enemy.collides_with(self.player) and not self.player.is_defeated:
                self.player.defeat()
                
                pygame.mixer.music.stop()
                if self.sounds.get("chase_loop"): self.sounds["chase_loop"].stop()
                if self.sounds.get("death_sound"): self.sounds["death_sound"].play()
                
                break

    def _debug_draw_collisions(self):
        scene = self.level_manager.current_scene
        if not scene: return

        COLOR_OBSTACLE = (0, 255, 255)    # Cian
        COLOR_INTERACTABLE = (0, 255, 0)  # Verde
        COLOR_TRIGGER = (255, 0, 255)     # Magenta
        COLOR_ENEMY = (255, 0, 0)         # Rojo
        COLOR_PLAYER = (255, 255, 0)      # Amarillo
        COLOR_ATTACK = (255, 165, 0)      # Naranja

        for obj in scene.obstacles:
            rect = getattr(obj, "collision_rect", obj.rect)
            pygame.draw.rect(self.screen, COLOR_OBSTACLE, rect, 1)

        for obj in scene.interactables:
            pygame.draw.rect(self.screen, COLOR_INTERACTABLE, obj.rect, 1)

        for trig in scene._triggers:
            pygame.draw.rect(self.screen, COLOR_TRIGGER, trig.rect, 1)

        for enemy in scene.enemies:
            rect = getattr(enemy, "collision_rect", enemy.rect)
            pygame.draw.rect(self.screen, COLOR_ENEMY, rect, 1)
            

        if hasattr(self.player, "collision_rect"):
            pygame.draw.rect(self.screen, COLOR_PLAYER, self.player.collision_rect, 1)
        else:
            pygame.draw.rect(self.screen, COLOR_PLAYER, self.player.rect, 1)

        if self.player.is_attacking:
             pygame.draw.rect(self.screen, COLOR_ATTACK, self.player.attack_rect, 2)
                    

    def _handle_event_result(self, result):
        if not result: return

        should_block = result.get("blocking", False)
        
        if result["type"] == "Note":
            self.ui_manager.show_note(result["data"], blocking=should_block)

        elif result["type"] == "Dialogue":
            self.ui_manager.show_dialogue(result["data"], blocking=should_block)
                
        elif result["type"] == "Image":
            self.ui_manager.show_image(result["data"], blocking=should_block)
            
            if result.get("pause_music", False):
                pygame.mixer.music.pause()

        elif result["type"] == "Animation":
            self.ui_manager.show_animation(result["data"], speed=result["speed"], blocking=should_block, loop=result.get("loop", True))
            
            if result.get("pause_music", False):
                pygame.mixer.music.pause()