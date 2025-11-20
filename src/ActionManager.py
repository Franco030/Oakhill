import pygame
from src.GameState import game_state

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

        if action_type == "SetFlag":
            key = params.get("flag")
            val = params.get("value")
            if key: game_state.set_flag(key, val)

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

        elif action_type == "IncrementFlag":
            key = params.get("flag")
            amount = params.get("value", 1) # By default it adds up one
            if key:
                game_state.increment_flag(key, amount)
                print(f"Flag {key} incremented. New value: {game_state.get_flag(key)}")

        elif action_type == "PlaySound":
            sound_name = params.get("sound")
            if sound_name in self.sound_library:
                self.sound_library[sound_name].play()
                print(f"Playing sound: {sound_name}")
            else:
                print(f"Error: Sound '{sound_name}' not found in library")

        elif action_type == "UnhideObject":
            target_id = params.get("id")
            sound_name = params.get("sound", "secret")
            if target_id:
                scene.unhide_object_by_id(target_id)

                if sound_name != "silent" and sound_name in self.sound_library:
                    self.sound_library[sound_name].play()
                    print(f"Playing sound: {sound_name} because of UnhideObject")
                

        elif action_type == "ShowDialogue":
            msg = params.get("msg", "...")
            print(f"Dialogue: {msg}")