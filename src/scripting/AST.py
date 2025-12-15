class ASTNode:
    """
    Base class for every node in the tree
    """
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"
    
class Program(ASTNode):
    def __init__(self, declarations):
        self.declarations = declarations # Function's list

class FunctionDecl(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body # Block node

class ReturnStatement(ASTNode):
    def __init__(self, value):
        self.value = value

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements # Statements list

class IfStatement(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class FunctionCall(ASTNode):
    def __init__(self, name, arguments, kwargs=None):
        self.name = name
        self.arguments = arguments # Value list
        self.kwargs = kwargs or {}

class Literal(ASTNode):
    def __init__(self, value):
        self.value = value

class BinaryOp(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator # TokenType (GT, LT, EQUALS...)
        self.right = right

class ImportStatement(ASTNode):
    def __init__(self, module_name):
        self.module_name = module_name

class VarDecl(ASTNode):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

class UnaryOP(ASTNode):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right