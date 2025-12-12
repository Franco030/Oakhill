from src.scripting.Lexer import Lexer, TokenType
from src.scripting.AST import *
from src.utils.Game_Enums import Actions
from src.core.GameState import game_state

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

        self.native_map = {
            "play_sound":    (Actions.PLAY_SOUND, ["sound", "volume"]),
            "show_dialogue": (Actions.SHOW_DIALOGUE, ["text"]),
            "show_note":     (Actions.SHOW_NOTE, ["id"]),
            "wait":          (Actions.WAIT, ["time"]),
            "teleport":      (Actions.TELEPORT, ["zone", "x", "y"])
        }

    def load(self, program_node):
        for decl in program_node.declarations:
            if isinstance(decl, FunctionDecl):
                self.functions[decl.name] = decl

    def run_function(self, name):
        func_node = self.functions.get(name)
        if not func_node:
            print(f"[Interpreter] Function '{name}' was not found")
            return
        
        try:
            return self.visit(func_node.body)
        except ReturnException as e:
            return e.value
        
    def _execute_user_function(self, func_node, arguments):
        previous_env = self.environment
        local_env = Environment(self.globals)

        for i, param_name in enumerate(func_node.params):
            if i < len(arguments):
                local_env.define(param_name, arguments[i])
            else:
                local_env.define(param_name, None)

        self.environment = local_env

        ret_val = None
        try:
            ret_val = self.visit(func_node.body)
        except ReturnException as e:
            ret_val = e.value
        finally:
            self.environment = previous_env
        
        return ret_val
        
    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"[Interpreter] there's no method visit_{type(node).__name__}")
    
    def visit_Block(self, node):
        last_result = None

        for stmt in node.statements:
            res = self.visit(stmt)

            if res is not None:
                last_result = res

        return last_result

    def visit_IfStatement(self, node):
        condition = self.visit(node.condition)
        if condition:
            self.visit(node.then_branch)
        elif node.else_branch:
            self.visit(node.else_branch)

    def visit_ReturnStatement(self, node):
        value = None
        if node.value:
            value = self.visit(node.value)
        raise ReturnException(value)

    def visit_FunctionCall(self, node):
        args = [self.visit(arg) for arg in node.arguments]
        if node.name == "get_flag":
            return game_state.get_flag(args[0])
        
        if node.name in self.native_map:
            return self._call_native(node.name, args)
        
        if node.name in self.functions:
            return self._execute_user_function(self.functions[node.name], args)
        
        print(f"[Interpreter] Error: Unknown function '{node.name}'")

    def _call_native(self, name, args_nodes):
        action_type, param_names = self.native_map[name]
        param_string = ""

        for i, arg_node in enumerate(args_nodes):
            if i >= len(param_names): break

            val = self.visit(arg_node)
            key = param_names[i]
            param_string += f"{key}={val};"

        print(f"[Interpreter] Executing native: {action_type} with params [{param_string}]")
        return self.action_manager.execute(action_type, param_string, self.player, self.scene)
    
    def visit_Literal(self, node):
        if isinstance(node.value, str) and node.value not in self.native_map:
            try:
                return self.environment.get(node.value)
            except:
                return node.value
            
        return node.value
    
    def visit_BinaryOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.operator

        if op == TokenType.PLUS:
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
            
        if op == TokenType.MINUS: return left - right
        if op == TokenType.MUL:   return left * right
        if op == TokenType.DIV:   
            if right == 0:
                print("[Interpreter Runtime Error] Division by zero")
                return 0
            return left / right

        if op == TokenType.GT: return left > right
        if op == TokenType.LT: return left < right
        if op == TokenType.EQUALS: return left == right
        
        return False