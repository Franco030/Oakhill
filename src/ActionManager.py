import pygame
from src.GameState import game_state
from src.Game_Constants import MAPS, LEVEL_MUSIC, LEVEL_DARKNESS
from utils import resource_path

class ActionManager:
    def __init__(self, scene_manager=None, sound_library=None):
        self.scene_manager = scene_manager
        self.sound_library = sound_library if sound_library else {}

    def parse_params(self, param_string):
        """
        Turns 'flag=text; value=true' into a set
        """
        params = {}
        if not param_string:
            return params
        
        pairs = param_string.split(';')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if value.lower() == 'true': value = True
                elif value.lower() == 'false': value = False
                else:
                    try: value = int(value)
                    except ValueError:
                        try: value = float(value)
                        except ValueError: pass
                
                params[key] = value
        return params

    def execute(self, action_type, param_string, player, scene):
        print(f"[ACTION] Executing {action_type} with {param_string}")
        params = self.parse_params(param_string)

        # --- Universal Sound System
        # This allows that EVERY actions (SetFlag, Teleport, etc.) has a Sound parameter
        # We just add "sound=sound_name" in the editor parameters
        sound_name = params.get("sound")
        if sound_name and sound_name != "silent":
            if sound_name in self.sound_library:
                self.sound_library[sound_name].play()
            else:
                print(f"Advertencia: Sonido '{sound_name}' no encontrado en librería.")

        # Sets a flag (variable) to a value (number, string, float, etc)
        # flag=variable; value=12 -> variable=12
        if action_type == "SetFlag":
            key = params.get("flag")
            val = params.get("value")
            if key: game_state.set_flag(key, val)

        # Teleports the player to the zone
        # zone=(0, 5) -> scene.change_zone(0, 5)
        elif action_type == "Teleport":
            zone_str = str(params.get("zone"))
            x = params.get("x")
            y = params.get("y")
            
            if zone_str:
                zone_clean = zone_str.replace("(", "").replace(")", "")
                try:
                    parts = zone_clean.split(",")
                    new_zone = (int(parts[0]), int(parts[1]))
                    
                    scene.change_zone(new_zone)
                    
                    if x is not None and y is not None:
                        player.sprite.rect.topleft = (x, y)
                        
                except Exception as e:
                    print(f"Error Teleport: {e}")

        # Increments the value of a flag by one. You may change the value of 'value', by 'value' is one.
        # flag=variable; value=2 -> variable = variable + 2
        # flag=variable -> variable = variable + 1
        elif action_type == "IncrementFlag":
            key = params.get("flag")
            amount = params.get("value", 1) # By default it adds up one
            if key:
                game_state.increment_flag(key, amount)
                print(f"Flag {key} incremented. New value: {game_state.get_flag(key)}")

        # Plays a sound
        # The value of the sound should be in the sound library
        # sound library is setted in main_window
        # sound=scream -> scream.play()
        elif action_type == "PlaySound":
            sound_name = params.get("sound")
            if sound_name in self.sound_library:
                self.sound_library[sound_name].play()
                print(f"Playing sound: {sound_name}")
            else:
                print(f"Error: Sound '{sound_name}' not found in library")

        # If any type of object initiates with the property 'starts_hidden' set to True
        # this action_type sets it to False, so it gets drawn
        # id=object_id; sound=secret -> scene.unhide_object_by_id(object_id) secret.play()
        elif action_type == "UnhideObject":
            target_id = params.get("id")
            # sound_name = params.get("sound", "secret")
            if target_id:
                scene.unhide_object_by_id(target_id)

                # if sound_name != "silent" and sound_name in self.sound_library:
                #     self.sound_library[sound_name].play()
                #     print(f"Playing sound: {sound_name} because of UnhideObject")


        # Changes the level (the map of the game)
        elif action_type == "ChangeLevel":
            # params: level=school; json=data/school_interior.json; zone=(4, 1) any (x, y pair that exists withing the school map); x=100; y=500

            level_name = params.get("level")
            json_file = params.get("json")
            zone_str = str(params.get("zone"))
            x = params.get("x")
            y = params.get("y")

            if level_name in MAPS and json_file:
                # Parse zone
                clean = zone_str.replace("(", "").replace(")", "")
                parts = clean.split(",")
                new_zone = (int(parts[0]), int(parts[1]))

                music = LEVEL_MUSIC.get(level_name)
                is_dark = LEVEL_DARKNESS.get(level_name, False)

                game_state.request_level_change(
                    json_path=resource_path(json_file),
                    map_matrix=MAPS[level_name],
                    entry_zone=new_zone,
                    player_pos=(x, y),
                    music_path=music,
                    darkness=is_dark
                )
                print(f"Requesting travel to level: {level_name}")
                
        # Placeholder
        elif action_type == "ShowDialogue":
            msg = params.get("msg", "...")
            print(f"Dialogue: {msg}")