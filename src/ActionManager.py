from src.GameState import game_state
from src.Game_Constants import MAPS, LEVEL_MUSIC, LEVEL_DARKNESS
from utils import resource_path
from src.ResourceManager import resource_manager
from src.TweenManager import tween_manager
from src.Game_Enums import Actions
import pygame
import random

class ActionManager:
    def __init__(self):
        pass

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

        sound_id = params.get("sound")
        if sound_id and sound_id != "silent":
            snd = resource_manager.get_sound(sound_id)
            if snd: snd.play()


        if action_type == Actions.SET_FLAG:
            key = params.get("flag")
            val = params.get("value")
            if key: game_state.set_flag(key, val)
            
        elif action_type == Actions.INCREMENT_FLAG:
            key = params.get("flag")
            amount = params.get("value", 1)
            if key: game_state.increment_flag(key, amount)

        elif action_type == Actions.TELEPORT:
            zone_str = str(params.get("zone"))
            x = params.get("x")
            y = params.get("y")
            
            if x is not None and y is not None:
                game_state.request_teleport(zone_str, x, y)
                print(f"[ActionManager] Teleport requested to {zone_str} at ({x}, {y})")

        elif action_type == Actions.PLAY_SOUND:
            sound_id = params.get("sound")
            sound_volume = float(params.get("volume", 1.0))
            if sound_id and sound_id != "silent":
                snd = resource_manager.get_sound(sound_id)
                if snd:
                    snd.set_volume(sound_volume) 
                    snd.play()
            
        elif action_type == Actions.UNHIDE_OBJECT:
            tid = params.get("id")
            if tid: 
                scene.unhide_object_by_id(tid)

        elif action_type == Actions.HIDE_OBJECT:
            tid = params.get("id")
            if tid:
                scene.hide_object_by_id(tid)

        elif action_type == Actions.MODIFY_LIGHT:
            enable = params.get("enable", False)
            scene.has_darkness = enable

        elif action_type == Actions.RANDOM_ACTION:
            chance = int(params.get("chance", 50))
            roll = random.randint(1, 100)

            if roll <= chance:
                print(f"[RandomAction] Success ({roll} <= {chance}). Executing sub-action")
                sub_action = params.get("action")
                return self.execute(sub_action, param_string, player, scene)

        elif action_type == Actions.CHANGE_LEVEL:
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

        elif action_type == Actions.SHOW_NOTE:
            text_content = params.get("text", "")
            return {
                "type": "Note",
                "data": text_content,
                "sound": params.get("sound")
            }
        
        elif action_type == Actions.SHOW_DIALOGUE:
            text = params.get("text", "...")
            color_str = str(params.get("color", "255,255,255"))
            should_pause = str(params.get("pause_music", "false")).lower() == "true"
            
            try:
                text_color = tuple(map(int, color_str.split(',')))
            except:
                print(f"Error parsing color: {color_str}, using white.")
                text_color = (255, 255, 255)

            if should_pause:
                pygame.mixer.music.pause()

            return {
                "type": "Dialogue",
                "data": {
                    "text": text,
                    "color": text_color
                },
                "sound": params.get("sound"),
                "pause_music": should_pause,
            }
        
        elif action_type == Actions.SHOW_IMAGE:
            path = params.get("image") or params.get("path")
            return {
                "type": "Image",
                "data": path,
                "sound": params.get("sound"),
                "pause_music": params.get("pause_music", False)
            }
        
        elif action_type == Actions.CLOSE_IMAGE:
            pass

        elif action_type == Actions.SHOW_ANIMATION:
            base_id = params.get("path")
            frames = int(params.get("frames", 1))
            speed = float(params.get("speed", 0.1))
            loop = params.get("loop", True)

            image_list = []
            if base_id:
                # Assuming that base_id is "anim_angel"
                for i in range(frames):
                    # Generates "anim_angel_0", "anim_angel_1", etc.
                    image_list.append(f"{base_id}_{i}")
                
            return {
                "type": "Animation",
                "data": image_list,
                "speed": speed,
                "loop": loop,
                "sound": params.get("sound"),
                "pause_music": params.get("pause_music", False)
            }
        
        elif action_type == Actions.CHANGE_MUSIC:
            # This action needs the path and not the key because of the way pygame manages music and sounds
            music_path = params.get("path") or params.get("music")
            fade_ms = int(params.get("fade", 500))
            volume = float(params.get("volume", 0.6))
            loop_count = int(params.get("loop", -1))

            if music_path:
                resource_manager.play_music(music_path, volume, loop_count, fade_ms)

        elif action_type == Actions.MOVE_OBJECT:
            tid = params.get("id")
            if tid:
                target_obj = scene.get_object_by_id(tid)

                if target_obj:
                    try:
                        tx = int(params.get("x", 0))
                        ty = int(params.get("y", 0))
                        is_rel = str(params.get("relative", "false")).lower() == "true"
                
                        tween_manager.teleport(target_obj, tx, ty, relative=is_rel)
                        
                    except ValueError:
                        print(f"[ActionManager] Error params for MoveObject")
                else:
                    print(f"[ActionManager] Object '{tid}' not found for MoveObject.")

        elif action_type == Actions.SLIDE_OBJECT:
            tid = params.get("id")
            if tid:
                target_obj = scene.get_object_by_id(tid)
                if target_obj:
                    try:
                        tx = int(params.get("x", 0))
                        ty = int(params.get("y", 0))
                        dur = float(params.get("duration", 1.0))
                        is_rel = str(params.get("relative", "false")).lower() == "true"

                        should_animate = str(params.get("animate", "false")).lower() == "true"

                        if should_animate and hasattr(target_obj, "start_animation"):
                            target_obj.start_animation()

                        def on_slide_complete():
                            if should_animate and hasattr(target_obj, "stop_animation"):
                                target_obj.stop_animation()
                        
                        tween_manager.start_move(target_obj, tx, ty, dur, relative=is_rel, on_complete=on_slide_complete)
                        
                    except ValueError:
                        print(f"[ActionManager] Error params for SlideObject: {params}")
                else:
                    print(f"[ActionManager] Warning: Object '{tid}' not found for SlideObject.")

        elif action_type == Actions.MODIFY_OBJECT:
            print(params)
            tid = params.get("id")
            changes = {}
            for k, v in params.items():
                if k != "id":
                    changes[k] = v
                
            scene.modify_object_by_id(tid, changes)
        
        return None