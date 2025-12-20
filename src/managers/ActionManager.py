import random
from src.core.GameState import game_state
from src.utils.Game_Constants import MAPS, LEVEL_MUSIC, LEVEL_DARKNESS
from src.utils.utils import resource_path
from .ResourceManager import resource_manager
from .TweenManager import tween_manager
from src.utils.Game_Enums import Actions, Colors

from src.core.GameResults import (
    NoteResult, DialogueResult, ChoiceResult, 
    ImageResult, AnimationResult, DestroyResult,
    WaitResult
)


_handlers_registry = {}

def register(action_enum):
    def decorator(func):
        _handlers_registry[action_enum] = func
        return func
    return decorator

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
            print(f"{Colors.BRIGHT_YELLOW}[ActionManager]{Colors.RESET} Warning: Action {action_type} not implemented")
            return None

    @register(Actions.SHOW_IMAGE)
    def _handle_show_image(self, params, _, _p, _s, _id):
        path = params.get("image") or params.get("path")
        should_pause = str(params.get("pause_music", "false")).lower() == "true"
        blocking = str(params.get("blocking", "false")).lower() == "true"
        return ImageResult(path, blocking=blocking, pause_music=should_pause)

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

    @register(Actions.DESTROY_OBJECT)
    def _handle_destroy_object(self, params, _, _p, _s, source_id):
        target_id = params.get("id")
        if target_id == "SELF":
            target_id = source_id if source_id else None
        
        if target_id:
            return DestroyResult(target_id)
        return None