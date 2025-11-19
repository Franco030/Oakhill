import pygame
from src.GameState import game_state

class ActionManager:
    def __init__(self, scene_manager=None):
        self.scene_manager = scene_manager

    def parse_params(self, param_string):
        """Convierte 'flag=test; value=true' en un diccionario."""
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

        elif action_type == "PlaySound":
            sound_name = params.get("sound")
            print(f"Reproduciendo sonido: {sound_name}")

        elif action_type == "UnhideObject":
            target_id = params.get("id")
            if target_id:
                scene.unhide_object_by_id(target_id)

        elif action_type == "ShowDialogue":
            msg = params.get("msg", "...")
            print(f"Diálogo: {msg}")