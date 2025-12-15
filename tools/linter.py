import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.scripting.Lexer import Lexer
    from src.scripting.Parser import Parser
except ImportError as e:
    print(f"1: Import error: {e}")
    sys.exit(1)

def check_code(source_code):
    if not source_code.strip():
        return

    try:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        parser.parse()
    except Exception as e:
        msg = str(e)
        line = 1
        import re
        match = re.search(r'line (\d+)', msg)
        if match:
            line = int(match.group(1))
        
        clean_msg = msg.replace(f"in line {line}", "").strip()
        clean_msg = clean_msg.replace("[Parser Error]", "").strip()
        
        print(f"{line}:{clean_msg}", flush=True)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                check_code(f.read())
    else:
        content = sys.stdin.read()
        check_code(content)