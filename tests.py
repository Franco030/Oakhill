import pygame
import json
from src.Obstacles import *
from src.Game_Constants import SCREEN_WIDTH, SCREEN_HEIGHT

pygame.init()

# Constants
FPS = 60
GRID_SIZE = 40

# World map defining accessible zones
world_map_level = [
    [0, 0, 1, 1, 1, 1], 
    [0, 1, 1, 0, 0, 0], 
    [0, 1, 0, 0, 0, 0], 
    [0, 1, 1, 0, 0, 0],
    [0, 0, 1, 1, 0, 0],
    [0, 0, 1, 0, 0, 0]  
]

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Level Editor")
clock = pygame.time.Clock()

# Obstacle preview state
obstacle_types = {
    'Tree': [Tree],
    'Rock': [Rock],
    'Wall': [Wall]
}

tree_indexes = range(len(Tree.images))
rock_indexes = range(len(Rock.images))
wall_indexes = range(len(Wall.images))

current_type = 'Tree'
current_index = 0
current_zone = (5, 2)
zones_data = {}
font = pygame.font.SysFont(None, 24)

def create_obstacle(obj):
    if obj["type"] == "Tree":
        return Tree(obj["x"], obj["y"], obj.get("index", 0))
    elif obj["type"] == "Rock":
        return Rock(obj["x"], obj["y"], obj.get("index", 0))
    elif obj["type"] == "Wall":
        return Wall(obj["x"], obj["y"], obj.get("index", 0))

def is_zone_accessible(y, x):
    try:
        return world_map_level[y][x] == 1
    except IndexError:
        return False

running = True
while running:
    screen.fill((50, 50, 50))

    # Draw grid
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, (100, 100, 100), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, (100, 100, 100), (0, y), (SCREEN_WIDTH, y))

    # UI Text
    text = font.render(f"Zone: {current_zone} | Selected: {current_type} (Index {current_index}) | Press 1-Tree 2-Rock 3-Wall | [ and ] to change index | Arrows to change zone | S to Save | L to Load | Right-click to delete", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    # Draw placed obstacles
    placed_obstacles = zones_data.get(current_zone, [])
    for obj in placed_obstacles:
        screen.blit(obj.image, obj.rect)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                current_type = 'Tree'
                current_index = 0
            elif event.key == pygame.K_2:
                current_type = 'Rock'
                current_index = 0
            elif event.key == pygame.K_3:
                current_type = 'Wall'
                current_index = 0
            elif event.key == pygame.K_LEFTBRACKET:
                current_index = max(0, current_index - 1)
            elif event.key == pygame.K_RIGHTBRACKET:
                current_index += 1

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
                        if isinstance(obj, Tree):
                            obj_list.append({"type": "Tree", "x": obj.rect.centerx, "y": obj.rect.centery, "index": obj.index})
                        elif isinstance(obj, Rock):
                            obj_list.append({"type": "Rock", "x": obj.rect.centerx, "y": obj.rect.centery, "index": obj.index})
                        elif isinstance(obj, Wall):
                            obj_list.append({"type": "Wall", "x": obj.rect.centerx, "y": obj.rect.centery, "index": obj.index})
                    json_data[str(zone)] = obj_list
                with open("scene_output.json", "w") as f:
                    json.dump({"zones": json_data}, f, indent=4)
                print("Saved to scene_output.json")

            elif event.key == pygame.K_l:
                try:
                    with open("scene_output.json", "r") as f:
                        loaded = json.load(f)
                        zones_data = {}
                        for zone_str, obj_list in loaded.get("zones", {}).items():
                            zone_tuple = eval(zone_str)
                            zones_data[zone_tuple] = [create_obstacle(obj) for obj in obj_list]
                    print("Loaded scene_output.json")
                except Exception as e:
                    print("Error loading file:", e)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            grid_x = (mx // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2
            grid_y = (my // GRID_SIZE) * GRID_SIZE + GRID_SIZE // 2

            if event.button == 1:
                index = current_index
                new_obj = None
                if current_type == 'Tree':
                    index = index % len(tree_indexes)
                    new_obj = Tree(grid_x, grid_y, index)
                    new_obj.index = index
                elif current_type == 'Rock':
                    index = index % len(rock_indexes)
                    new_obj = Rock(grid_x, grid_y, index)
                    new_obj.index = index
                elif current_type == 'Wall':
                    index = index % len(wall_indexes)
                    new_obj = Wall(grid_x, grid_y, index)
                    new_obj.index = index

                zones_data.setdefault(current_zone, []).append(new_obj)

            elif event.button == 3:
                for obj in zones_data.get(current_zone, [])[::-1]:
                    if obj.rect.collidepoint(mx, my):
                        zones_data[current_zone].remove(obj)
                        break

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()