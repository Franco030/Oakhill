import pygame
from sys import exit
from src.Game_Constants import *
from src.Obstacles import *
from src.Player import Player
from src.Scene_Loader import SceneLoader

def main():
    player_x_pos = 600
    player_y_pos = 300
    

    y_cord, x_cord = 5, 2
    current_zone = (y_cord, x_cord)

    game_active = True

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
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:   
                    # player.sprite.rect.center = (0, 0) ----> the player.sprite.pos manages this rectangle
                    player.sprite.collision_rect.center = (player_x_pos, player_y_pos)
                    player.sprite.pos = pygame.math.Vector2(player.sprite.collision_rect.center)
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
                if enemy.collision_rect.colliderect(player.sprite.attack_rect):
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
            # What happens if you "lose" - Intro - etcetera
            screen.fill('orange')
            font = pygame.font.Font(None, 50)
            text_surface = font.render('You were hit by an enemy! Press ESC to Restart', True, 'black')
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(text_surface, text_rect)
            pass


        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()