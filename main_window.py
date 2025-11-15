import pygame
from sys import exit
from src.Game_Constants import *
from src.Obstacles import *
from src.Interactable import Note, Scarecrow, Image
from src.Player import Player
from src.Scene_Loader import SceneLoader
from utils import resource_path

def draw_note_ui(screen, note_text_lines):
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

    for i, line in enumerate(note_text_lines):
        text_surface = font.render(line, True, (255, 255, 0))
        screen.blit(text_surface, (start_x, start_y + i * line_spacing))

    close_font = pygame.font.Font(None, 30)
    close_text = close_font.render("Presiona 'ESC' o 'ESPACIO' para cerrar", True, (255, 255, 0))
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

def find_safe_spawn(target_pos, player_sprite, obstacles):
    """
    Finds a safe spawn position for the player
    """

    player_w = player_sprite.collision_rect.width
    player_h = player_sprite.collision_rect.height

    test_rect = pygame.Rect(0, 0, player_w, player_h)
    test_rect.center = target_pos

    is_safe = True
    for obs in obstacles:
        if obs.collision_rect.colliderect(test_rect):
            is_safe = False
            break

    if is_safe:
        return target_pos
    
    search_radius = 1
    max_search_radius = 50
    step_distance = max(player_w, player_h)

    while search_radius < max_search_radius:
        distance = search_radius * step_distance

        search_points = [
            (target_pos[0], target_pos[1] - distance), # N
            (target_pos[0] + distance, target_pos[1] - distance), # NE
            (target_pos[0] + distance, target_pos[1]), # E
            (target_pos[0] + distance, target_pos[1] + distance), # SE
            (target_pos[0], target_pos[1] + distance), # S
            (target_pos[0] - distance, target_pos[1] + distance), # SW
            (target_pos[0] - distance, target_pos[1]), # W
            (target_pos[0] - distance, target_pos[1] - distance)  # NW
        ]

        for point in search_points:
            test_rect.center = point
            is_safe = True
            for obs in obstacles:
                if obs.collision_rect.colliderect(test_rect):
                    is_safe = False
                    break
            if is_safe:
                return point
        search_radius += 1
    return target_pos



def game_loop():
    player_x_pos = 600
    player_y_pos = 300
    

    y_cord, x_cord = 5, 2
    current_zone = (y_cord, x_cord)

    game_state = "PLAYING" # Other states could be "PLAYER_DEAD", "READING_NOTE"


    note_to_show = None
    note_being_interacted = None

    zone_event_triggered = set()

    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.RESIZABLE | pygame.DOUBLEBUF, vsync=1)
    pygame.display.set_caption('Oakhill')
    clock = pygame.time.Clock()


    try:
        chase_sound = pygame.mixer.Sound(resource_path("assets/sounds/chase_loop.wav"))
    except pygame.error as e:
        print("Error when loading the file")
        chase_sound = None

    try:
        flee_sound = pygame.mixer.Sound(resource_path("assets/sounds/flee_loop.wav"))
    except pygame.error as e:
        print("Error when loading the file")
        flee_sound = None

    try:
        note_interact_sound = pygame.mixer.Sound(resource_path("assets/sounds/note_reading_more_vol.wav"))
    except pygame.error as e:
        print("Error when loading the file")
        note_interact_sound = None

    try:
        screaming_sound = pygame.mixer.Sound(resource_path("assets/sounds/scream.wav"))
        screaming_sound.set_volume(0.5)
    except pygame.error as e:
        print("Error when loading the file")
        screaming_sound = None

    try:
        walking_sound = pygame.mixer.Sound(resource_path("assets/sounds/steps_cut.wav"))
        walking_sound.set_volume(0.6)
    except pygame.error as e:
        print("Error when loading the file")
        walking_sound = None

    try:
        secret_revealed = pygame.mixer.Sound(resource_path("assets/sounds/item_discovered.wav"))
    except pygame.error as e:
        print("Error when loading the file")
        secret_revealed = None

    try:
        death_sound = pygame.mixer.Sound(resource_path("assets/sounds/death_sound_final.wav"))
    except pygame.error as e:
        print(f"Error when loading the file: {e}")
        death_sound = None

    try:
        game_over_image = pygame.image.load(resource_path("assets/images/death_pic.png")).convert_alpha()
        # game_over_image = pygame.transform.scale(game_over_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except pygame.error as e:
        print(f"Error when loading the file: {e}")
        game_over_image = None

    try:
        pygame.mixer.music.load(resource_path("assets/sounds/background_sound.wav"))
        pygame.mixer.music.play(loops=-1)
        pygame.mixer.music.set_volume(0.5)
    except pygame.error as e:
        print(f"Advertencia: No se pudo cargar la música de fondo: {e}")



    player = pygame.sprite.GroupSingle()
    player_sprite = Player(player_x_pos, player_y_pos, walking_sound)
    player.add(player_sprite)


    initial_zone = (5, 2)


    # At first the zone is loaded without the enemies, the nemies may be added later, or maybe I'll add them to the editor, but that may never happen.
    main_scene = SceneLoader.load_from_json(resource_path("data/scene_output.json"), WORLD_MAP_LEVEL, initial_zone, player_sprite, chase_sound, flee_sound)
    scene = main_scene

    while True:
        screen.fill('black')
        delta_time = clock.get_time()
        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_SPACE:
                    if game_state == "PLAYING":
                        player.sprite.attack()
                    elif game_state == "READING_NOTE":
                        if isinstance(note_to_show, str):
                            pygame.mixer.music.unpause()
                        note_to_show = None
                        game_state = "PLAYING"
                
                elif event.key == pygame.K_ESCAPE:
                    
                    if game_state == "PLAYER_DEAD":
                        return
                        
                    elif game_state == "READING_NOTE":
                        if isinstance(note_to_show, str):
                            pygame.mixer.music.unpause()
                        note_to_show = None
                        game_state = "PLAYING"                    
                
        # --- Game logic ---
        if game_state == "PLAYING":  
            player.update(scene.obstacles)
            scene.enemies.update(delta_time)

            if note_being_interacted:
                status = note_being_interacted.update()
                if status == "interaction_finished":
                    note_to_show = note_being_interacted.read()
                    game_state = "READING_NOTE"
                    note_being_interacted = None


                    if isinstance(note_to_show, str):
                        pygame.mixer.music.pause()
                        if screaming_sound:
                            screaming_sound.play()
            
            if player.sprite.is_attacking and not note_being_interacted:
                collided_interactables = pygame.sprite.spritecollide(
                    player.sprite,
                    scene.interactables,
                    False,
                    lambda sprite_a, sprite_b: sprite_b.collision_rect.colliderect(sprite_a.attack_rect)
                )

                if collided_interactables:
                    note_obj = collided_interactables[0]
                    if not note_obj.interacted_once:
                        interaction_status = note_obj.interact()
                        if interaction_status == "interaction_started":
                            if note_interact_sound:
                                note_interact_sound.play()
                            note_being_interacted = note_obj
                            player.sprite.cancel_attack()
                else:
                    for enemy in scene.enemies:
                        if enemy.collision_rect.colliderect(player.sprite.attack_rect):
                            if hasattr(enemy, 'while_attacked'):
                                enemy.while_attacked()

            for enemy in scene.enemies:
                if enemy.collides_with(player.sprite):
                    player.sprite.defeat() 
                    # if hasattr(enemy, 'behaviours') and hasattr(enemy.behaviours, 'shoo'):
                    #     enemy.behaviours.shoo(enemy)

                    pygame.mixer.music.stop()
                    chase_sound.set_volume(0)
                    if death_sound:
                        death_sound.play()

                    game_state = "PLAYER_DEAD"
                    break



            if current_zone not in zone_event_triggered:
                all_notes_in_zone = []
                read_notes_count = 0

                if current_zone in scene._interactables_dict:
                    for obj in scene._interactables_dict[current_zone]:
                        if isinstance(obj, Note):
                            all_notes_in_zone.append(obj)
                            if obj.interacted_once:
                                read_notes_count += 1     

                if len(all_notes_in_zone) > 0 and len(all_notes_in_zone) == read_notes_count:
                    if scene.unhide_object_by_class(Image):
                        note_interact_sound.set_volume(0.3)
                        secret_revealed.play()
                        note_interact_sound.set_volume(1)
                        pass   
                    
                    zone_event_triggered.add(current_zone)

            
            scene.draw(screen, player)

            # --- Collisions (this type of collisions do not change the game_active e.g. (an enemy attacking you)) ---
            # ---------- THIS WAS BEFORE UPDATING THE PLAYER CLASS, NOW PLAYER COLLISIONS ARE HANDLED BY THE PLAYER -------------
            # collided_obstacles = pygame.sprite.spritecollide(player.sprite, scene._obstacles, False, lambda sprite_a, sprite_b: sprite_b.collides_with(sprite_a))

            # --- Debugging Collisions ---s
            # pygame.draw.rect(screen, 'red', player.sprite.rect, 2)
            # pygame.draw.rect(screen, 'yellow', player.sprite.collision_rect, 2)
            # pygame.draw.rect(screen, 'green', player.sprite.attack_rect, 2)
            # for sprite in scene.enemies:
            #     if (sprite.collides_with(player.sprite)):
            #         print("collision")
            #     pygame.draw.rect(screen, 'green', sprite.collision_rect, 2)
            # pygame.draw.rect(screen, 'red', player.sprite.rect, 2)
            # pygame.draw.rect(screen, 'yellow', player.sprite.collision_rect, 2)
            # for sprite in scene.obstacles:
            #     if isinstance(sprite, Wall):
            #         pygame.draw.rect(screen, 'pink', sprite.collision_rect, 2)
            # for sprite in scene.obstacles:
            #     if isinstance(sprite, Tree):
            #         pygame.draw.rect(screen, 'blue', sprite.collision_rect, 2)
            # for sprite in scene.obstacles:
            #     if isinstance(sprite, Rock):
            #         pygame.draw.rect(screen, 'green', sprite.collision_rect, 2)
            # for sprite in scene.obstacles:
            #     if isinstance(sprite, SchoolBuilding):
            #         pygame.draw.rect(screen, 'green', sprite.collision_rect, 2)


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
        

        elif game_state == "PLAYER_DEAD":
            # player.update(scene.obstacles)
            # scene.enemies.update(delta_time)
            # scene.draw(screen, player)
            # draw_defeat_text(screen)
            scene.draw(screen, player)
            draw_game_over_screen(screen, game_over_image)

        elif game_state == "READING_NOTE":
            if isinstance(note_to_show, list):
                draw_note_ui(screen, note_to_show)
            elif isinstance(note_to_show, str):
                draw_image_ui(screen, note_to_show)


        pygame.display.flip()
        clock.tick(FPS)

def main():
    """
    The master loop calls game_loop() repeatedly
    """
    print("hola")
    while True:
        game_loop()

if __name__ == "__main__":
    main()