import pygame
from sys import exit
from src.Game_Constants import *
from src.Obstacles import Obstacle
from src.Interactable import Interactable 
from src.Player import Player
from src.Scene_Loader import SceneLoader
from src.ResourceManager import ResourceManager
from utils import resource_path

from src.ActionManager import ActionManager
from src.EventManager import EventManager
from src.GameState import game_state


def draw_note_ui(screen, note_data):
    """
    Draws the note UI on the screen with the provided text lines.
    """
    padding = 50
    ui_width = SCREEN_WIDTH - padding * 2
    ui_height = SCREEN_HEIGHT - padding * 2

    sheet_rect = pygame.Rect(padding, padding, ui_width, ui_height)
    pygame.draw.rect(screen, (0, 0, 0), sheet_rect)
    pygame.draw.rect(screen, (255, 255, 0), sheet_rect, 3)

    font_path = resource_path("assets/fonts/scary_font.ttf")
    font = pygame.font.Font(font_path, 36)

    line_spacing = 40
    start_x = padding + 20
    start_y = padding + 20

    lines_to_render = []
    if isinstance(note_data, list):
        lines_to_render = note_data
    elif isinstance(note_data, str):
        lines_to_render = note_data.split('\n')

    for i, line in enumerate(lines_to_render):
        render_line = line if line else " "
        
        text_surface = font.render(render_line, True, (255, 255, 0))
        screen.blit(text_surface, (start_x, start_y + i * line_spacing))

    close_font = pygame.font.Font(None, 30)
    close_text = close_font.render("Presiona 'ESPACIO' para cerrar", True, (255, 255, 0))
    close_rect = close_text.get_rect(centerx = sheet_rect.centerx, bottom = sheet_rect.bottom - 20)
    screen.blit(close_text, close_rect)

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

def draw_image_ui(screen, image_path):
    """
    Loads an image to the screen
    """
    try:
        image = pygame.image.load(image_path).convert_alpha()
    except pygame.error as e:
        font = pygame.font.Font(None, 50)
        text = font.render("Error: No se pudo cargar la imagen.", True, (255, 0, 0))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
        return
    
    img_rect = image.get_rect()
    scale = min(SCREEN_WIDTH / img_rect.width, SCREEN_HEIGHT / img_rect.height)
    new_width = int(img_rect.width * scale)
    new_height = int(img_rect.height * scale)
    
    scaled_image = pygame.transform.scale(image, (new_width, new_height))
    scaled_rect = scaled_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    screen.fill((0, 0, 0))
    screen.blit(scaled_image, scaled_rect)

    close_font = pygame.font.Font(None, 30)
    close_text = close_font.render("Presiona 'ESC' o 'ESPACIO' para cerrar", True, (200, 200, 200))
    close_rect = close_text.get_rect(centerx = SCREEN_WIDTH // 2, bottom = SCREEN_HEIGHT - 20)
    screen.blit(close_text, close_rect)

def draw_game_over_screen(screen, image):
    """
    Draws the "Game over" screen
    """
    if image:
        screen.blit(image, (0, 0))
    else:
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 70)
        text = font.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)

    img_rect = image.get_rect()
    scale = min(SCREEN_WIDTH / img_rect.width, SCREEN_HEIGHT / img_rect.height)
    new_width = int(img_rect.width * scale)
    new_height = int(img_rect.height * scale)
    
    scaled_image = pygame.transform.scale(image, (new_width, new_height))
    scaled_rect = scaled_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    screen.fill((0, 0, 0))
    screen.blit(scaled_image, scaled_rect)

    close_font = pygame.font.Font(None, 30)
    close_text = close_font.render("Presiona 'ESC' para reiniciar", True, (200, 200, 200))
    close_rect = close_text.get_rect(centerx = SCREEN_WIDTH // 2, bottom = SCREEN_HEIGHT - 20)
    screen.blit(close_text, close_rect)

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
    
    y_cord, x_cord = Y_CORD, X_CORD
    current_zone = (y_cord, x_cord)

    game_status = "PLAYING"

    image_to_show = None
    
    death_screen_delay = DEATH_DELAY
    game_over_sound_played = False

    note_to_show = None

    sounds = ResourceManager.load_all_sounds("assets/sounds")
    images = ResourceManager.load_all_images("assets/images")
    game_over_image = images.get("death_pic")

    # Ilumination setup
    light_mask = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)) 
    
    light_radius = 250
    flashlight_texture = pygame.Surface((light_radius * 2, light_radius * 2))
    
    for r in range(light_radius, 0, -2):
        intensity = int(255 * (1 - (r / light_radius)))
        pygame.draw.circle(flashlight_texture, (intensity, intensity, intensity), (light_radius, light_radius), r)

    player = pygame.sprite.GroupSingle()
    player_sprite = Player(player_x_pos, player_y_pos)
    player.add(player_sprite)

    current_music_path = LEVEL_MUSIC["forest"]
    initial_darkness = LEVEL_DARKNESS["forest"]
    
    main_scene = SceneLoader.load_from_json(resource_path("data/scene_output_new.json"), WORLD_MAP_LEVEL, INITIAL_ZONE, player_sprite, sounds.get("chase_loop"), sounds.get("flee_loop"), music_path=current_music_path, has_darkness=initial_darkness)
    scene = main_scene

    try:  
        pygame.mixer.music.load(current_music_path)
        pygame.mixer.music.play(loops=-1)
        pygame.mixer.music.set_volume(0.5)
    except pygame.error as e:
        print(f"Error when loading the file: {e}")


    action_manager = ActionManager(sound_library=sounds)
    event_manager = EventManager(action_manager)

    while True:
        screen.fill('black')
        delta_time = clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                return "QUIT"

            if event.type == pygame.KEYDOWN:
                # Debug options
                if event.key == pygame.K_p:
                    print(f"Player Position: {player.sprite.pos}")
                if event.key == pygame.K_SPACE:
                    if game_status == "PLAYING":
                        player.sprite.attack()
                    elif game_status == "READING_NOTE" or game_status == "READING_IMAGE":
                        pygame.mixer.music.unpause()
                        note_to_show = None
                        image_to_show = None
                        game_status = "PLAYING"
                
                elif event.key == pygame.K_ESCAPE:
                    
                    if game_status == "PLAYER_DEAD" or player.sprite.is_defeated:
                        if sounds.get("death_sound"):
                            sounds.get("death_sound").stop()
                        if sounds.get("game_over_sound"):
                            sounds.get("game_over_sound").stop()

                        pygame.mixer.music.stop()
                        return "MAIN_MENU"
                        
                    elif game_status == "READING_NOTE" or game_status == "READING_IMAGE":
                        pygame.mixer.music.unpause()
                        note_to_show = None
                        image_to_show = None
                        game_status = "PLAYING"       

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    if game_status == "PLAYING":
                        player.sprite.stop_attack()

                
        # --- Game logic ---
        if game_status == "PLAYING":  
            seq_result = event_manager.update(delta_time, player_sprite, scene)

            if seq_result:
                handle_event_result(seq_result)

            if not event_manager.is_blocking:
                player.update(scene.obstacles)
            else:
                player_sprite.stop_attack()


            scene.enemies.update(delta_time)
            scene.obstacles.update()
            scene.interactables.update()

            def handle_event_result(result):
                nonlocal game_status, note_to_show, image_to_show
                if not result: return
                
                if result["type"] == "Note":
                    game_status = "READING_NOTE"
                    note_to_show = result["data"]
                    should_play = result.get("play_default_sound", True)
                    has_custom_sound = result.get("sound") is not None
                    if should_play and not has_custom_sound and sounds.get("note_reading_more_vol"): 
                        sounds["note_reading_more_vol"].play()
                    
                elif result["type"] == "Image":
                    image_to_show = result["data"]
                    game_status = "READING_IMAGE"
                    pygame.mixer.music.pause()

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

            # INTERACTABLES (OnEnter & OnInteract)
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

            
            scene.draw(screen, player_sprite)


            if scene.darkness:
                light_mask.fill((50, 50, 50)) 
                
                light_x = player_sprite.rect.centerx - light_radius
                light_y = player_sprite.rect.centery - light_radius
                
                light_mask.blit(flashlight_texture, (light_x, light_y), special_flags=pygame.BLEND_ADD)
                
                screen.blit(light_mask, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            if event_manager.current_image:
                draw_image_ui(screen, event_manager.current_image)

            # Right direction
            if (player.sprite.rect.left > SCREEN_WIDTH + TRANSITION_BIAS):
                if scene.check_zone((y_cord, x_cord + 1)):
                    x_cord += 1
                    current_zone = (y_cord, x_cord)
                    scene.set_location(current_zone)
                    player.sprite.rect.left = 0 - (TRANSITION_BIAS / 2)
                    player.sprite.pos = pygame.Vector2(player.sprite.rect.center)
                else:
                    player.sprite.rect.left = 0 - (TRANSITION_BIAS / 2)
                    player.sprite.pos = pygame.Vector2(player.sprite.rect.center)
            
            # Left direction
            if (player.sprite.rect.right < 0 - TRANSITION_BIAS):
                if scene.check_zone((y_cord, x_cord - 1)):
                    x_cord -= 1
                    current_zone = (y_cord, x_cord)
                    scene.set_location(current_zone)
                    player.sprite.rect.right = SCREEN_WIDTH + (TRANSITION_BIAS / 2)
                    player.sprite.pos = pygame.Vector2(player.sprite.rect.center)
                else:
                    player.sprite.rect.right = SCREEN_WIDTH + (TRANSITION_BIAS / 2)
                    player.sprite.pos = pygame.math.Vector2(player.sprite.rect.center)

            # Bottom direction
            if (player.sprite.rect.top > SCREEN_HEIGHT + TRANSITION_BIAS):
                if scene.check_zone((y_cord + 1, x_cord)):
                    y_cord += 1
                    current_zone = (y_cord, x_cord)
                    scene.set_location(current_zone)
                    player.sprite.rect.top = 0 - (TRANSITION_BIAS / 2)
                    player.sprite.pos = pygame.math.Vector2(player.sprite.rect.center)
                else:
                    player.sprite.rect.top = 0 - TRANSITION_BIAS
                    player.sprite.pos = pygame.math.Vector2(player.sprite.rect.center)

            # Top direction 
            if (player.sprite.rect.bottom < 0):
                if scene.check_zone((y_cord - 1, x_cord)):
                    y_cord -= 1
                    current_zone = (y_cord, x_cord)
                    scene.set_location(current_zone)
                    player.sprite.rect.bottom = SCREEN_HEIGHT + (TRANSITION_BIAS / 2)
                    player.sprite.pos = pygame.math.Vector2(player.sprite.rect.center)
                else:
                    player.sprite.rect.bottom = SCREEN_HEIGHT + TRANSITION_BIAS
                    player.sprite.pos = pygame.math.Vector2(player.sprite.rect.center)
            
            if player.sprite.is_defeated:
                death_screen_delay -= delta_time
                if death_screen_delay <= 0:
                    game_status = "PLAYER_DEAD"

                    if not game_over_sound_played:
                        if sounds.get("game_over_sound"):
                            sounds.get("game_over_sound").play()
                        game_over_sound_played = True
        
        elif game_status == "PLAYER_DEAD":
            player.update(scene.obstacles)
            scene.enemies.update(delta_time)
            scene.draw(screen, player_sprite)
            draw_game_over_screen(screen, game_over_image)

        elif game_status == "READING_NOTE":
            draw_note_ui(screen, note_to_show)
        
        elif game_status == "READING_IMAGE":
            draw_image_ui(screen, image_to_show)


        # --- Change level management ---
        level_request = game_state.consume_level_change()
        if level_request:
            scene.cleanup()
            screen.fill((0, 0, 0))
            pygame.display.flip()

            new_scene = SceneLoader.load_from_json(
                level_request["json_path"],
                level_request["map_matrix"],
                level_request["entry_zone"],
                player_sprite,
                sounds.get("chase_loop"),
                sounds.get("flee_loop"),
                level_request["music_path"],
                level_request["darkness"]
            )

            new_music = level_request["music_path"]

            if new_music and new_music != current_music_path:
                    print(f"Changing music: {new_music}")
                    pygame.mixer.music.fadeout(500)
                    try:
                        pygame.mixer.music.load(resource_path(new_music))
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(0.60)
                    except Exception as e:
                        print(f"Error when loading the file: {e}")
                    current_music_path = new_music

            scene = new_scene
            current_zone = level_request["entry_zone"]
            y_cord, x_cord = current_zone

            pos = level_request["player_pos"]
            player_sprite.rect.topleft = pos
            player_sprite.pos = pygame.math.Vector2(pos)

            print("Level changed")
            continue
        
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