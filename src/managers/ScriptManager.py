import os
from src.utils.utils import resource_path
from src.scripting.Lexer import Lexer
from src.scripting.Parser import Parser
from src.scripting.Interpreter import ImportStatement

class ScriptManager:
    def __init__(self, relative_path="data/scripts"):
        self.base_dir = relative_path
        self.cache = {}

    def get_script(self, script_name):
        if script_name in self.cache:
            return self.cache[script_name]

        print(f"[ScriptManager] Initiating '{script_name}' and its dependencies")

        imported_modules = set()
        main_ast = self._load_and_parse(script_name)

        if not main_ast: return None

        final_declarations = []
        self._resolve_dependencies(main_ast, final_declarations, imported_modules)
        main_ast.declarations = final_declarations
        
        self.cache[script_name] = main_ast
        print(f"[ScriptManager] '{script_name}' compiled successfully")
        return main_ast
    
    def _resolve_dependencies(self, ast_node, accumulated_decls, visited_modules):
        for decl in ast_node.declarations:
            if isinstance(decl, ImportStatement):
                module_name = decl.module_name
                
                if module_name in visited_modules:
                    continue
                
                visited_modules.add(module_name)
                sub_ast = self._load_and_parse(module_name)
                if sub_ast:
                    self._resolve_dependencies(sub_ast, accumulated_decls, visited_modules)
            else:
                accumulated_decls.append(decl)

    def _load_and_parse(self, name):
        filename = name if name.endswith(".fer") else f"{name}.fer"
        full_path = resource_path(os.path.join(self.base_dir, filename))

        if not os.path.exists(full_path):
            print(f"[ScriptManager] ERROR: '{filename}' was not found")
            return None

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                source = f.read()
            
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            return parser.parse()
        except Exception as e:
            print(f"[ScriptManager] Error parsing '{filename}': {e}")
            return None

    def reload_all(self):
        """
        For debug: cleans cache to reload changes without closing the game
        """
        self.cache.clear()
        print(f"[ScriptManager] Cache reloaded")

script_manager = ScriptManager()