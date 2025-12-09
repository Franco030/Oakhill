import pygame
from .Interactable import Interactable
from .Trigger import Trigger
from .ResourceManager import resource_manager
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

        self.active_slides = []
        
        self.music_path = music_path
        self.darkness = has_darkness
        self.map_level = map_level

        self._obstacles = pygame.sprite.Group()
        self._interactables = pygame.sprite.Group()
        self._triggers = pygame.sprite.Group()
        self._enemies = pygame.sprite.Group()

        self._id_map = {}

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
    
    def _register_object_id(self, obj):
        if hasattr(obj, 'id') and obj.id:
            clean_id = str(obj.id).replace(" ", "")
            self._id_map[clean_id] = obj

    # I didn't change the name but a more correct name is:
    # _load_objects_for_current_location
    def _load_obstacles_for_current_location(self):
        """
        Cleans and reloads the group of sprites in every self.location
        """
        self._obstacles.empty()
        self._interactables.empty()
        self._triggers.empty()
        self._id_map.clear()

        if self.location in self.obstacles_dict:
            current_obs = self.obstacles_dict[self.location]
            for obj in current_obs: 
                self._register_object_id(obj)
                if obj.is_hidden:
                    if not game_state.has_interacted(obj.id):
                        continue
                self._obstacles.add(obj)

                    


        if self.location in self._interactables_dict:
            current_ints = self._interactables_dict[self.location]
            for obj in current_ints:
                self._register_object_id(obj)
                is_hidden = getattr(obj, 'is_hidden', False)

                
                should_show = not is_hidden and (not obj.interacted_once or obj.used_image)
                if should_show:
                    if isinstance(obj, Interactable):
                         self._interactables.add(obj)
                    
                    self._obstacles.add(obj)

        if self.location in self._triggers_dict:
            current_trigs = self._triggers_dict[self.location]
            for trig in current_trigs:
                self._register_object_id(obj)
                if trig.id and game_state.has_interacted(trig.id) or trig.is_hidden:
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
        clean_target = str(target_id).replace(" ", "")
        obj = self._id_map.get(clean_target)

        if obj:
            print(f"[SCENE] Object '{target_id}' found in map. Revealing...")
            obj.unhide()
            
            if isinstance(obj, Interactable):
                self._interactables.add(obj)
            
            if not getattr(obj, 'is_passable', False) and not isinstance(obj, Trigger):
                self._obstacles.add(obj)
                
            if isinstance(obj, Trigger):
                self._triggers.add(obj)

            return
            
        print(f"[SCENE] ERROR: No object id found similar to '{target_id}' in {self.location}")

    def hide_object_by_id(self, target_id):
        clean_target = str(target_id).replace(" ", "")
        obj = self._id_map.get(clean_target)

        if obj:
            print(f"[SCENE] Hiding object with id: '{target_id}'")
            if hasattr(obj, 'hide'):
                obj.hide()
            
            obj.kill()
        else:
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
                # Enemies are always on top
                layer_priority = 2
            elif getattr(sprite, 'is_ground', False):
                # Gound is always at the bottom
                layer_priority = 0
            else:
                layer_priority = 1

            z = getattr(sprite, 'z_index', 0)
            
            y_depth = 0
            if hasattr(sprite, 'collision_rect'):
                 y_depth = sprite.collision_rect.bottom
            elif hasattr(sprite, 'rect'):
                 y_depth = sprite.rect.bottom

            if hasattr(sprite, 'sort_offset_y'):
                y_depth += sprite.sort_offset_y
            
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


    def get_object_by_id(self, target_id):
        clean_target = str(target_id).replace(" ", "")
        return self._id_map.get(clean_target)
    
    def modify_object_by_id(self, target_id, new_properties):
        """
        Powerful function that modifies an object
        I'll use it carefully
        """
        obj = self.get_object_by_id(target_id)
        if not obj: return

        if hasattr(obj, 'data') and isinstance(obj.data, dict):
            for key, value in new_properties.items():
                obj.data[key] = value

        for key, value in new_properties.items():
            if key in ["interaction_blocked", "is_passable", "z_index"]:
                setattr(obj, key, value)
            
            elif hasattr(obj, key):
                setattr(obj, key, value)

        if "image_path" in new_properties or "resize_factor" in new_properties:
            img_path = new_properties.get("image_path", getattr(obj, "image_path", "None"))
            factor = float(new_properties.get("resize_factor", getattr(obj, "resize_factor", 1.0)))
            
            new_img = resource_manager.get_image(img_path)
            if new_img:
                w = int(new_img.get_width() * factor)
                h = int(new_img.get_height() * factor)
                obj.image = pygame.transform.scale(new_img, (w, h))
                obj.original_image = obj.image.copy()
                
                old_center = obj.rect.center
                obj.rect = obj.image.get_rect(center=old_center)
                
                if hasattr(obj, 'width'): obj.width = w
                if hasattr(obj, 'height'): obj.height = h
                if hasattr(obj, 'data'):
                    obj.data['width'] = w
                    obj.data['height'] = h

        if "collision_rect_offset" in new_properties or "image_path" in new_properties:
            if hasattr(obj, 'collision_rect'):
                offset = new_properties.get("collision_rect_offset", getattr(obj, "collision_rect_offset", [0,0,0,0]))
                if isinstance(offset, list) and len(offset) >= 4:
                    obj.collision_rect.x = obj.rect.x + offset[0]
                    obj.collision_rect.y = obj.rect.y + offset[1]
                    obj.collision_rect.width = obj.rect.width + offset[2]
                    obj.collision_rect.height = obj.rect.height + offset[3]

        if "flash_image_path" in new_properties:
            path = new_properties["flash_image_path"]
            if path in ["None", "", None]:
                obj.flash_image = None
            else:
                factor = getattr(obj, "resize_factor", 1.0)
                raw_flash = resource_manager.get_image(path)
                if raw_flash:
                     w = int(raw_flash.get_width() * factor)
                     h = int(raw_flash.get_height() * factor)
                     obj.flash_image = pygame.transform.scale(raw_flash, (w, h))

        if "charge_sound_path" in new_properties:
            path = new_properties["charge_sound_path"]
            if path in ["None", "", None]:
                obj.charge_sound = None
            else:
                try:
                    import os
                    from utils import resource_path
                    full = resource_path(path)
                    if os.path.exists(full):
                        obj.charge_sound = pygame.mixer.Sound(full)
                except:
                    obj.charge_sound = None
        
        print(f"[Scene] Modified object '{target_id}'")
