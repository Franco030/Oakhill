"""
NO LONGER IN USE
"""



import pygame
from sys import exit
from src.Game_Constants import *
from src.Obstacles import Obstacle
from src.Interactable import Interactable 
from src.Player import Player
from src.Scene_Loader import SceneLoader
from src.ResourceManager import ResourceManager
from src.UIManager import UIManager
from src.LevelManager import LevelManager
from utils import resource_path

from src.ActionManager import ActionManager
from src.EventManager import EventManager
from src.GameState import game_state


def draw_defeat_text(screen):
    """
    Draws the defeat text on the screen.
    """
    font = pygame.font.Font(None, 50)
    text_surface = font.render('Presiona ESC para reiniciar', True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))

    s = pygame.Surface((text_rect.width + 20, text_rect.height + 20))
    s.set_alpha(128)
    s.fill((0, 0, 0))
    screen.blit(s, (text_rect.left - 10, text_rect.top - 10))
    screen.blit(text_surface, text_rect)


def menu_loop(screen, clock):
    """
    Main menu loop
    """
    try:
        font_path = resource_path("assets/fonts/scary_font.ttf")
        title_font = pygame.font.Font(font_path, 90)
        button_font = pygame.font.Font(font_path, 60)
    except Exception:
        title_font = pygame.font.Font(None, 100)
        button_font = pygame.font.Font(None, 70)

    try:
        pygame.mixer.music.load(resource_path("assets/sounds/main_menu_song.wav")) 
        pygame.mixer.music.play(loops=-1)
        pygame.mixer.music.set_volume(0.7)
    except pygame.error as e:
        print(f"Error while loading the file: {e}")


    title_text = title_font.render("OAKHILL", True, (255, 255, 0))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))

    play_text = button_font.render("Jugar", True, (200, 200, 200))
    play_rect = play_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

    quit_text = button_font.render("Salir", True, (200, 200, 200))
    quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))

    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return "QUIT"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if play_rect.collidepoint(event.pos):
                        pygame.mixer.music.stop()
                        return "GAMEPLAY" 
                    if quit_rect.collidepoint(event.pos):
                        pygame.mixer.music.stop()
                        return "QUIT"

        screen.fill('black')

        mouse_pos = pygame.mouse.get_pos()
        
        if play_rect.collidepoint(mouse_pos):
            play_text = button_font.render("Jugar", True, (255, 255, 255))
        else:
            play_text = button_font.render("Jugar", True, (200, 200, 200))

        if quit_rect.collidepoint(mouse_pos):
            quit_text = button_font.render("Salir", True, (255, 255, 255))
        else:
            quit_text = button_font.render("Salir", True, (200, 200, 200))

        screen.blit(title_text, title_rect)
        screen.blit(play_text, play_rect)
        screen.blit(quit_text, quit_rect)

        pygame.display.flip()
        clock.tick(FPS) 


def game_loop(screen, clock):
    game_state.reset()

    player_x_pos = 600
    player_y_pos = 300

    game_status = "PLAYING"

    death_screen_delay = DEATH_DELAY
    game_over_sound_played = False

    sounds = ResourceManager.load_all_sounds("assets/sounds")
    images = ResourceManager.load_all_images("assets/images")
    game_over_image = images.get("death_pic")

    player = pygame.sprite.GroupSingle()
    player_sprite = Player(player_x_pos, player_y_pos)
    player.add(player_sprite)


    action_manager = ActionManager(sounds)
    event_manager = EventManager(action_manager)
    ui_manager = UIManager()
    level_manager = LevelManager(sounds)
    start_request = {
        "json_path": resource_path("data/scene_output_new.json"),
        "map_matrix": WORLD_MAP_LEVEL,
        "entry_zone": INITIAL_ZONE,
        "player_pos": (player_x_pos, player_y_pos),
        "music_path": LEVEL_MUSIC.get("forest"),
        "darkness": LEVEL_DARKNESS.get("forest", False)
    }
    level_manager.load_level_from_request(start_request, player_sprite)
    

    def handle_event_result(result):
        if not result: return

        if result["type"] == "Note":
            ui_manager.show_note(result["data"])
            if result.get("play_default_sound", True) and sounds.get("note"):
                sounds["note_reading_more_vol"].play()
            
            
        elif result["type"] == "Image":
            ui_manager.show_image(result["data"])
            pygame.mixer.music.pause()

    while True:
        screen.fill('black')
        delta_time = clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return "QUIT"
            
            if ui_manager.handle_input(event):
                continue

            if event.type == pygame.KEYDOWN:
                # Debug options
                if event.key == pygame.K_p:
                    print(f"Player Position: {player.sprite.pos}")
                if event.key == pygame.K_SPACE:
                        player.sprite.attack()
                
                elif event.key == pygame.K_ESCAPE:
                    if player.sprite.is_defeated:
                        if sounds.get("death_sound"):
                            sounds.get("death_sound").stop()
                        if sounds.get("game_over_sound"):
                            sounds.get("game_over_sound").stop()

                        pygame.mixer.music.stop()
                        return "MAIN_MENU" 

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    player.sprite.stop_attack()
                
        # --- Game logic ---
        if game_status == "PLAYING":  
            scene = level_manager.current_scene
            level_manager.update(delta_time)
            if not ui_manager.active:
                seq_result = event_manager.update(delta_time, player_sprite, scene)

                if seq_result:
                    handle_event_result(seq_result)

                if not event_manager.is_blocking:
                    player.update(scene.obstacles)
                else:
                    player_sprite.stop_attack()

                hit_triggers = pygame.sprite.spritecollide(
                    player_sprite, 
                    scene._triggers, 
                    False,
                    collided=lambda p, t: p.collision_rect.colliderect(t.rect)
                )
                for trig in hit_triggers:
                    if trig.condition in ["OnEnter", "IfFlag"]:
                        res = event_manager.process_trigger(trig, player_sprite, scene)
                        handle_event_result(res)

                # INTERACTABLES (OnEnter and OnInteract)
                processed_interaction = False 
                for obj in scene.interactables:
                    is_contacting = False
                    
                    if obj.trigger_condition == "OnEnter":
                        if player_sprite.collision_rect.colliderect(obj.rect):
                            if obj.progress_interaction() != "finished": 
                                obj.current_progress = obj.interaction_duration 
                            is_contacting = True

                    elif obj.trigger_condition == "OnInteract" or obj.trigger_condition == "None":
                        if player_sprite.is_attacking:
                            if player_sprite.attack_rect.colliderect(obj.rect):
                                is_contacting = True

                    if is_contacting and not processed_interaction:
                        status = obj.progress_interaction() 
                        if status == "finished":
                            processed_interaction = True
                            
                            res = event_manager.process_trigger(obj, player_sprite, scene)
                            handle_event_result(res)

                            obj.read()
                            
                            if player_sprite.is_attacking:
                                player_sprite.cancel_attack()
                        
                    else:
                        obj.reset_interaction()


                if player_sprite.is_attacking:
                    for enemy in scene.enemies:
                        if enemy.collision_rect.colliderect(player_sprite.attack_rect):
                            if hasattr(enemy, 'while_attacked'):
                                enemy.while_attacked()

                for enemy in scene.enemies:
                    if enemy.collides_with(player.sprite) and not player.sprite.is_defeated:
                        player.sprite.defeat() 
                        pygame.mixer.music.stop()
                        
                        if sounds.get("chase_sound"):
                            sounds.get("chase_sound").stop()

                        if sounds.get("death_sound"):
                            sounds.get("death_sound").play()

                        break

                    # --- Change level management ---
                level_req = game_state.consume_level_change()
                if level_req:
                    screen.fill((0, 0, 0))
                    pygame.display.flip()
                    
                    level_manager.load_level_from_request(level_req, player_sprite)
                    
                    scene = level_manager.current_scene
                    continue
                level_manager.handle_zone_transition(player_sprite)
            
                if player.sprite.is_defeated:
                    death_screen_delay -= delta_time
                    if death_screen_delay <= 0:
                        game_status = "PLAYER_DEAD"
                        if not game_over_sound_played:
                            if sounds.get("game_over_sound"):
                                sounds.get("game_over_sound").play()
                            game_over_sound_played = True
            
            level_manager.draw(screen, player_sprite)
            ui_manager.draw(screen)
        
        elif game_status == "PLAYER_DEAD":
            if pygame.time.get_ticks() % 1000 < 20: 
                print(f"[DEBUG DEAD] Estado: {game_status}")
                print(f"[DEBUG DEAD] Imagen Variable: {game_over_image}")
                if game_over_image:
                    print(f"[DEBUG DEAD] Tamaño Imagen: {game_over_image.get_size()}")
            player.update(scene.obstacles)
            scene.enemies.update(delta_time)
            scene.draw(screen, player_sprite)
            UIManager.draw_game_over(screen, game_over_image)

        else:
            scene.draw(screen, player_sprite)
            ui_manager.draw(screen)

        
        pygame.display.flip()
        clock.tick(FPS)

def main():
    """
    The master loop calls game_loop() repeatedly
    """
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.RESIZABLE | pygame.DOUBLEBUF, vsync=1)
    pygame.display.set_caption('Oakhill')

    try:
        logo_image = pygame.image.load(resource_path("assets/images/logo.png"))
        pygame.display.set_icon(logo_image)
    except pygame.error as e:
        print(f"Error when loading the file: {e}")


    clock = pygame.time.Clock()

    master_game_state = "MAIN_MENU"

    while master_game_state != "QUIT":
        if master_game_state == "MAIN_MENU":
            master_game_state = menu_loop(screen, clock)
        elif master_game_state == "GAMEPLAY":
            master_game_state = game_loop(screen, clock)

    pygame.quit()
    exit()

if __name__ == "__main__":
    main()