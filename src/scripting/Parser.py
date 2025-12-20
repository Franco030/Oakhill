from src.scripting.Lexer import TokenType
from src.scripting.AST import (
    Program, Assign, FunctionDecl, Block, FunctionCall, 
    Literal, IfStatement, BinaryOp, ReturnStatement,
    ImportStatement, VarDecl, LogicalOp, UnaryOp,
    ListLiteral, IndexAccess, WhileStatement, ForStatement,
    GetAttribute, SetAttribute, StructDecl, DictLiteral,
    PersistAssignment, ExternalCast
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
        raise Exception(f"[Parser] Error: {message} in line {self.peek().line}")
    
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
        
        if self.check(TokenType.STRUCT):
            return self.struct_declaration()
        
        return self.statement()

    def function_declaration(self):
        self.consume(TokenType.FUNC, "'func' was expected")
        name = self.consume(TokenType.IDENTIFIER, "a function name was expected").value
        
        self.consume(TokenType.LPAREN, "'(' was expected after the name")

        parameters = []
        had_default = False
        if not self.check(TokenType.RPAREN):
            while True:
                param_token = self.consume(TokenType.IDENTIFIER, "a parameter was expected")

                default_value = None
                if self.match(TokenType.ASSIGN):
                    default_value = self.expression()
                    had_default = True
                else:
                    if had_default:
                        raise Exception(f"[SyntaxError] Non-default argument '{param_token.value}' follows default argument in function '{name}' (line {param_token.line})")

                parameters.append((param_token.value, default_value))

                if not self.check(TokenType.COMMA): break
                self.advance()

        self.consume(TokenType.RPAREN, "')' was expected")
        
        self.consume(TokenType.LBRACE, "'{' was expected before the block")
        body = self.block()
        return FunctionDecl(name, parameters, body)
    
    def struct_declaration(self):
        self.consume(TokenType.STRUCT, "'struct' was expected")
        name = self.consume(TokenType.IDENTIFIER, "Struct name was expected").value
        self.consume(TokenType.LBRACE, "'{' expected before struct body")

        fields = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            field_name = self.consume(TokenType.IDENTIFIER, "Field name was expected").value
            self.consume(TokenType.SEMICOLON, "';' expected after field name")
            fields.append(field_name)

        self.consume(TokenType.RBRACE, "'}' expected after struct body")
        return StructDecl(name, fields)
    
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
        
        if self.check(TokenType.WHILE):
            return self.while_statement()
        
        if self.check(TokenType.FOR):
            return self.for_statement()
        
        if self.check(TokenType.RETURN):
            return self.return_statement()
        
        if self.check(TokenType.AT) and self.peek_next_token_is(TokenType.PERSIST):
            return self.persist_statement()

        if self.check(TokenType.LBRACE):
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
    
    def while_statement(self):
        self.consume(TokenType.WHILE, "Expected 'while'")
        self.consume(TokenType.LPAREN, "Expected '(' after 'while'")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Expected ')' after condition")

        self.consume(TokenType.LBRACE, "Expected '{' to start while body")
        body = self.block()

        return WhileStatement(condition, body)
    
    def for_statement(self):
        self.consume(TokenType.FOR, "Expected 'for'")

        iterator_token = self.consume(TokenType.IDENTIFIER, "Expected variable name after 'for'")
        self.consume(TokenType.IN, "Expected 'in' after variable name")

        iterable = self.expression()
        
        self.consume(TokenType.LBRACE, "Expected '{' to start for body")
        body = self.block()

        return ForStatement(iterator_token.value, iterable, body)
    
    def persist_statement(self):
        self.consume(TokenType.AT, "Expected '@'")
        self.consume(TokenType.PERSIST, "Expected 'persist'")

        left_side = self.call()

        if not isinstance(left_side, GetAttribute):
            raise Exception(f"[Parser Error] @persist requires a property access (e.g. object.prop) in line {self.peek().line}")
        
        target = left_side.object_node
        prop_name = left_side.property_name

        self.consume(TokenType.ASSIGN, "Expected '='")
        value = self.expression()

        self.consume(TokenType.SEMICOLON, "';' was expected")

        return PersistAssignment(target, prop_name, value)

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
        expr = self.logic_or()

        if self.match(TokenType.ASSIGN):
            value = self.expression()

            if isinstance(expr, Literal):
                return Assign(expr.value, value)
            
            elif isinstance(expr, GetAttribute):
                return SetAttribute(expr.object_node, expr.property_name, value)
            
            raise Exception(f"[Parser Error] Invalid assignment target in line {self.peek().line}")

        return expr
    
    def logic_or(self):
        expr = self.logic_and()
        while self.check(TokenType.OR):
            operator = self.advance().type
            right = self.logic_and()
            expr = LogicalOp(expr, operator, right)
        return expr
    
    def logic_and(self):
        expr = self.equality()
        while self.check(TokenType.AND):
            operator = self.advance().type
            right = self.equality()
            expr = LogicalOp(expr, operator, right)
        return expr

    def equality(self):
        expr = self.comparison()
        while self.check(TokenType.EQUALS) or self.check(TokenType.NE):
            operator = self.advance().type
            right = self.comparison()
            expr = BinaryOp(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.addition()
        while (self.check(TokenType.GT) or self.check(TokenType.LT) or 
               self.check(TokenType.LE) or self.check(TokenType.GE)):
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
        expr = self.unary() 
        while (self.check(TokenType.MUL) or self.check(TokenType.DIV) or
               self.check(TokenType.MOD) or self.check(TokenType.FLOOR_DIV)):
            operator = self.advance().type
            right = self.unary()
            expr = BinaryOp(expr, operator, right)
        return expr

    def primary(self):
        """
        Literals, identifiers, calls
        """
        if self.match(TokenType.NULL):
            return Literal(None)

        if self.check(TokenType.AT):
            self.advance()

            if not self.check(TokenType.IDENTIFIER):
                raise Exception(f"[Parser Error] Expected function call after '@' in line {self.peek().line}")
            
            node = self.call() 

            if isinstance(node, FunctionCall):
                node.is_capture = True
                return node
            else:
                raise Exception(f"[Parser Error] '@' can only be used with function calls or as a property modifier, not variables, in line {self.peek().line}")
        
        if self.check(TokenType.NUMBER) or self.check(TokenType.STRING) or self.check(TokenType.BOOLEAN):
            return Literal(self.advance().value)
            
        if self.check(TokenType.LPAREN):
            self.advance()
            expr = self.expression()
            self.consume(TokenType.RPAREN, "')' was expected")
            return expr
        
        if self.check(TokenType.LBRACKET):
            self.advance()
            elements = []
            if not self.check(TokenType.RBRACKET):
                while True:
                    elements.append(self.expression())
                    if not self.check(TokenType.COMMA): break
                    self.advance()

            self.consume(TokenType.RBRACKET, "Expected ']' after list elements")
            return ListLiteral(elements)
        
        if self.check(TokenType.LBRACE):
            self.consume(TokenType.LBRACE, "Expected '{'")
            pairs = []

            if not self.check(TokenType.RBRACE):
                while True:
                    key = self.expression()
                    self.consume(TokenType.COLON, "Expected ':' after dictionary key")
                    
                    value = self.expression()
                    pairs.append((key, value))

                    if not self.check(TokenType.COMMA): break
                    self.advance()

            self.consume(TokenType.RBRACE, "Expected '}' after dictionary")
            return DictLiteral(pairs)
        
        if self.check(TokenType.IDENTIFIER):
            return Literal(self.advance().value)

        raise Exception(f"[Parser] Unexpected token '{self.peek().type}' in line {self.peek().line}")
    
    def unary(self):
        if self.check(TokenType.AT) and self.peek_next_token_is(TokenType.EXTERNAL):
            self.advance()
            self.advance()

            right = self.unary()
            return ExternalCast(right)

        if self.check(TokenType.NOT) or self.check(TokenType.MINUS):
            operator = self.advance().type
            right = self.unary()
            return UnaryOp(operator, right)
        
        return self.call()

    def call(self):
        expr = self.primary()

        while True:
            if self.match(TokenType.LPAREN):
                expr = self.finish_call(expr)

            elif self.match(TokenType.DOT):
                name_token = self.consume(TokenType.IDENTIFIER, "Expected property name after '.'")
                expr = GetAttribute(expr, name_token.value)

            elif self.match(TokenType.LBRACKET):
                index = self.expression()
                self.consume(TokenType.RBRACKET, "Expected ']' after index")
                expr = IndexAccess(expr, index)

            else:
                break
        
        return expr
    
    def finish_call(self, callee):
        arguments = []
        kwargs = {}

        if not self.check(TokenType.RPAREN):
            while True:
                if (self.check(TokenType.IDENTIFIER) and self.peek_next_token_is(TokenType.ASSIGN)):
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
        
        return FunctionCall(callee, arguments, kwargs)