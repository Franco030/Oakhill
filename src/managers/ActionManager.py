import random
from src.core.GameState import game_state
from src.utils.Game_Constants import MAPS, LEVEL_MUSIC, LEVEL_DARKNESS
from src.utils.utils import resource_path
from .ResourceManager import resource_manager
from .TweenManager import tween_manager
from src.utils.Game_Enums import Actions

from src.core.GameResults import (
    NoteResult, DialogueResult, ChoiceResult, 
    ImageResult, AnimationResult, DestroyResult
)


_handlers_registry = {}

def register(action_enum):
    def decorator(func):
        _handlers_registry[action_enum] = func
        return func
    return decorator

class ActionManager:
    def __init__(self, note_manager):
        self.note_manager = note_manager

    
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
    
    def execute(self, action_type, param_string, player, scene, source_id=None):
        params = self.parse_params(param_string)

        sound_id = params.get("sound")
        if sound_id and sound_id != "silent":
            snd = resource_manager.get_sound(sound_id)
            if snd: 
                vol = float(params.get("volume", 1.0))
                snd.set_volume(vol)
                snd.play()

        handler = _handlers_registry.get(action_type)
        if handler:
            result = handler(self, params, param_string, player, scene, source_id)
            if result and hasattr(result, "blocking"):
                if "blocking" in params:
                    result.blocking = params.get("blocking")
            return result
        else:
            print(f"[ActionManager] Warning: Action {action_type} not implemented")
            return None
        
    
    @register(Actions.SET_FLAG)
    def _handle_set_flag(self, params, _, _p, _s, _id):
        key = params.get("flag")
        val = params.get("value")
        if key: game_state.set_flag(key, val)

    @register(Actions.INCREMENT_FLAG)
    def _handle_increment_flag(self, params, _, _p, _s, _id):
        key = params.get("flag")
        amount = params.get("value", 1)
        if key: game_state.increment_flag(key, amount)

    @register(Actions.TELEPORT)
    def _handle_teleport(self, params, _, _p, _s, _id):
        zone_str = str(params.get("zone"))
        x = params.get("x")
        y = params.get("y")
        if x is not None and y is not None:
            game_state.request_teleport(zone_str, x, y)

    @register(Actions.PLAY_SOUND)
    def _handle_play_sound(self, params, _, _p, _s, _id):
        pass

    @register(Actions.UNHIDE_OBJECT)
    def _handle_unhide_object(self, params, _, _p, scene, _id):
        tid = params.get("id")
        if tid: scene.unhide_object_by_id(tid)

    @register(Actions.HIDE_OBJECT)
    def _handle_hide_object(self, params, _, _p, scene, _id):
        tid = params.get("id")
        if tid: scene.hide_object_by_id(tid)

    @register(Actions.MODIFY_LIGHT)
    def _handle_modify_light(self, params, _, _p, scene, _id):
        enable = params.get("enable", False)
        scene.has_darkness = enable

    @register(Actions.RANDOM_ACTION)
    def _handle_random_action(self, params, raw_param_string, player, scene, source_id):
        chance = int(params.get("chance", 50))
        roll = random.randint(1, 100)
        if roll <= chance:
            sub_action = params.get("action")
            return self.execute(sub_action, raw_param_string, player, scene, source_id)
        return None

    @register(Actions.CHANGE_LEVEL)
    def _handle_change_level(self, params, _, _p, _s, _id):
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

    @register(Actions.SHOW_NOTE)
    def _handle_show_note(self, params, _, _p, _s, _id):
        note_id = params.get("id")
        should_save = str(params.get("save", "false")).lower() == "true"
        if not note_id: return None
        
        note_data = self.note_manager.get_note_content(note_id)
        if note_data:
            if should_save:
                game_state.unlock_note(note_id)
            return NoteResult(note_data, blocking=True)
        return None

    @register(Actions.SHOW_DIALOGUE)
    def _handle_show_dialogue(self, params, _, _p, _s, _id):
        text = params.get("text", "...")
        color_str = str(params.get("color", "255,255,255"))
        should_pause = str(params.get("pause_music", "false")).lower() == "true"
        
        try:
            text_color = tuple(map(int, color_str.split(',')))
        except:
            text_color = (255, 255, 255)

        return DialogueResult(
            data={"text": text, "color": text_color},
            blocking=True,
            pause_music=should_pause
        )

    @register(Actions.SHOW_IMAGE)
    def _handle_show_image(self, params, _, _p, _s, _id):
        path = params.get("image") or params.get("path")
        should_pause = str(params.get("pause_music", "false")).lower() == "true"
        blocking = str(params.get("blocking", "false")).lower() == "true"
        return ImageResult(path, blocking=blocking, pause_music=should_pause)

    @register(Actions.CLOSE_IMAGE)
    def _handle_close_image(self, params, _, _p, _s, _id):
        pass

    @register(Actions.SHOW_ANIMATION)
    def _handle_show_animation(self, params, _, _p, _s, _id):
        base_id = params.get("path")
        frames = int(params.get("frames", 1))
        speed = float(params.get("speed", 0.1))
        loop = str(params.get("loop", "true")).lower() == "true"
        should_pause = str(params.get("pause_music", "false")).lower() == "true"

        image_list = []
        if base_id:
            for i in range(frames):
                image_list.append(f"{base_id}_{i}")
            
        return AnimationResult(
            image_list, 
            speed=speed, 
            blocking=True, 
            loop=loop,
            pause_music=should_pause
        )

    @register(Actions.CHANGE_MUSIC)
    def _handle_change_music(self, params, _, _p, _s, _id):
        music_path = params.get("path") or params.get("music")
        fade_ms = int(params.get("fade", 500))
        volume = float(params.get("volume", 0.6))
        loop_count = int(params.get("loop", -1))

        if music_path:
            resource_manager.play_music(music_path, volume, loop_count, fade_ms)

    @register(Actions.MOVE_OBJECT)
    def _handle_move_object(self, params, _, _p, scene, _id):
        tid = params.get("id")
        if tid:
            target_obj = scene.get_object_by_id(tid)
            if target_obj:
                try:
                    tx = int(params.get("x", 0))
                    ty = int(params.get("y", 0))
                    is_rel = str(params.get("relative", "false")).lower() == "true"
                    tween_manager.teleport(target_obj, tx, ty, relative=is_rel)
                except ValueError: pass

    @register(Actions.SLIDE_OBJECT)
    def _handle_slide_object(self, params, _, _p, scene, _id):
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
                except ValueError: pass

    @register(Actions.MODIFY_OBJECT)
    def _handle_modify_object(self, params, _, _p, scene, _id):
        tid = params.get("id")
        changes = {k: v for k, v in params.items() if k != "id"}
        scene.modify_object_by_id(tid, changes)

    @register(Actions.ASK_CHOICE)
    def _handle_ask_choice(self, params, _, _p, _s, _id):
        text = params.get("text", "Choose")
        flag_name = params.get("flag", "temp_decision")
        return ChoiceResult(text, flag_name, blocking=True)

    @register(Actions.JUMP_IF_TRUE)
    def _handle_jump_if_true(self, params, _, _p, _s, _id):
        flag_name = params.get("flag")
        target_label = params.get("label") or params.get("target")
        if flag_name and game_state.get_flag(flag_name, False) == True:
            return {"type": "Jump", "target": target_label}
        return None

    @register(Actions.JUMP_IF_FALSE)
    def _handle_jump_if_false(self, params, _, _p, _s, _id):
        flag_name = params.get("flag")
        target_label = params.get("label") or params.get("target")
        if flag_name and game_state.get_flag(flag_name, False) == False:
            return {"type": "Jump", "target": target_label}
        return None

    @register(Actions.EXIT)
    def _handle_exit(self, params, _, _p, _s, _id):
        return {"type": "Exit"}

    @register(Actions.LABEL)
    def _handle_label(self, params, _, _p, _s, _id):
        return None

    @register(Actions.WAIT)
    def _handle_wait(self, params, _, _p, _s, _id):
        return None

    @register(Actions.DESTROY_OBJECT)
    def _handle_destroy_object(self, params, _, _p, _s, source_id):
        target_id = params.get("id")
        if target_id == "SELF":
            target_id = source_id if source_id else None
        
        if target_id:
            return DestroyResult(target_id)
        return None