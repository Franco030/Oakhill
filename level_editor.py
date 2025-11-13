import pygame
import json
from src.Obstacles import *
from src.Game_Constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WORLD_MAP_LEVEL
from src.Asset_Config import OBSTACLE_CONFIG
from src.Note_Content import ALL_NOTE_TEXTS
from src.Lore_Image_Content import ALL_LORE_IMAGES

pygame.init()

# Constants
GRID_SIZE = 20

# World map defining accessible zones (1 = accessible, 0 = blocked) and json_filename
# If we were to make a house and make a new scene there, these two variables will be updated
# world_map_level = [
#     [0, 0, 1, 1, 1, 1], 
#     [0, 1, 1, 0, 0, 0], 
#     [0, 1, 0, 0, 0, 0], 
#     [0, 1, 1, 0, 0, 0],
#     [0, 0, 1, 1, 0, 0],
#     [0, 0, 1, 1, 0, 0]  
# ]
json_filename = "data/scene_output.json"

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Level Editor")
clock = pygame.time.Clock()


# Just to make the GUI work for the first time
current_type = 'Tree'
current_index = 0
current_zone = (5, 2)
zones_data = {}
font = pygame.font.SysFont(None, 24)

grid_visible = True

# Helper to recreate object from dict
def create_obstacle(obj):
    cls = OBSTACLE_CONFIG[obj["type"]]["class"]
    obstacle = cls(obj["x"], obj["y"], obj.get("index", 0))
    obstacle.index = obj.get("index", 0)
    obstacle.type_name = obj["type"]
    return obstacle

def is_zone_accessible(y, x):
    try:
        return WORLD_MAP_LEVEL[y][x] == 1
    except IndexError:
        return False

running = True
while running:
    screen.fill((50, 50, 50))

    # Draw grid
    if grid_visible:
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(screen, (100, 100, 100), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, (100, 100, 100), (0, y), (SCREEN_WIDTH, y))

    # UI Text
    keybinds = " ".join([f"{i+1}-{name}" for i, name in enumerate(OBSTACLE_CONFIG)])
    note_text_preview = ""
    if current_type  == 'Note':
        if current_index < len(ALL_NOTE_TEXTS):
            note_text_preview = f" (\"{ALL_NOTE_TEXTS[current_index][0]}\"...)"
    lines = [
        f"Zone: {current_zone} | Selected: {current_type} (Index {current_index}){note_text_preview}",
        f"Press {keybinds} | [ and ] to change index | G to toggle grid | S to save | L to load",
        "Arrows to change zone | Right-click to delete"
    ]
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10 + i * 20))

    # Draw placed obstacles
    placed_obstacles = zones_data.get(current_zone, [])
    for obj in placed_obstacles:
        screen.blit(obj.image, obj.rect)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            for name, config in OBSTACLE_CONFIG.items():
                if event.key == config['key']:
                    current_type = name
                    current_index = 0

            if event.key == pygame.K_LEFTBRACKET:
                current_index = max(0, current_index - 1)
            elif event.key == pygame.K_RIGHTBRACKET:
                current_index += 1

                if current_type == 'Note':
                    if current_index >= len(ALL_NOTE_TEXTS):
                        current_index = len(ALL_NOTE_TEXTS) - 1
                elif current_type == 'Image':
                    if current_index >= len(ALL_LORE_IMAGES):
                        current_index = len(ALL_LORE_IMAGES)
                elif current_type in OBSTACLE_CONFIG:
                    obstacle = OBSTACLE_CONFIG[current_type]
                    if current_index >= len(obstacle['indexes']):
                        current_index = len(obstacle['indexes']) - 1


            elif event.key == pygame.K_g:
                grid_visible = not grid_visible

            elif event.key == pygame.K_UP:
                new_zone = (current_zone[0] - 1, current_zone[1])
                if is_zone_accessible(*new_zone):
                    current_zone = new_zone
            elif event.key == pygame.K_DOWN:
                new_zone = (current_zone[0] + 1, current_zone[1])
                if is_zone_accessible(*new_zone):
                    current_zone = new_zone
            elif event.key == pygame.K_LEFT:
                new_zone = (current_zone[0], current_zone[1] - 1)
                if is_zone_accessible(*new_zone):
                    current_zone = new_zone
            elif event.key == pygame.K_RIGHT:
                new_zone = (current_zone[0], current_zone[1] + 1)
                if is_zone_accessible(*new_zone):
                    current_zone = new_zone

            elif event.key == pygame.K_s:
                json_data = {}
                for zone, objs in zones_data.items():
                    obj_list = []
                    for obj in objs:
                        obj_list.append({
                            "type": obj.type_name,
                            "x": obj.rect.centerx,
                            "y": obj.rect.centery,
                            "index": obj.index
                        })
                    json_data[str(zone)] = obj_list
                with open(json_filename, "w") as f:
                    json.dump({"zones": json_data}, f, indent=4)
                print("Saved to ", json_filename)

            elif event.key == pygame.K_l:
                try:
                    with open(json_filename, "r") as f:
                        loaded = json.load(f)
                        zones_data = {}
                        for zone_str, obj_list in loaded.get("zones", {}).items():
                            zone_tuple = eval(zone_str)
                            zones_data[zone_tuple] = [create_obstacle(obj) for obj in obj_list]
                    print("Loaded ", json_filename)
                except Exception as e:
                    print("Error loading file:", e)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            grid_x = (mx // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
            grid_y = (my // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2

            if event.button == 1:
                config = OBSTACLE_CONFIG[current_type]
                cls = config['class']
                index_to_use = 0

                if current_type == 'Note':
                    index_to_use = current_index % len(ALL_NOTE_TEXTS)
                elif current_type == 'Image':
                    index_to_use = current_index % len(ALL_LORE_IMAGES)
                else:
                    indexes = config['indexes']
                    index_to_use = current_index % len(indexes)
                new_obj = cls(grid_x, grid_y, index_to_use)
                new_obj.index = index_to_use
                new_obj.type_name = current_type
                zones_data.setdefault(current_zone, []).append(new_obj)

            elif event.button == 3:
                for obj in zones_data.get(current_zone, [])[::-1]:
                    if obj.rect.collidepoint(mx, my):
                        zones_data[current_zone].remove(obj)
                        break


    # Draw preview of current obstacle at mouse position
    mx, my = pygame.mouse.get_pos()
    grid_x = (mx // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
    grid_y = (my // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2

    preview_cls = OBSTACLE_CONFIG[current_type]['class']
    index_preview = 0

    if current_type == 'Note':
        index_preview = current_index % len(ALL_NOTE_TEXTS)
    else:
        index_preview = current_index % len(OBSTACLE_CONFIG[current_type]['indexes'])

    preview_obj = preview_cls(grid_x, grid_y, index_preview)
    preview_obj.image.set_alpha(128)  # Make it semi-transparent
    screen.blit(preview_obj.image, preview_obj.rect)



    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
