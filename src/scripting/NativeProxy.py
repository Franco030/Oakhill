from src.core.GameState import game_state
from src.scripting.AST import *

import os
import warnings
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "1"
warnings.filterwarnings("ignore", message=".*pkg_resources.*")

import pygame

class NativeProxy:
    """
    Static class to manage actions between Python and Fer
    """

    @staticmethod
    def py_to_fer(value, interpreter):
        if value is None:
            return None
        
        if isinstance(value, (tuple, list)) and len(value) == 2:
            return NativeProxy._create_vector2(value[0], value[1], interpreter)
        if isinstance(value, pygame.math.Vector2):
            return NativeProxy._create_vector2(value.x, value.y, interpreter)

        if isinstance(value, pygame.Rect):
            return NativeObject(value, None, interpreter)
        
        if callable(value):
            return NativeFunction(value, interpreter)
        
        return value
    
    @staticmethod
    def fer_to_py(value):
        if isinstance(value, NativeObject):
            return value._real_obj
        
        if isinstance(value, NativeSystem):
            return value._real_system
        
        if hasattr(value, "struct_def") and value.struct_def.name == "Vector2":
            return (value.get("x"), value.get("y"))
        
        return value
    
    @staticmethod
    def _create_vector2(x, y, interpreter):
        if "Vector2" in interpreter.structs:
            from src.scripting.Interpreter import FerInstance 
            struct_def = interpreter.structs["Vector2"]
            instance = FerInstance(struct_def)
            instance.set("x", x)
            instance.set("y", y)
            return instance
        return (x, y)
    
class NativeFunction:
    def __init__(self, py_func, interpreter):
        self.func = py_func
        self.interpreter = interpreter

    def __call__(self, *args, **kwargs):
        py_args = [NativeProxy.fer_to_py(arg) for arg in args]

        py_kwargs = {}
        for key, value in kwargs.items():
            py_kwargs[key] = NativeProxy.fer_to_py(value)

        try:
            result = self.func(*py_args, **py_kwargs)
            return NativeProxy.py_to_fer(result, self.interpreter)
        except Exception as e:
            print(f"[NativeProxy] Error executing '{self.func.__name__}': {e}")
            return None
    
class NativeSystem:
    def __init__(self, system_obj, interpreter):
        self._real_system = system_obj
        self._interpreter = interpreter

    def __getattr__(self, name):
        if name.startswith("_"): return None

        if hasattr(self._real_system, name):
            val = getattr(self._real_system, name)
            return NativeProxy.py_to_fer(val, self._interpreter)
        return None
    
class NativeObject:
    def __init__(self, real_obj, obj_id, interpreter):
        super().__setattr__("_real_obj", real_obj)
        super().__setattr__("_id", obj_id)
        super().__setattr__("_interpreter", interpreter)

    def __getattr__(self, name):
        if name.startswith("_"): return None

        try:
            if isinstance(self._real_obj, dict):
                val = self._real_obj.get(name)
                return NativeProxy.py_to_fer(val, self._interpreter)

            if hasattr(self._real_obj, name):
                val = getattr(self._real_obj, name)
                return NativeProxy.py_to_fer(val, self._interpreter)
                
        except Exception as e:
            pass
        return None

    def __setattr__(self, name, value):
        if name.startswith("_"): return

        try:
            py_val = NativeProxy.fer_to_py(value)
            
            if isinstance(self._real_obj, dict):
                self._real_obj[name] = py_val
                return

            setattr(self._real_obj, name, py_val)

            if self._id:
                flag_key = f"OBJ_{self._id}_{name}"
                game_state.set_flag(flag_key, py_val)

        except Exception as e:
            print(f"[NativeBridge] Write Error '{name}': {e}")
    
class RemoteObject:
    def __init__(self, obj_id, map_id, zone_id, interpreter):
        self._id = obj_id
        self._map_id = map_id
        self._zone_id = zone_id
        self._interpreter = interpreter

    def __getattr__(self, name):
        if name.startswith("_"): return None
        
        flag_key = f"OBJ_{self._id}_{name}"
        stored_val = game_state.get_flag(flag_key)
        
        if stored_val is not None:
             return stored_val
             
        if self._map_id:
            print(f"[RemoteObject] Warning: Property '{name}' unknown. In '{self._id}' of '{self._map_id}' zone '{self._zone_id}'")
        return None

    def __setattr__(self, name, value):
        if name.startswith("_"): 
            super().__setattr__(name, value)
            return

        py_val = NativeProxy.fer_to_py(value)
        flag_key = f"OBJ_{self._id}_{name}"
        
        game_state.set_flag(flag_key, py_val)
        
        location_info = f" [{self._map_id} {self._zone_id}]" if self._map_id else ""
        print(f"[RemoteObject] Persisting change for '{self._id}'{location_info}: {name} = {py_val}")