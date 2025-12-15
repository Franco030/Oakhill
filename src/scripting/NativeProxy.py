from src.core.GameState import game_state
from src.scripting.AST import *

class NativeProxy:
    """
    Static class to manage actions between Python and Fer
    """

    @staticmethod
    def py_to_fer(value, interpreter_ref):
        if value is None:
            return None
        
        if isinstance(value, (tuple, list)) and len(value) == 2:
            if "Vector2" in interpreter_ref.structs:
                from src.scripting.Interpreter import FerInstance
                struct_def = interpreter_ref.structs["Vector2"]
                instance = FerInstance(struct_def)
                instance.set("x", value[0])
                instance.set("y", value[1])
                return instance
        
        return value
    
    @staticmethod
    def fer_to_py(value):
        if hasattr(value, "struct_def") and value.struct_def.name == "Vector2":
            return (value.get("x"), value.get("y"))
        
        return value

class NativeObject:
    """
    Wrapper to wrap real objects in python
    """
    def __init__(self, real_obj, obj_id, interpreter):
        super().__setattr__("_real_obj", real_obj)
        super().__setattr__("_id", obj_id)
        super().__setattr__("_interpreter", interpreter)

    def __getattr__(self, name):
        if name.startswith("_"):
            print(f"[NativeObject] Access denied to private attribute '{name}'")
            return None

        try:
            if not hasattr(self._real_obj, name):
                return None
            
            val = getattr(self._real_obj, name)

            if callable(val):
                return val 
            
            return NativeProxy.py_to_fer(val, self._interpreter)

        except Exception as e:
            print(f"[NativeObject] Error reading '{name}': {e}")
            return None
        
    def __setattr__(self, name, value):
        if name.startswith("_"):
            print(f"[NativeObject] Cannot modify private attribute '{name}'")
            return

        try:
            py_val = NativeProxy.fer_to_py(value)
            setattr(self._real_obj, name, py_val)

            if self._id:
                flag_key = f"OBJ_{self._id}_{name}"
                game_state.set_flag(flag_key, py_val)
                print(f"[NativeBridge] Persisted: {flag_key} = {py_val}")

        except Exception as e:
            print(f"[NativeObject] Error writing '{name}': {e}")