import pygame
from .Interactable import Interactable
from .GameState import game_state

class Scene:
    """
    Manages the objects and state of the current game "scene" or zone
    The same Scene object is going to be used to represent the "open world", what diferentiates one scene from another is its location
    You may need to make a new Scene object if you "enter a house", because the house will have a different scenario, different object, different events, etc.
    """
    def __init__(self, initial_location: tuple, obstacles: dict, interactables: dict, triggers: dict, enemies: dict, map_level, global_enemies=None, music_path=None, has_darkness=False):
        """
        Description: Initializes the scene
        Parameters:
            initial_locaiton (tuple): A tuple (x, y) representing the starting zone in the map_level.
            obstacles (dict): A dictionary where keys are zone coordinates and values are a list of _Obstacle objects in the zone
            enemies (dict): A dictionary where keys are zone coordinates and values are a lis of _Enemy objects in the zone
            map_level: The 2D array representing the game map, indicating traversable zones.
        Functionality:
            Initializes _obstacles which is a list of all obstacles in the scene, it will be used to load and draw the obstacles in different locations
            Initializes _interactables which is a kind of obstacles that is interactable e.g. (a door, a tree that has apples in it, a trapdoor, etc.)
        """
        self.location = initial_location
        self.has_darkness = has_darkness

        self.obstacles_dict = obstacles
        self._interactables_dict = interactables
        self._triggers_dict = triggers
        self.enemies_dict = enemies
        self.global_enemies = global_enemies if global_enemies else []
        
        self.music_path = music_path
        self.darkness = has_darkness
        self.map_level = map_level

        self._obstacles = pygame.sprite.Group()
        self._interactables = pygame.sprite.Group()
        self._triggers = pygame.sprite.Group()
        self._enemies = pygame.sprite.Group()

        self._load_obstacles_for_current_location()
        self._load_enemies_for_current_location()

    def check_zone(self, cords: tuple):
        """
        Checks if a given zone coordinate (y, x) is accesible on the map_level
        """
        try:
            return self.map_level[cords[0]][cords[1]] == 1
        except IndexError:
            return False
        
    @property
    def obstacles(self):
        return self._obstacles
    
    @property
    def interactables(self):
        return self._interactables
    
    @property
    def enemies(self):
        return self._enemies
        
    def _load_obstacles_for_current_location(self):
        """
        Cleans and reloads the group of sprites in every self.location
        """
        self._obstacles.empty()
        self._interactables.empty()
        self._triggers.empty()

        if self.location in self.obstacles_dict:
            self._obstacles.add(self.obstacles_dict[self.location])

        if self.location in self._interactables_dict:
            for obj in self._interactables_dict[self.location]:
                is_hidden = getattr(obj, 'is_hidden', False)
                
                should_show = not is_hidden and (not obj.interacted_once or obj.used_image)
                if should_show:
                    if isinstance(obj, Interactable):
                         self._interactables.add(obj)
                    
                    self._obstacles.add(obj)

        if self.location in self._triggers_dict:
            for trig in self._triggers_dict[self.location]:
                if trig.id and game_state.has_interacted(trig.id):
                    continue
                self._triggers.add(trig)

    def _load_enemies_for_current_location(self):
        self._enemies.empty()

        if self.location in self.enemies_dict:
            for enemy in self.enemies_dict[self.location]:
                self._enemies.add(enemy)
        
        for genemy in self.global_enemies:
            self._enemies.add(genemy)
    
    def set_location(self, new_location: tuple):
        """
        Changes the current's scene location and reloads the appropriate obstacles
        """
        if self.location != new_location:
            self.location = new_location
            self._load_obstacles_for_current_location()

    def unhide_object_by_id(self, target_id):
        """
        Searches for an object by id, ignoring spaces and checking all lists
        """
        print(f"[SCENE] Searching hidden object with id: '{target_id}'")
        clean_target = str(target_id).replace(" ", "")

        def search_and_reveal(object_list, destination_group):
            for obj in object_list:
                obj_id = getattr(obj, 'id', "")
                clean_obj_id = str(obj_id).replace(" ", "")
                
                if clean_obj_id == clean_target:
                    obj.unhide()
                    destination_group.add(obj)
                    
                    if not getattr(obj, 'is_passable', False):
                        self._obstacles.add(obj)
                        
                    print(f"[SCENE] Object '{obj_id}' revealed.")
                    return True
            return False

        if self.location in self._interactables_dict:
            if search_and_reveal(self._interactables_dict[self.location], self._interactables):
                return

        if self.location in self.obstacles_dict:
            if search_and_reveal(self.obstacles_dict[self.location], self._obstacles):
                return
            
        print(f"[SCENE] ERROR: No object id found similiar to '{target_id}' in {self.location}")

    def hide_object_by_id(self, target_id):
        print(f"[SCENE] Hiding object with id: '{target_id}'")
        clean_target = str(target_id).replace(" ", "")


        all_sprites = list(self._obstacles) + list(self._interactables) + list(self._triggers)
        
        found = False
        for obj in all_sprites:
            obj_id = getattr(obj, 'id', "")
            clean_obj_id = str(obj_id).replace(" ", "")
            
            if clean_obj_id == clean_target:
                if hasattr(obj, 'hide'):
                    obj.hide()
                
                obj.kill()
                found = True
        
        if not found:
            print(f"[SCENE] Warning: Object '{target_id}' not found to hide.")
            
    def unhide_object_by_interaction_type(self, interaction_type_to_unhide: str):
        """
        DEPRECATED NO LONGER IN USE
        """
        if self.location not in self._interactables_dict:
            return False
        
        found_and_unhidden = False

        for obj in self._interactables_dict[self.location]:
            if getattr(obj, 'interaction_type', None) == interaction_type_to_unhide and getattr(obj, 'is_hidden', False):
                obj.unhide()
                
                self._interactables.add(obj)
                self._obstacles.add(obj)
                
                found_and_unhidden = True
                print(f"Secret revealed. type {interaction_type_to_unhide} appeared")

        return found_and_unhidden
    
    def cleanup(self):
        for enemy in self._enemies:
            enemy.reset_state()

    def draw(self, screen, player):
        render_list = []

        for sprite in self._obstacles:
            render_list.append(sprite)
        
        for sprite in self._interactables:
            if sprite not in self._obstacles:
                render_list.append(sprite)


        render_list.append(player)

        for enemy in self._enemies:
            render_list.append(enemy)

        def sort_key(sprite):
            if sprite in self._enemies:
                layer_priority = 2
            elif getattr(sprite, 'is_ground', False):
                layer_priority = 0
            else:
                layer_priority = 1

            z = getattr(sprite, 'z_index', 0)
            
            y_depth = 0
            if hasattr(sprite, 'collision_rect'):
                 y_depth = sprite.collision_rect.bottom
            elif hasattr(sprite, 'rect'):
                 y_depth = sprite.rect.bottom
            
            return (layer_priority, z, y_depth)

        render_list.sort(key=sort_key)


        for sprite in render_list:
            screen.blit(sprite.image, sprite.rect)
                
    def change_zone(self, new_zone_tuple):
        self.location = new_zone_tuple
        self._load_obstacles_for_current_location()
        self._load_enemies_for_current_location()

    def change_zone_by_string(self, zone_str):
        try:
            clean = zone_str.replace("(", "").replace(")", "")
            parts = clean.split(",")
            new_loc = (int(parts[0]), int(parts[1]))
            self.change_zone(new_loc)
        except Exception as e:
            print(f"Error changing zone to {zone_str}: {e}")