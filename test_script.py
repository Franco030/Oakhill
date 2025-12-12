from src.managers.ScriptManager import script_manager
from src.scripting.Interpreter import Interpreter

class MockComponents: pass 

print("--- Probando ScriptManager ---")

ast = script_manager.get_script("test_npc")

if ast:
    print("¡ÉXITO! El script se cargó y es un Árbol válido.")
    print(ast)
    
    print("\n--- Pidiendo el script de nuevo (Caché) ---")
    ast2 = script_manager.get_script("test_npc")
else:
    print("FALLO: No se pudo cargar el script. Revisa la ruta 'data/scripts/'.")