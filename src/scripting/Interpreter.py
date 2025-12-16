from src.scripting.Lexer import TokenType
from src.scripting.AST import *
from src.scripting.NativeProxy import NativeObject, NativeProxy
from src.utils.Game_Enums import Actions
from src.core.GameState import game_state
import inspect
import time

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value
    
class FerStruct:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

    def __repr__(self):
        return f"<Struct {self.name}>"
    
class FerInstance:
    def __init__(self, struct_def):
        self.struct_def = struct_def
        self.fields = {}
        for field in struct_def.fields:
            self.fields[field] = None
    
    def get(self, name):
        if name in self.fields:
            return self.fields[name]
        raise Exception(f"Undefined property '{name}' on instance of {self.struct_def.name}")
    
    def set(self, name, value):
        if name in self.fields:
            self.fields[name] = value
        else:
            raise Exception(f"Cannot set undefined property '{name}' on {self.struct_def.name}")
        
    def __getattr__(self, name):
        if name in self.fields:
            return self.fields[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        
    def __repr__(self):
        return f"<{self.struct_def.name} Instance: {self.fields}>"

class Environment:
    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent

    def define(self, name, value):
        self.values[name] = value

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
            return
        
        # if it's not here it looks in a bigger scope
        if self.parent:
            self.parent.assign(name, value)
            return
        
        raise Exception(f"Undefined variable '{name}'. Cannot assign value")

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise Exception(f"Variable '{name}' not defined")

class Interpreter:
    def __init__(self, action_manager, player, scene, source_id="SYSTEM"):
        self.action_manager = action_manager
        self.player = player
        self.scene = scene
        self.source_id = source_id
        self.functions = {}
        self.structs = {}
        self.globals = Environment()


        # The structures for function helpers and Marshalling
        self.structs["Vector2"] = FerStruct("Vector2", ["x", "y"]) # Structure for python tuples

        self.structs["ActionResult"] = FerStruct("ActionResult", [
            "value",
            "source",
            "duration",
            "meta",
            "original_return",
        ])

        # The global function 'get_object'. Before setting up self.environment
        # A lambda function calls an internal method with access to self.scene
        self.globals.define("get_object", lambda obj_id: self._native_get_object(obj_id))

        self.environment = self.globals
        self.global_params = ["blocking", "sound", "volume"]


        # This functions are slowly becoming more easy to make in FER
        self.native_map = {
            # --- AUDIO ---
            "play_sound":     (Actions.PLAY_SOUND, ["sound", "volume"]),
            "change_music":   (Actions.CHANGE_MUSIC, ["path", "fade", "volume", "loop"]),

            # --- UI & DIALOGUE ---
            "show_dialogue":  (Actions.SHOW_DIALOGUE, ["text", "color", "pause_music"]),
            "show_note":      (Actions.SHOW_NOTE, ["id", "save"]),
            "ask_choice":     (Actions.ASK_CHOICE, ["text", "flag"]),
            
            # --- VISUALS ---
            "show_image":     (Actions.SHOW_IMAGE, ["image", "pause_music"]),
            "close_image":    (Actions.CLOSE_IMAGE, []),
            "show_animation": (Actions.SHOW_ANIMATION, ["path", "frames", "speed", "loop", "pause_music"]),
            "modify_light":   (Actions.MODIFY_LIGHT, ["enable"]),

            # --- LEVEL & MOVEMENT ---
            "teleport":       (Actions.TELEPORT, ["zone", "x", "y"]),
            "change_level":   (Actions.CHANGE_LEVEL, ["level", "json", "zone", "x", "y"]),
            "wait":           (Actions.WAIT, ["time"]),

            # --- OBJECT MANIPULATION ---
            "unhide_object":  (Actions.UNHIDE_OBJECT, ["id"]),
            "hide_object":    (Actions.HIDE_OBJECT, ["id"]),
            "destroy_object": (Actions.DESTROY_OBJECT, ["id"]),
            
            # Move instantly
            "move_object":    (Actions.MOVE_OBJECT, ["id", "x", "y", "relative"]),
            
            # Move smoothly (Tween)
            "slide_object":   (Actions.SLIDE_OBJECT, ["id", "x", "y", "duration", "relative", "animate"]),

            # --- GLOBAL FLAGS ---
            # While .fer has local vars, these modify the permanent GameState
            "set_flag":       (Actions.SET_FLAG, ["flag", "value"]),
            "increment_flag": (Actions.INCREMENT_FLAG, ["flag", "value"]),
            
            # --- EXCLUDED ACTIONS ---
            # JUMP/LABEL/EXIT: Excluded because .fer handles flow control natively (if/func/return).
        }

    def load(self, program_node):
        for decl in program_node.declarations:
            if isinstance(decl, FunctionDecl):
                self.functions[decl.name] = decl
            
            elif isinstance(decl, StructDecl):
                self.structs[decl.name] = FerStruct(decl.name, decl.fields)

    def run_function(self, name, args=[]):
        func_node = self.functions.get(name)
        if not func_node: 
            print(f"[Interpreter] Warning: Function '{name}' was not found")
            return None
        
        yield from self._execute_user_function(func_node, args)

    def evaluate(self, node):
        result = self.visit(node)

        if inspect.isgenerator(result):
            return (yield from result)
        
        return result

    def _execute_user_function(self, func_node, arguments):
        previous_env = self.environment
        local_env = Environment(self.globals)
        
        for i, param_name in enumerate(func_node.params):
            val = arguments[i] if i < len(arguments) else None
            local_env.define(param_name, val)

        self.environment = local_env
        
        try:
            generator = self.visit(func_node.body)
            
            if inspect.isgenerator(generator):
                yield from generator
            elif generator is not None:
                yield generator

        except ReturnException as e:
            return e.value
        finally:
            self.environment = previous_env

    def _call_native(self, name, args, kwargs):
        action_type, param_names = self.native_map[name]
        param_string = ""

        for i, val in enumerate(args):
            if i < len(param_names):
                if val is not None:
                    param_string += f"{param_names[i]}={val};"

        for key, val in kwargs.items():
            is_dynamic_func = (name == "modify_object")
            if is_dynamic_func or key in param_names or key in self.global_params:
                if val is not None:
                    val_str = str(val)
                    param_string += f"{key}={val_str}"

            else:
                print(f"[Interpreter Warning] The parameter '{key}' doesn't exist in '{name}'")

        return self.action_manager.execute(action_type, param_string, self.player, self.scene)
    
    def _native_get_object(self, obj_id):
        """
        Busca un objeto nativo en la escena actual por su ID.
        """
        if not self.scene: return None
        
        if obj_id == "player":
            return NativeObject(self.player, "player", self)

        for obj in self.scene.obstacles:
            if getattr(obj, "id", None) == obj_id:
                return NativeObject(obj, obj_id, self)

        for obj in self.scene.interactables:
            if getattr(obj, "id", None) == obj_id:
                return NativeObject(obj, obj_id, self)
        
        # for enemy in self.scene.enemies:
        #     if getattr(enemy, "id", None) == obj_id:
        #         return NativeObject(enemy, obj_id, self)

        triggers_list = getattr(self.scene, "triggers", getattr(self.scene, "_triggers", []))
        for trig in triggers_list:
            if getattr(trig, "id", None) == obj_id:
                return NativeObject(trig, obj_id, self)

        print(f"[Interpreter] Objeto '{obj_id}' no encontrado en la escena.")
        return None
    
    def _enrich_meta(self, func_name, args, kwargs, pre_exec_state=None):
        """
        Generates intelligent metadata, depending on the function
        """
        meta = {
            "timestamp": time.time(),
            "params": {**kwargs}
        }

        if args:
            meta["args_list"] = args

        if func_name in ["set_flag", "increment_flag", "ask_choice"]:
            flag_name = None
            
            if func_name == "set_flag" or func_name == "increment_flag":
                flag_name = args[0] if len(args) > 0 else kwargs.get("flag")
            elif func_name == "ask_choice":
                flag_name = args[1] if len(args) > 1 else kwargs.get("flag")

            if flag_name:
                meta["target_flag"] = flag_name
                meta["previous_value"] = pre_exec_state.get("flag_val")
                meta["new_value"] = game_state.get_flag(flag_name)
                
                meta["changed"] = meta["previous_value"] != meta["new_value"]

        elif func_name == "play_sound":
            meta["sound_id"] = args[0] if len(args) > 0 else kwargs.get("sound")
            meta["volume"] = args[1] if len(args) > 1 else kwargs.get("volume", 1.0)

        elif func_name in ["unhide_object", "move_object", "slide_object", "destroy_object", "modify_object"]:
            obj_id = args[0] if len(args) > 0 else kwargs.get("id")
            meta["target_object_id"] = obj_id

            if func_name == "modify_object":
                meta["modifications"] = kwargs

        return meta

    # --- VISIT ---

    def visit(self, node):
        if node is None:
            print("[Interpreter DEBUG] Attempt to visit a 'None' node. This indicates an error in the Parser or in the AST")
            return None

        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"Method visit_{type(node).__name__} doesn't exist")

    # --- NODES ---

    def visit_Block(self, node):
        for stmt in node.statements:
            if stmt is None: continue
            
            result = self.visit(stmt)
            if inspect.isgenerator(result):
                yield from result
            
            elif result is not None and hasattr(result, "blocking"):
                yield result

    def visit_Assign(self, node):
        value = yield from self.evaluate(node.value)
        self.environment.assign(node.name, value)
        
        return value

    def visit_FunctionCall(self, node):
        args = []
        for arg in node.arguments:
            val = yield from self.evaluate(arg)
            args.append(val)

        kwargs = {}
        if hasattr(node, "kwargs"):
            for key, val_node in node.kwargs.items():
                val = yield from self.evaluate(val_node)
                kwargs[key] = val

        if node.name == "print":
            output = " ".join(str(arg) for arg in args)
            print(f"\033[96m[SCRIPT DEBUG]\033[0m {output}") 
            return None
            
        if node.name == "get_flag":
            return game_state.get_flag(args[0])
        
        pre_exec_state = {}
        if getattr(node, 'is_capture', False):
            start_time = time.time()

            target_flag = None
            if node.name in ["set_flag", "increment_flag"]:
                target_flag = args[0] if len(args) > 0 else kwargs.get("flag")
            elif node.name == "ask_choice":
                target_flag = args[1] if len(args) > 1 else kwargs.get("flag")
            
            if target_flag:
                pre_exec_state["flag_val"] = game_state.get_flag(target_flag)


        result_value = None
        executed = False
        
        start_time = time.time()
        
        # Here we check if the literal is a native function
        if node.name in self.native_map:
            result_value = self._call_native(node.name, args, kwargs)
            if result_value is not None:
                yield result_value
            executed = True
        
        # If it is a user made function (in FER)
        elif node.name in self.functions:
            result_value = yield from self._execute_user_function(self.functions[node.name], args)
            executed = True

        # If it is a struct
        elif node.name in self.structs:
            struct_def = self.structs[node.name]
            instance = FerInstance(struct_def)

            for i, val in enumerate(args):
                if i < len(struct_def.fields):
                    field_name = struct_def.fields[i]
                    instance.set(field_name, val)

                else:
                    print(f"[Interpreter] Too many arguments for struct '{struct_def.name}'")

            if kwargs:
                for key, val in kwargs.items():
                    instance.set(key, val)
            
            return instance
        
        # If its anything else. And, in this case, anything alse might be a Native python Object
        else:
            try:
                func_obj = self.environment.get(node.name)

                if callable(func_obj):
                    py_args = [NativeProxy.fer_to_py(arg) for arg in args]
                    result = func_obj(*py_args)

                    return NativeProxy.py_to_fer(result, self)
            except:
                pass

            print(f"[Interpreter] Error: Unknown function '{node.name}'")
            return None
        
        if getattr(node, 'is_capture', False):
            end_time = time.time()
            duration = end_time - start_time
            
            final_value = result_value

            if node.name == "ask_choice":
                flag_name = None
                if len(args) > 1: flag_name = args[1]
                elif "flag" in kwargs: flag_name = kwargs["flag"]
                
                if flag_name:
                    final_value = game_state.get_flag(flag_name)

            enriched_meta = self._enrich_meta(node.name, args, kwargs, pre_exec_state)
            if result_value and hasattr(result_value, "blocking"):
                enriched_meta["blocking"] = result_value.blocking
            
            struct_def = self.structs.get("ActionResult")
            instance = FerInstance(struct_def)

            instance.set("value", final_value)
            instance.set("source", self.source_id)
            instance.set("duration", duration)
            instance.set("meta", enriched_meta)
            instance.set("original_return", result_value)

            return instance


        if not executed:
            print(f"[Interpreter] Error: Unknown function '{node.name}'")
            return None
            
        return result_value
    
    def visit_StructDecl(self, node):
        """
        Registers the instance in runtime
        """
        self.structs[node.name] = FerStruct(node.name, node.fields)
        return None
    
    def visit_Literal(self, node):
        if isinstance(node.value, str) and node.value not in self.native_map:
            try:
                return self.environment.get(node.value)
            except:
                return node.value
        return node.value
    
    def visit_VarDecl(self, node):
        value = None
        if node.initializer:
            value = yield from self.evaluate(node.initializer)

        self.environment.define(node.name, value)
        return None

    def visit_IfStatement(self, node):
        condition = yield from self.evaluate(node.condition)
        
        if condition:
            return (yield from self.evaluate(node.then_branch))
        
        elif node.else_branch:
            return (yield from self.evaluate(node.else_branch))
            
        return None

    def visit_ReturnStatement(self, node):
        value = None
        if node.value:
            value = yield from self.evaluate(node.value)
        raise ReturnException(value)
    
    def visit_UnaryOp(self, node):
        right = yield from self.evaluate(node.right)
        
        if node.operator == TokenType.NOT:
            return not right
        if node.operator == TokenType.MINUS:
            if isinstance(right, (int, float)):
                return -right
            return None
        return None

    def visit_BinaryOp(self, node):
        left = yield from self.evaluate(node.left)
        right = yield from self.evaluate(node.right)
        op = node.operator

        if op == TokenType.PLUS:
            if isinstance(left, str) or isinstance(right, str): return str(left) + str(right)
            return left + right
        if op == TokenType.MINUS: return left - right
        if op == TokenType.MUL:   return left * right
        if op == TokenType.DIV:   return 0 if right == 0 else left / right
        
        if op == TokenType.GT: return left > right
        if op == TokenType.LT: return left < right
        if op == TokenType.EQUALS: return left == right
        
        if op == TokenType.LE: return left <= right
        if op == TokenType.GE: return left >= right
        if op == TokenType.NE: return left != right
        
        return False
    
    def visit_LogicalOp(self, node):
        left = yield from self.evaluate(node.left)

        if node.operator == TokenType.OR:
            if left:
                return True
            right = yield from self.evaluate(node.right)
            return bool(right)

        if node.operator == TokenType.AND:
            if not left:
                return False
            right = yield from self.evaluate(node.right)
            return bool(right)
            
        return None
    
    def visit_ListLiteral(self, node):
        elements = []
        for element_node in node.elements:
            val = yield from self.evaluate(element_node)
            elements.append(val)
        return elements
    
    def visit_DictLiteral(self, node):
        dict_pairs = {}
        for key_node, value_node in node.pairs:
            key = yield from self.evaluate(key_node)
            value = yield from self.evaluate(value_node)

            if not isinstance(key, (str, int, float, bool)):
                key = str(key)

            dict_pairs[key] = value
        return dict_pairs
    
    def visit_IndexAccess(self, node):
        target = yield from self.evaluate(node.target)
        index = yield from self.evaluate(node.index)

        if isinstance(target, list):
            if not isinstance(index, int):
                print(f"[Interpreter Error] List indices must be integers.")
                return None
            try:
                return target[index]
            except IndexError:
                print(f"[Interpreter Error] List index out of range.")
                return None
            
        if isinstance(target, dict):
            return target.get(index)

        print(f"[Interpreter Error] Type {type(target)} is not subscriptable.")
        return None
        
    def visit_WhileStatement(self, node):
        while True:
            condition = yield from self.evaluate(node.condition)
            
            if not condition:
                break
            
            yield from self.evaluate(node.body)
        return None
    
    def visit_ForStatement(self, node):
        iterable_value = yield from self.evaluate(node.iterable)
        
        if not isinstance(iterable_value, list):
            print(f"[Interpreter Error] 'for' loop expects a list, got {type(iterable_value)}")
            return None

        for item in iterable_value:
            self.environment.define(node.iterator_name, item)
            
            yield from self.evaluate(node.body)
            
        return None
    
    def visit_GetAttribute(self, node):
        """
        Gets attributes from either Structs or from Native python Objects
        """
        obj = yield from self.evaluate(node.object_node)
        
        if isinstance(obj, FerInstance):
            return obj.get(node.property_name)
        
        if isinstance(obj, NativeObject):
            # getattr is overriden in the NativeObject class so that it works as I like
            val = getattr(obj, node.property_name)
            return val
        
        if isinstance(obj, dict):
            return obj.get(node.property_name)

        print(f"[Interpreter Error] Cannot read property '{node.property_name}' on {type(obj)}")
        return None
    
    def visit_SetAttribute(self, node):
        """
        Sets attributes to either Structs or Native python Objects
        """
        obj = yield from self.evaluate(node.object_node)
        value = yield from self.evaluate(node.value)

        if isinstance(obj, FerInstance):
            obj.set(node.property_name, value)
            return value

        if isinstance(obj, NativeObject):
            # setattr is override in the NativeObject class so that it works as I like
            setattr(obj, node.property_name, value)
            return value
        
        if isinstance(obj, dict):
            obj[node.property_name] = value
            return value
        
        print(f"[Interpreter Error] Cannot set property on type {type(obj)}")
        return None