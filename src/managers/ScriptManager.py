import os
from src.utils.utils import resource_path
from src.scripting.Lexer import Lexer
from src.scripting.Parser import Parser

class ScriptManager:
    def __init__(self, relative_path="data/scripts"):
        self.base_dir = relative_path
        self.cache = {}

    def get_script(self, script_name):
        """
        Searches, loads and parses a script. If it's already in memory it returns is directly.

        :param script_name: The name of the file without route (e.g. "move_objects")
        :return: The Program node of the AST or None if it fails
        """

        if script_name in self.cache:
            return self.cache[script_name]

        filename = script_name if script_name.endswith(".fer") else f"{script_name}.fer"
        full_path = resource_path(os.path.join(self.base_dir, filename))

        try:
            if not os.path.exists(full_path):
                print(f"[ScriptManager] ERROR: File was not found: '{full_path}'")
                return None

            print(f"[ScriptManager] Loading and compiling: {script_name} ...")
            
            with open(full_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            lexer = Lexer(source_code)
            tokens = lexer.tokenize()

            parser = Parser(tokens)
            ast = parser.parse()

            self.cache[script_name] = ast
            print(f"[ScriptManager] '{script_name}' compiled successfully")
            return ast

        except Exception as e:
            print(f"[ScriptManager] CRITIC ERROR PARSING '{script_name}':\n{e}")
            return None

    def reload_all(self):
        """
        For debug: cleans cache to reload changes without closing the game
        """
        self.cache.clear()
        print(f"[ScriptManager] Cache reloaded")

script_manager = ScriptManager()