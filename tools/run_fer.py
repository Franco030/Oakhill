import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src.scripting.Lexer import Lexer
from src.scripting.Parser import Parser
from src.scripting.Interpreter import Interpreter, Environment
from src.scripting.AST import ImportStatement

class DummyManager:
    def execute(self, action_type, params, player, scene, source_id=None):
        return None 
    
    def parse_params(self, p): return {}

class FerRuntime:
    def __init__(self):
        self.action_manager = DummyManager()
        self.interpreter = Interpreter(self.action_manager, None, None)

    def load_file(self, filepath):
        if not os.path.exists(filepath):
            print(f"Error: '{filepath}' doesn't exist")
            return None
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def run(self, filepath, func_name="main"):
        code = self.load_file(filepath)
        if not code: return

        try:
            lexer = Lexer(code)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            
            self.interpreter.load(ast)

            if func_name not in self.interpreter.functions:
                print(f"Error: Function'{func_name}' is not defined in the file")
                print(f"Funciones disponibles: {list(self.interpreter.functions.keys())}")
                return

            generator = self.interpreter.run_function(func_name)

            if generator:
                try:
                    if hasattr(generator, '__iter__'):
                        for _ in generator: pass 
                except Exception as e:
                    pass

        except Exception as e:
            print(f"\n[EXECUTION ERROR]: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    filepath = sys.argv[1]
    func = sys.argv[2] if len(sys.argv) > 2 else "main"

    runner = FerRuntime()
    runner.run(filepath, func)