from src.GameState import game_state
from src.Game_Constants import MAPS, LEVEL_MUSIC, LEVEL_DARKNESS
from utils import resource_path
from src.ResourceManager import ResourceManager
from src.Game_Enums import Actions
import pygame

class ActionManager:
    def __init__(self, sound_library=None):
        self.sound_library = sound_library if sound_library else {}

    def parse_params(self, param_string):
        params = {}
        if not param_string: return params
        
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
                    except: pass
                params[key] = value
        return params

    def parse_params(self, param_string):
        params = {}
        if not param_string: return params
        
        clean_string = param_string.replace('\n', ';').replace('\r', '')
        
        pairs = clean_string.split(';')
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                value = value.replace('\\n', '\n') 

                if value.lower() == 'true': value = True
                elif value.lower() == 'false': value = False
                else:
                    try: value = int(value)
                    except: pass 
                
                params[key] = value
        return params

    def execute(self, action_type, param_string, player, scene):
        print(f"[ACTION] {action_type} -> {param_string}")
        params = self.parse_params(param_string)

        sound_name = params.get("sound")
        if sound_name and sound_name != "silent":
            if sound_name in self.sound_library:
                self.sound_library[sound_name].play()
            else:
                print(f"Sound '{sound_name}' not found.")


        if action_type == "SetFlag":
            key = params.get("flag")
            val = params.get("value")
            if key: game_state.set_flag(key, val)
            
        elif action_type == "IncrementFlag":
            key = params.get("flag")
            amount = params.get("value", 1)
            if key: game_state.increment_flag(key, amount)

        elif action_type == "Teleport":
            zone_str = str(params.get("zone"))
            x = params.get("x")
            y = params.get("y")
            
            if x is not None and y is not None:
                game_state.request_teleport(zone_str, x, y)
                print(f"[ActionManager] Teleport requested to {zone_str} at ({x}, {y})")

        elif action_type == "PlaySound":
            sound_name = params.get("sound")
            sound_volume = float(params.get("volume", 1.0))
            if sound_name in self.sound_library:

                self.sound_library[sound_name].set_volume(sound_volume)
                self.sound_library[sound_name].play()
                print(f"Playing sound: {sound_name}")
            else:
                print(f"Error: Sound '{sound_name}' not found in library")
            
        elif action_type == "UnhideObject":
            tid = params.get("id")
            sound_name = params.get("sound", "secret")
            if tid: 
                scene.unhide_object_by_id(tid)
                if sound_name != "silent" and sound_name in self.sound_library:
                    self.sound_library[sound_name].play()

        elif action_type == "ChangeLevel":
            level_name = params.get("level")
            json_file = params.get("json")
            zone_str = str(params.get("zone"))
            x = params.get("x")
            y = params.get("y")
            
            if level_name in MAPS and json_file:
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

        elif action_type == "ShowNote":
            text_content = params.get("text", "")
            return {
                "type": "Note",
                "data": text_content,
                "sound": params.get("sound")
            }
        
        elif action_type == Actions.SHOW_DIALOGUE:
            text = params.get("text", "...")
            
            color_str = str(params.get("color", "255,255,255"))
            
            try:
                text_color = tuple(map(int, color_str.split(',')))
            except:
                print(f"Error parsing color: {color_str}, using white.")
                text_color = (255, 255, 255)

            return {
                "type": "Dialogue",
                "data": {
                    "text": text,
                    "color": text_color
                },
                "sound": params.get("sound"),
                "pause_music": params.get("pause_music", False)
            }
        
        elif action_type == "ShowImage":
            path = params.get("image") or params.get("path")
            return {
                "type": "Image",
                "data": path,
                "sound": params.get("sound"),
                "pause_music": params.get("pause_music", False)
            }
        
        elif action_type == "CloseImage":
            pass

        elif action_type == "ShowAnimation":
            base_path = params.get("path")
            frames = int(params.get("frames", 1))
            speed = float(params.get("speed", 0.1))
            loop = params.get("loop", True)

            image_list = []
            if base_path:
                clean_base = base_path.replace(".png", "")
                for i in range(frames):
                    image_list.append(f"{clean_base}_{i}.png")
                
            return {
                "type": "Animation",
                "data": image_list,
                "speed": speed,
                "loop": loop,
                "sound": params.get("sound"),
                "pause_music": params.get("pause_music", False)
            }
        
        elif action_type == "ChangeMusic":
            # This action needs the path and not the key because of the way pygame manages music and sounds
            music_path = params.get("path") or params.get("music")
            fade_ms = int(params.get("fade", 500))
            volume = float(params.get("volume", 0.6))
            loop_count = int(params.get("loop", -1))

            if music_path:
                ResourceManager.play_music(music_path, volume, loop_count, fade_ms)
        
        return None