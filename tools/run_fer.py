import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src.managers.ScriptManager import ScriptManager
from src.scripting.Interpreter import Interpreter

class DummyManager:
    def execute(self, action_type, params, player, scene, source_id=None):
        return None 
    
    def parse_params(self, p): return {}

class FerRuntime:
    def __init__(self):
        self.action_manager = DummyManager()
        self.interpreter = Interpreter(self.action_manager, None, None)
        self.script_manager = None

    def run(self, filepath, func_name="main"):
        abs_path = os.path.abspath(filepath)
        script_dir = os.path.dirname(abs_path)
        script_filename = os.path.basename(abs_path)
        
        script_name = os.path.splitext(script_filename)[0]

        self.script_manager = ScriptManager(relative_path=script_dir)

        ast = self.script_manager.get_script(script_name)

        if not ast: 
            print("Error: AST couldn't be done")
            return

        self.interpreter.load(ast)

        if func_name not in self.interpreter.functions:
            print(f"Error: Function '{func_name}' is not defined in {script_filename} or its imports")
            print(f"Funciones disponibles: {list(self.interpreter.functions.keys())}")
            return

        generator = self.interpreter.run_function(func_name)

        if generator:
            try:
                if hasattr(generator, '__iter__'):
                    for val in generator: 
                        pass 
            except Exception as e:
                print(f"\n[RUNTIME EXCEPTION]: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)

    filepath = sys.argv[1]
    func = sys.argv[2] if len(sys.argv) > 2 else "main"

    runner = FerRuntime()
    runner.run(filepath, func)