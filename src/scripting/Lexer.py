import re

class TokenType:
    # Keywords
    FUNC = "FUNC"           # func
    IF = "IF"               # if
    ELSE = "ELSE"           # else
    LOOP = "LOOP"           # loop
    RETURN = "RETURN"       # return
    VAR = "VAR"             # var (local or global)
    IMPORT = "IMPORT"       # import
    AND = "AND"             # and
    OR = "OR"               # or
    FOR = "FOR"             # for
    WHILE = "WHILE"         # while
    IN = "IN"               # in
    STRUCT = "STRUCT"       # struct
    PERSIST = "PERSIST"     # persist
    EXTERNAL = "EXTERNAL"   # external

    # Literals and identifiers
    IDENTIFIER = "IDENTIFIER"   # my_function, player_hp
    NUMBER = "NUMBER"           # 10, 3.5
    STRING = "STRING"           # "Hello, world"
    BOOLEAN = "BOOLEAN"         # true, false

    LPAREN = "LPAREN"           # (
    RPAREN = "RPAREN"           # )
    LBRACE = "LBRACE"           # {
    RBRACE = "RBRACE"           # }
    LBRACKET = "LBRACKET"       # [
    RBRACKET = "RBRACKET"       # ]
    COMMA = "COMMA"             # ,
    SEMICOLON = "SEMICOLON"     # ;
    COLON = "COLON"             # :
    ASSIGN = "ASSIGN"           # =
    EQUALS = "EQUALS"           # ==
    GT = "GT"                   # >
    LT = "LT"                   # <
    LE = "LE"                   # <=
    GE = "GE"                   # >=
    NE = "NE"                   # !=
    NOT = "NOT"                 # !
    AT = "AT"                   # @
    DOT = "DOT"                 # .
    MOD = "MOD"                 # %
    FLOOR_DIV = "FLOOR_DIV"     # /~


    PLUS = "PLUS"   # +
    MINUS = "MINUS" # -
    MUL = "MUL"     # *
    DIV = "DIV"     # /

    # Specials
    EOF = "EOF" # End of file

_token_handlers = {}

def register_token(char_key):
    """
    Decorator to register a handler function to a specific character
    """
    def decorator(func):
        _token_handlers[char_key] = func
        return func
    return decorator

class Token:
    def __init__(self, type, value=None, line=0):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        if self.value:
            return f"Token({self.type}, '{self.value}', Line:{self.line})"
        return f"Token({self.type}, Line:{self.line})"
    
class Lexer:
    def __init__(self, source_code):
        self.source = source_code
        self.pos = 0
        self.line = 1
        self.current_char = self.source[0] if self.source else None

        # Reserved keywords. Fast detection
        self.keywords = {
            "func": TokenType.FUNC,
            "if": TokenType.IF,
            "else": TokenType.ELSE,
            "loop": TokenType.LOOP,
            "return": TokenType.RETURN,
            "true": TokenType.BOOLEAN,
            "false": TokenType.BOOLEAN,
            "var": TokenType.VAR,
            "import": TokenType.IMPORT,
            "and": TokenType.AND,
            "or": TokenType.OR,
            "for": TokenType.FOR,
            "while": TokenType.WHILE,
            "in": TokenType.IN,
            "struct": TokenType.STRUCT,
            "persist": TokenType.PERSIST,
            "external": TokenType.EXTERNAL
        }

    def advance(self):
        """
        Advance the pointer one character
        """
        self.pos += 1
        if self.pos < len(self.source):
            self.current_char = self.source[self.pos]
        else:
            self.current_char = None

    def peek(self):
        """
        Looks the next character without advancing (to detect ==)
        """
        peek_pos = self.pos + 1
        if peek_pos < len(self.source):
            return self.source[peek_pos]
        return None
    
    def skip_whitespace(self):
        """
        Any whitespace gets ignored
        """
        while self.current_char is not None and self.current_char.isspace():
            if self.current_char == '\n':
                self.line += 1
            self.advance()

    def skip_comment(self):
        """
        Comments are defined with // and they get ignored
        """
        while self.current_char is not None and self.current_char != '\n':
            self.advance()

    @register_token('(')
    def _handle_lparen(self):
        self.advance()
        return Token(TokenType.LPAREN, line=self.line)

    @register_token(')')
    def _handle_rparen(self):
        self.advance()
        return Token(TokenType.RPAREN, line=self.line)

    @register_token('{')
    def _handle_lbrace(self):
        self.advance()
        return Token(TokenType.LBRACE, line=self.line)

    @register_token('}')
    def _handle_rbrace(self):
        self.advance()
        return Token(TokenType.RBRACE, line=self.line)
    
    @register_token('[')
    def _handle_lbracket(self):
        self.advance()
        return Token(TokenType.LBRACKET, line=self.line)

    @register_token(']')
    def _handle_rbracket(self):
        self.advance()
        return Token(TokenType.RBRACKET, line=self.line)

    @register_token(',')
    def _handle_comma(self):
        self.advance()
        return Token(TokenType.COMMA, line=self.line)

    @register_token(';')
    def _handle_semicolon(self):
        self.advance()
        return Token(TokenType.SEMICOLON, line=self.line)
    
    @register_token(':')
    def _handle_colon(self):
        self.advance()
        return Token(TokenType.COLON, line=self.line)

    @register_token('>')
    def _handle_gt(self):
        self.advance()
        return Token(TokenType.GT, line=self.line)

    @register_token('<')
    def _handle_lt(self):
        self.advance()
        return Token(TokenType.LT, line=self.line)

    @register_token('=')
    def _handle_equals_or_assign(self):
        if self.peek() == '=':
            self.advance(); self.advance()
            return Token(TokenType.EQUALS, line=self.line)
        else:
            self.advance()
            return Token(TokenType.ASSIGN, line=self.line)

    @register_token('/')
    def _handle_slash_or_comment(self):
        if self.peek() == '/':
            self.skip_comment()
            return None
        elif self.peek() == "~":
            self.advance(); self.advance()
            return Token(TokenType.FLOOR_DIV, line=self.line)
        self.advance()
        return Token(TokenType.DIV, line=self.line)
    
    @register_token('+')
    def _handle_plus(self):
        self.advance()
        return Token(TokenType.PLUS, line=self.line)

    @register_token('-')
    def _handle_minus(self):
        self.advance()
        return Token(TokenType.MINUS, line=self.line)

    @register_token('*')
    def _handle_mul(self):
        self.advance()
        return Token(TokenType.MUL, line=self.line)

    @register_token('"')
    def _handle_string(self):
        string_val = ''
        self.advance() # Skip opening "
        while self.current_char is not None and self.current_char != '"':
            string_val += self.current_char
            self.advance()
        self.advance() # Skip closing "
        return Token(TokenType.STRING, string_val, self.line)
    
    @register_token('%')
    def _handle_percent(self):
        self.advance()
        return Token(TokenType.MOD, line=self.line)
    
    @register_token('!')
    def _handle_not_or_ne(self):
        if self.peek() == '=':
            self.advance(); self.advance()
            return Token(TokenType.NE, line=self.line)
        else:
            self.advance()
            return Token(TokenType.NOT, line=self.line)

    @register_token('<')
    def _handle_lt_or_le(self):
        if self.peek() == '=':
            self.advance(); self.advance()
            return Token(TokenType.LE, line=self.line)
        self.advance()
        return Token(TokenType.LT, line=self.line)

    @register_token('>')
    def _handle_gt_or_ge(self):
        if self.peek() == '=':
            self.advance(); self.advance()
            return Token(TokenType.GE, line=self.line)
        self.advance()
        return Token(TokenType.GT, line=self.line)
    
    @register_token('@')
    def _handle_at(self):
        self.advance()
        return Token(TokenType.AT, line=self.line)

    @register_token('.')
    def _handle_dot(self):
        self.advance()
        return Token(TokenType.DOT, line=self.line)

    def make_number(self):
        """
        NUMBER type is either int or float
        """
        num_str = ''
        dot_count = 0

        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TokenType.NUMBER, int(num_str), self.line)
        return Token(TokenType.NUMBER, float(num_str), self.line)

    def make_identifier(self):
        """
        Gets the names of variables or keywords
        """
        id_str = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            id_str += self.current_char
            self.advance()
        
        token_type = self.keywords.get(id_str, TokenType.IDENTIFIER)
        value = id_str if token_type == TokenType.IDENTIFIER else (id_str == "true")

        if token_type == TokenType.BOOLEAN:
            value = (id_str == "true")

        return Token(token_type, value, self.line)
    
    def make_string(self):
        """
        Get the text between quotation marks
        """
        string_val = ''
        self.advance() # Skips the first quotation mark (")

        while self.current_char is not None and self.current_char != '"':
            string_val += self.current_char
            self.advance()

        self.advance() # Skips the last quotation mark (")
        return Token(TokenType.STRING, string_val, self.line)
    
    def tokenize(self):
        tokens = []

        while self.current_char is not None:
            char = self.current_char

            if char.isspace():
                self.skip_whitespace()
                continue

            handler = _token_handlers.get(char)
            if handler:
                token = handler(self) 
                if token:
                    tokens.append(token)
                continue

            if char.isalpha() or char == '_':
                tokens.append(self.make_identifier())
                continue

            if char.isdigit():
                tokens.append(self.make_number())
                continue

            print(f"[Lexer] Illegal character '{char}' in line {self.line}")
            self.advance()
        
        tokens.append(Token(TokenType.EOF, line=self.line))
        return tokens