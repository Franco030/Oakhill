from src.scripting.Lexer import TokenType
from src.scripting.AST import (
    Program, FunctionDecl, Block, FunctionCall, 
    Literal, IfStatement, BinaryOp, ReturnStatement,
    ImportStatement, VarDecl
)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        """
        Entry point, generates a Program node
        """
        declarations = []
        while not self.is_at_end():
            declarations.append(self.declaration())
        return Program(declarations)

    # Tokens navigation
    def peek(self):
        return self.tokens[self.current]
    
    def peek_next_token_is(self, type):
        if self.current + 1 >= len(self.tokens): return False
        return self.tokens[self.current + 1].type == type

    def previous(self):
        return self.tokens[self.current - 1]

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def check(self, type):
        if self.is_at_end(): return False
        return self.peek().type == type

    def consume(self, type, message):
        if self.check(type):
            return self.advance()
        raise Exception(f"[Parser Error] {message} in line {self.peek().line}")
    
    def match(self, token_type):
        if self.check(token_type):
            self.advance()
            return True
        return False

    # Grammar rules

    def declaration(self):
        """
        Handles 'func name() { ... }'
        import (module_name)
        var x = 2
        """

        if self.check(TokenType.VAR):
            return self.var_declaration()

        if self.check(TokenType.IMPORT):
            return self.import_statement()

        if self.check(TokenType.FUNC):
            return self.function_declaration()
        
        return self.statement()

    def function_declaration(self):
        self.consume(TokenType.FUNC, "'func' was expected")
        name = self.consume(TokenType.IDENTIFIER, "a function name was expected").value
        
        self.consume(TokenType.LPAREN, "'(' was expected after the name")

        parameters = []
        if not self.check(TokenType.RPAREN):
            while True:
                param_token = self.consume(TokenType.IDENTIFIER, "a parameter was expected")
                parameters.append(param_token.value)

                if not self.check(TokenType.COMMA): break
                self.advance()
        self.consume(TokenType.RPAREN, "')' was expected")
        
        self.consume(TokenType.LBRACE, "'{' was expected before the block")
        body = self.block()
        return FunctionDecl(name, parameters, body)
    
    def var_declaration(self):
        self.consume(TokenType.VAR, "'var' was expected")
        name_token = self.consume(TokenType.IDENTIFIER, "name of variable was expected")

        initializer = None
        if self.match(TokenType.ASSIGN):
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "';' was expected after the variable")
        return VarDecl(name_token.value, initializer)

    def block(self):
        """
        Handles '{ stmt1; stmt2; }'
        """
        
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            statements.append(self.declaration())
        
        self.consume(TokenType.RBRACE, "'}' was expected at the end of the block")
        return Block(statements)

    def statement(self):
        if self.check(TokenType.IF):
            return self.if_statement()
        
        if self.check(TokenType.RETURN):
            return self.return_statement()

        if self.check(TokenType.LBRACE): # Nested block
            self.consume(TokenType.LBRACE, "")
            return self.block()
        
        return self.expression_statement()

    def if_statement(self):
        self.consume(TokenType.IF, "'if' was expected")
        self.consume(TokenType.LPAREN, "'(' was expected after 'if'")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "')' was expected after the condition")
        
        then_branch = self.statement()
        else_branch = None
        
        if self.check(TokenType.ELSE):
            self.advance()
            else_branch = self.statement()
            
        return IfStatement(condition, then_branch, else_branch)

    def expression_statement(self):
        """
        expression statement: 'play_sound();'
        """
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "';' was expected at the end of the sentence")
        return expr
    
    def return_statement(self):
        self.consume(TokenType.RETURN, "return was expected")
        value = None

        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "';' was expected after return")
        return ReturnStatement(value)
    
    def import_statement(self):
        self.consume(TokenType.IMPORT, "'import' was expected")
        path_token = self.consume(TokenType.STRING, "the name of the file between quotation marks was expected")
        self.consume(TokenType.SEMICOLON, "';' was expected after the import")
        return ImportStatement(path_token.value)

    def expression(self):
        return self.equality()

    def equality(self):
        """
        Handles comparisons of type: x == y
        """
        expr = self.comparison()
        while self.check(TokenType.EQUALS): # We may add, Not Equals here
            operator = self.advance().type
            right = self.comparison()
            expr = BinaryOp(expr, operator, right)
        return expr

    def comparison(self):
        """
        Handles comparisons of type: x > y.
        Calls addition instead of 'primary'
        """
        expr = self.addition()
        while self.check(TokenType.GT) or self.check(TokenType.LT):
            operator = self.advance().type
            right = self.addition()
            expr = BinaryOp(expr, operator, right)
        return expr
    
    def addition(self):
        """
        Handles + and - (low priority)
        """
        expr = self.multiplication()
        while self.check(TokenType.PLUS) or self.check(TokenType.MINUS):
            operator = self.advance().type
            right = self.multiplication()
            expr = BinaryOp(expr, operator, right)
        return expr
    
    def multiplication(self):
        """
        Handles * and / (high priority)
        """
        expr = self.primary()
        while self.check(TokenType.MUL) or self.check(TokenType.DIV):
            operator = self.advance().type
            right = self.primary()
            expr = BinaryOp(expr, operator, right)
        return expr

    def primary(self):
        """
        Literals, identifiers, calls
        """
        if self.check(TokenType.NUMBER) or self.check(TokenType.STRING) or self.check(TokenType.BOOLEAN):
            return Literal(self.advance().value)
            
        if self.check(TokenType.IDENTIFIER):
            return self.function_call_or_var()
            
        if self.check(TokenType.LPAREN):
            self.advance()
            expr = self.expression()
            self.consume(TokenType.RPAREN, "')' was expected")
            return expr

        raise Exception(f"[Parser] Unexpected token '{self.peek().type}' in line {self.peek().line}")

    def function_call_or_var(self):
        token_id = self.advance()

        if self.check(TokenType.LPAREN):
            self.advance()
            
            arguments = []
            kwargs = {}

            if not self.check(TokenType.RPAREN):
                while True:
                    if (self.check(TokenType.IDENTIFIER) and 
                        self.peek_next_token_is(TokenType.ASSIGN)):
                        
                        arg_name = self.advance().value
                        self.consume(TokenType.ASSIGN, "Expected '='")
                        arg_value = self.expression()
                        
                        kwargs[arg_name] = arg_value
                    else:
                        if len(kwargs) > 0:
                            raise Exception(f"[ParserError] Positional argument after keyword argument in line {self.peek().line}")
                        
                        arguments.append(self.expression())

                    if not self.check(TokenType.COMMA): break
                    self.advance()

            self.consume(TokenType.RPAREN, "')' was expected")
            return FunctionCall(token_id.value, arguments, kwargs)
        else:
            return Literal(token_id.value)