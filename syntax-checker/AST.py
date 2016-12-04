
class Node(object):

    def accept(self, visitor):
        return visitor.visit(self)

    def __init__(self):
        self.children = ()

    def __str__(self):
        return self.printTree()


class NodeList(Node):
    def __init__(self):
        super(NodeList, self).__init__()

        self.children = []

    def append(self, child):
        self.children.append(child)


class Const(Node):
    def __init__(self, value):
        super(Const, self).__init__()
        self.value = value


class Integer(Const):
    pass


class Float(Const):
    pass


class String(Const):
    pass


class Variable(Node):
    pass


class BinExpr(Node):
    def __init__(self, left, op, right):
        super(BinExpr, self).__init__()

        self.left = left
        self.op = op
        self.right = right

        # if you want to use somewhere generic_visit method instead of visit_XXX in visitor
        # definition of children field is required in each class from AST
        self.children = (left, right)


class ExpressionList(NodeList):
    pass


class GroupedExpression(Node):
    def __init__(self, interior):
        super(GroupedExpression, self).__init__()

        self.interior = interior


class FunctionExpression(Node):
    def __init__(self, retType, name, args, body):
        super(FunctionExpression, self).__init__()

        self.retType = retType
        self.name = name
        self.args = args
        self.body = body


class DeclarationList(Node):
    def __init__(self):
        super(DeclarationList, self).__init__()

        self.declarations = []

    def append(self, declaration):
        self.declarations.append(declaration)


class Declaration(Node):
    def __init__(self, type, inits):
        super(Declaration, self).__init__()

        self.type = type
        self.inits = inits


class InvocationExpression(Node):
    def __init__(self, name, args):
        super(InvocationExpression, self).__init__()

        self.name = name
        self.args = args


class Argument(Node):
    def __init__(self, type, name):
        super(Argument, self).__init__()

        self.type = type
        self.name = name


class ArgumentList(NodeList):
    pass


class InitList(NodeList):
    pass


class Init(Node):
    def __init__(self, name, expr):
        super(Init, self).__init__()

        self.name = name
        self.expr = expr


class InstructionList(NodeList):
    pass


class PrintInstruction(Node):
    def __init__(self, expr):

        super(PrintInstruction, self).__init__()
        self.expr = expr


class LabeledInstruction(Node):
    def __init__(self, id, instr):
        super(LabeledInstruction, self).__init__()

        self.id = id
        self.instr = instr


class AssignmentInstruction(Node):
    def __init__(self, id, expr):
        super(AssignmentInstruction, self).__init__()

        self.id = id
        self.expr = expr


class CompoundInstruction(Node):
    def __init__(self, declarations, instructions):
        super(CompoundInstruction, self).__init__()

        self.declarations = declarations
        self.instructions = instructions


class ChoiceInstruction(Node):
    def __init__(self, condition, action, alternateAction=None):
        super(ChoiceInstruction, self).__init__()

        self.condition = condition
        self.action = action
        self.alternateAction = alternateAction


class RepeatInstruction(Node):
    def __init__(self, instructions, condition):
        super(RepeatInstruction, self).__init__()

        self.instructions = instructions
        self.condition = condition


class WhileInstruction(Node):
    def __init__(self, condition, instruction):
        super(WhileInstruction, self).__init__()

        self.condition = condition
        self.instruction = instruction


class ReturnInstruction(Node):
    def __init__(self, expression):
        super(ReturnInstruction, self).__init__()

        self.expression = expression


class BreakInstruction(Node):
    pass


class ContinueInstruction(Node):
    pass


class Program(Node):
    def __init__(self, program_blocks):
        super(Program, self).__init__()

        self.program_blocks = program_blocks


class ProgramBlockList(NodeList):
    pass


class ProgramBlock(Node):
    def __init__(self, block):
        super(ProgramBlock, self).__init__()

        self.block = block


