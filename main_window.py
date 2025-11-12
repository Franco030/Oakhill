import pygame
from sys import exit
from src.Game_Constants import *
from src.Obstacles import *
from src.Player import Player
from src.Scene_Loader import SceneLoader


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

    font_path = "assets/fonts/scary_font.ttf"
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

def main():
    player_x_pos = 600
    player_y_pos = 300
    

    y_cord, x_cord = 5, 2
    current_zone = (y_cord, x_cord)

    game_active = True
    note_to_show = None

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED | pygame.RESIZABLE | pygame.DOUBLEBUF, vsync=1)
    pygame.display.set_caption('Oakhill')
    clock = pygame.time.Clock()


    # world_map_level = [
    #     [0, 0, 1, 1, 1, 1], 
    #     [0, 1, 1, 0, 0, 0], 
    #     [0, 1, 0, 0, 0, 0], 
    #     [0, 1, 1, 0, 0, 0],
    #     [0, 0, 1, 1, 0, 0],
    #     [0, 0, 1, 1, 0, 0]  
    # ]


    player = pygame.sprite.GroupSingle()
    player_sprite = Player(player_x_pos, player_y_pos)
    player.add(player_sprite)


    initial_zone = (5, 2)


    # At first the zone is loaded without the enemies, the nemies may be added later, or maybe I'll add them to the editor, but that may never happen.
    main_scene = SceneLoader.load_from_json("data/scene_output.json", WORLD_MAP_LEVEL, initial_zone, player_sprite)
    scene = main_scene

    while True:
        screen.fill('black')
        delta_time = clock.get_time()
        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            

            if not game_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if note_to_show:
                            note_to_show = None
                            game_active = True
                        else:
                            player.sprite.collision_rect.center = (player_x_pos, player_y_pos)
                            player.sprite.pos = pygame.math.Vector2(player.sprite.collision_rect.center)
                            game_active = True
                    if event.key == pygame.K_SPACE and note_to_show:
                        note_to_show = None
                        game_active = True
                    
                    

        # --- Collisions (this type of collisions may change the game_active e.g. (an enemy attacking you))---
        # if pygame.sprite.spritecollide(player.sprite, scene.enemies, False, lambda sprite_a, sprite_b: sprite_b.collides_with(sprite_a))
        #     game_active = False
        for enemy in scene.enemies:
            if enemy.collides_with(player.sprite):
                game_active = False

        # --- Game logic ---
        if game_active:  
            # print(current_zone)
            scene.draw(screen, player)
            player.update(scene.obstacles)

            for enemy in scene.enemies:
                enemy.update(delta_time)
                screen.blit(enemy.image, enemy.rect)
            
            if player.sprite.is_attacking:
                collided_interactables = pygame.sprite.spritecollide(
                    player.sprite,
                    scene.interactables,
                    False,
                    lambda sprite_a, sprite_b: sprite_b.collision_rect.colliderect(sprite_a.attack_rect)
                )

                if collided_interactables:
                    note_obj = collided_interactables[0]
                    note_content = note_obj.interact()

                    if note_content:
                        note_to_show = note_content
                        game_active = False
                        player.sprite.cancel_attack()
                else:
                    for enemy in scene.enemies:
                        if enemy.collision_rect.colliderect(player.sprite.attack_rect):
                            if hasattr(enemy, 'while_attacked'):
                                enemy.while_attacked()


            # --- Collisions (this type of collisions do not change the game_active e.g. (an enemy attacking you)) ---
            # ---------- THIS WAS BEFORE UPDATING THE PLAYER CLASS, NOW PLAYER COLLISIONS ARE HANDLED BY THE PLAYER -------------
            # collided_obstacles = pygame.sprite.spritecollide(player.sprite, scene._obstacles, False, lambda sprite_a, sprite_b: sprite_b.collides_with(sprite_a))


            # --- Debugging Collisions ---s
            pygame.draw.rect(screen, 'red', player.sprite.rect, 2)
            pygame.draw.rect(screen, 'yellow', player.sprite.collision_rect, 2)
            pygame.draw.rect(screen, 'green', player.sprite.attack_rect, 2)
            for sprite in scene.enemies:
                if (sprite.collides_with(player.sprite)):
                    print("collision")
                pygame.draw.rect(screen, 'green', sprite.collision_rect, 2)
            pygame.draw.rect(screen, 'red', player.sprite.rect, 2)
            pygame.draw.rect(screen, 'yellow', player.sprite.collision_rect, 2)
            # for sprite in scene.obstacles:
            #     if isinstance(sprite, Wall):
            #         pygame.draw.rect(screen, 'pink', sprite.collision_rect, 2)
            # for sprite in scene.obstacles:
            #     if isinstance(sprite, Tree):
            #         pygame.draw.rect(screen, 'blue', sprite.collision_rect, 2)
            # for sprite in scene.obstacles:
            #     if isinstance(sprite, Rock):
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
        

        else:
            if note_to_show:
                draw_note_ui(screen, note_to_show)
            else:
                screen.fill('orange')
                font = pygame.font.Font(None, 50)
                text_surface = font.render('You were hit by an enemy! Press ESC to Restart', True, 'black')
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(text_surface, text_rect)


        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()