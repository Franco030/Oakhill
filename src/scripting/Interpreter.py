from src.scripting.Lexer import TokenType
from src.scripting.AST import *
from src.utils.Game_Enums import Actions
from src.core.GameState import game_state
import inspect

class ReturnException(Exception):
    def __init__(self, value):
        self.value = value

class Environment:
    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise Exception(f"Variable '{name}' not defined")

class Interpreter:
    def __init__(self, action_manager, player, scene):
        self.action_manager = action_manager
        self.player = player
        self.scene = scene
        self.functions = {}
        self.globals = Environment()
        self.environment = self.globals

        self.global_params = ["blocking", "sound", "volume"]

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
            # MODIFY_OBJECT: Excluded because it accepts arbitrary dynamic parameters (kwargs) 
            #                which doesn't map well to positional arguments.
            # JUMP/LABEL/EXIT: Excluded because .fer handles flow control natively (if/func/return).
        }

    def load(self, program_node):
        for decl in program_node.declarations:
            if isinstance(decl, FunctionDecl):
                self.functions[decl.name] = decl

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
            if key in param_names or key in self.global_params:
                if val is not None:
                    param_string += f"{key}={val};"
            else:
                print(f"[Interpreter Warning] The parameter '{key}' doesn't exist in '{name}'")

        return self.action_manager.execute(action_type, param_string, self.player, self.scene)

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

        if node.name in self.native_map:
            result = self._call_native(node.name, args, kwargs)
            
            if result is not None:
                yield result
            
            return result

        if node.name in self.functions:
            return (yield from self._execute_user_function(self.functions[node.name], args))
        
        print(f"[Interpreter] Error: Unknown function '{node.name}'")
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