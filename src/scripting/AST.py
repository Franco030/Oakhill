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
    def __init__(self, name, body):
        self.name = name
        self.body = body # Block node

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements # Statements list

class IfStatement(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class FunctionCall(ASTNode):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments # Value list

class Literal(ASTNode):
    def __init__(self, value):
        self.value = value

class BinaryOp(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator # TokenType (GT, LT, EQUALS...)
        self.right = right