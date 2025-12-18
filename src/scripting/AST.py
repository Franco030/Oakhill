class ASTNode:
    """
    Base class for every node in the tree
    """
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"
    
class Program(ASTNode):
    def __init__(self, declarations):
        self.declarations = declarations # Function's list

class Assign(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

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
    def __init__(self, callee, arguments, kwargs=None):
        self.callee = callee
        self.arguments = arguments
        self.kwargs = kwargs if kwargs else {}

class GetAttribute(ASTNode):
    def __init__(self, object_node, property_name):
        self.object_node = object_node
        self.property_name = property_name

class SetAttribute(ASTNode):
    def __init__(self, object_node, property_name, value):
        self.object_node = object_node
        self.property_name = property_name
        self.value = value

class Literal(ASTNode):
    def __init__(self, value):
        self.value = value

class BinaryOp(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator # TokenType (GT, LT, EQUALS...)
        self.right = right

class LogicalOp(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right    

class ImportStatement(ASTNode):
    def __init__(self, module_name):
        self.module_name = module_name

class VarDecl(ASTNode):
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

class UnaryOp(ASTNode):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

class ListLiteral(ASTNode):
    def __init__(self, elements):
        self.elements = elements

class IndexAccess(ASTNode):
    def __init__(self, target, index):
        self.target = target
        self.index = index

class WhileStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class ForStatement(ASTNode):
    def __init__(self, iterator_name, iterable, body):
        self.iterator_name = iterator_name
        self.iterable = iterable
        self.body = body

class StructDecl(ASTNode):
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

class DictLiteral(ASTNode):
    def __init__(self, pairs):
        self.pairs = pairs

# Until now I was delaying the fact that I had to make "custom" nodes. All of the other ones were kind of global
# Every programming languages needs the above nodes, but this one is completely to make my life easier with the game
# I'll see how this goes
class PersistAssignment(ASTNode):
    def __init__(self, target, property_name, value):
        self.target = target
        self.property_name = property_name
        self.value = value