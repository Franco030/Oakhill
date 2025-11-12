import json
from .Obstacles import *
from .Scene import Scene
from .Enemies import *
from .Behaviour import *
from .Interactable import _Interactable
from .Asset_Config import OBSTACLE_CONFIG


class SceneLoader:
    @staticmethod
    def load_from_json(path: str, map_level: list, initial_zone: tuple, player) -> Scene:
        with open(path, 'r') as f:
            data = json.load(f)

        zone_data = data.get("zones", {})
        zone_obstacles = {}
        zone_interactables = {}

        for zone_str, objects in zone_data.items():
            zone = eval(zone_str)
            obstacle_list = []
            interactable_list = []

            for obj in objects:
                obstacle_type = obj["type"]
                # cls = OBSTACLE_CONFIG.get(obstacle_type)['class']
                # if cls:
                #     x, y = obj["x"], obj["y"]
                #     index = obj.get("index", 0)
                #     obstacle = cls(x, y, index)
                #     obstacle.index = index
                #     obstacle_list.append(obstacle)
                config_entry = OBSTACLE_CONFIG.get(obstacle_type)
                if config_entry:
                    cls = config_entry['class']
                    x, y = obj["x"], obj["y"]
                    index = obj.get("index", 0)
                    obstacle = cls(x, y, index)
                    obstacle.index = index

                    if isinstance(obstacle, _Interactable):
                        interactable_list.append(obstacle)
                    else:
                        obstacle_list.append(obstacle)
                

            zone_obstacles[zone] = obstacle_list
            zone_interactables[zone] = interactable_list

        enemy_dict_placeholder = {
            (5, 2): [Stalker_Ghost(500, 500, 100, StalkerBehaviour(player, speed=150, min_wait=5.0, max_wait=15.0, stop_distance=50))],
        }

        return Scene(initial_zone, zone_obstacles, zone_interactables, enemy_dict_placeholder, map_level)
