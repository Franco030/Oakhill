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
from utils import resource_path

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.RESIZABLE | pygame.DOUBLEBUF, vsync=1)
        pygame.display.set_caption('Oakhill')
        self.clock = pygame.time.Clock()
        
        self._load_resources()
        
        self.action_manager = ActionManager(self.sounds)
        self.event_manager = EventManager(self.action_manager)
        self.ui_manager = UIManager()
        self.level_manager = LevelManager(self.sounds)
        
        self.state = "MAIN_MENU"
        self.game_over_sound_played = False
        self.death_screen_delay = DEATH_DELAY
        
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

        if self.sounds.get("chase_loop"): self.sounds["chase_loop"].set_volume(0.6)
        if self.sounds.get("flee_loop"): self.sounds["flee_loop"].set_volume(0.6)
        if self.sounds.get("note_reading_more_vol"): self.sounds["note_reading_more_vol"].set_volume(1.0)

    def run(self):
        while self.state != "QUIT":
            if self.state == "MAIN_MENU":
                self._menu_loop()
            elif self.state == "GAMEPLAY":
                self._game_loop()
        
        pygame.quit()
        sys.exit()

    def _menu_loop(self):
        try:
            font_path = resource_path("assets/fonts/scary_font.ttf")
            title_font = pygame.font.Font(font_path, 90)
            btn_font = pygame.font.Font(font_path, 60)
        except:
            title_font = pygame.font.Font(None, 100)
            btn_font = pygame.font.Font(None, 70)

        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(resource_path("assets/sounds/main_menu_song.wav"))
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(0.7)
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

        self.player.is_defeated = False
        self.player.cancel_attack()
        self.player.direction = pygame.math.Vector2(0,0)
        self.player.velocity = pygame.math.Vector2(0,0)
        self.player.facing = "down"
        self.player.image = self.player.animations["down"].images[0]
        
        start_req = {
            "json_path": resource_path("data/scene_output_new.json"),
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

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state = "QUIT"
                    return
                
                if self.ui_manager.handle_input(event):
                    continue 

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.attack()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.stop()
                        if self.sounds.get("game_over_sound"): self.sounds["game_over_sound"].stop()
                        if self.sounds.get("death_sound"): self.sounds["death_sound"].stop()
                        self.state = "MAIN_MENU"
                        return

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.player.stop_attack()

            if not self.ui_manager.active or not self.ui_manager.is_blocking:
                seq_result = self.event_manager.update(delta_time, self.player, self.level_manager.current_scene)
                if seq_result:
                    self._handle_event_result(seq_result)

                if not self.event_manager.is_blocking:
                    self.player_group.update(self.level_manager.current_scene.obstacles)
                else:
                    self.player.stop_attack()
                
                self.level_manager.update(delta_time)
                self.level_manager.handle_zone_transition(self.player)
                
                scene = self.level_manager.current_scene
                if scene:
                    hits = pygame.sprite.spritecollide(self.player, scene._triggers, False, collided=lambda p,t: p.collision_rect.colliderect(t.rect))
                    for trig in hits:
                        if trig.condition in ["OnEnter", "IfFlag"]:
                            res = self.event_manager.process_trigger(trig, self.player, scene)
                            self._handle_event_result(res)
                    
                    processed = False
                    for obj in scene.interactables:
                        contact = False
                        if obj.trigger_condition == "OnEnter":
                            if self.player.collision_rect.colliderect(obj.rect):
                                if obj.progress_interaction() != "finished": obj.current_progress = obj.interaction_duration
                                contact = True
                        elif obj.trigger_condition in ["OnInteract", "None"]:
                            if self.player.is_attacking and self.player.attack_rect.colliderect(obj.rect):
                                contact = True
                        
                        if contact and not processed:
                            status = obj.progress_interaction()
                            if status == "finished":
                                processed = True
                                res = self.event_manager.process_trigger(obj, self.player, scene)
                                self._handle_event_result(res)
                                obj.read() # Persistencia visual
                                if self.player.is_attacking: self.player.cancel_attack()
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

                req = game_state.consume_level_change()
                if req:
                    self.screen.fill((0,0,0)); pygame.display.flip()
                    self.level_manager.load_level_from_request(req, self.player)
                    continue 

                if self.player.is_defeated:
                    self.death_screen_delay -= delta_time
                    if self.death_screen_delay <= 0:
                        if not self.game_over_sound_played:
                            if self.sounds.get("game_over_sound"): self.sounds["game_over_sound"].play()
                            self.game_over_sound_played = True
                        pass 

            if self.player.is_defeated and self.death_screen_delay <= 0:
                self.level_manager.draw(self.screen, self.player)
                UIManager.draw_game_over(self.screen, self.images.get("death_pic"))
            else:
                self.level_manager.draw(self.screen, self.player)
                self.ui_manager.draw(self.screen)
                
                if self.event_manager.current_image:
                    self.ui_manager.show_image(self.event_manager.current_image)

            pygame.display.flip()
            self.clock.tick(60)

    def _handle_event_result(self, result):
        if not result: return

        should_block = result.get("blocking", False)
        print(f"Should block, {should_block}")
        
        if result["type"] == "Note":
            self.ui_manager.show_note(result["data"], blocking=should_block)
                
        elif result["type"] == "Image":
            self.ui_manager.show_image(result["data"], blocking=should_block)
            pygame.mixer.music.pause()