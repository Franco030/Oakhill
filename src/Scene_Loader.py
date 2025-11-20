import json
from .Obstacles import _Obstacle
from .Scene import Scene
from .Enemies import *
from .Behaviour import *
from .Interactable import _Interactable
from .Trigger import Trigger

class SceneLoader:
    @staticmethod
    def load_from_json(path: str, map_level: list, initial_zone: tuple, player, chase_sound, flee_sound) -> Scene:
        with open(path, 'r') as f:
            data = json.load(f)

        zone_data = data.get("zones", {})
        zone_obstacles = {}
        zone_interactables = {}
        zone_triggers = {}

        for zone_str, objects_data_list in zone_data.items():
            zone = eval(zone_str)
            obstacle_list = []
            interactable_list = []
            trigger_list = []

            for obj_data in objects_data_list:
                obj_type = obj_data.get("type")

                if obj_type == "Obstacle":
                    obstacle = _Obstacle(obj_data)
                    obstacle_list.append(obstacle)
                elif obj_type == "Interactable":
                    interactable = _Interactable(obj_data)
                    interactable_list.append(interactable)
                elif obj_type == "Trigger":
                    trigger = Trigger(obj_data)
                    trigger_list.append(trigger)
                
            zone_obstacles[zone] = obstacle_list
            zone_interactables[zone] = interactable_list
            zone_triggers[zone] = trigger_list

            stalker = Stalker_Ghost(-200, -200, 100, StalkerBehaviour(player, speed=300, min_wait=20.0, max_wait=60.0, stop_distance=50, chase_sound=chase_sound, flee_sound=flee_sound))

            enemy_dict_placeholder = {}


        return Scene(initial_zone, zone_obstacles, zone_interactables, zone_triggers, enemy_dict_placeholder, map_level, global_enemies=[stalker])