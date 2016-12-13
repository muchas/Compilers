
import AST
import SymbolTable
from Memory import *
from Exceptions import  *
from visit import *
import sys

sys.setrecursionlimit(10000)


class Interpreter(object):

    def __init__(self):
        self.memory = MemoryStack()

    @on('node')
    def visit(self, node):
        pass

    @when(AST.Program)
    def visit(self, program):
        program.program_blocks.accept(self)

    @when(AST.ProgramBlock)
    def visit(self, program_block):
        program_block.block.accept(self)

    @when(AST.InitList)
    def visit(self, node):
        for child in node.children:
            child.accept(self)

    @when(AST.ExpressionList)
    def visit(self, node):
        for child in node.children:
            child.accept(self)

    @when(AST.InstructionList)
    def visit(self, node):
        for child in node.children:
            child.accept(self)

    @when(AST.ProgramBlockList)
    def visit(self, node):
        for child in node.children:
            child.accept(self)

    @when(AST.DeclarationList)
    def visit(self, node):
        for child in node.children:
            child.accept(self)

    @when(AST.ArgumentList)
    def visit(self, node):
        for child in node.children:
            child.accept(self)

    @when(AST.BinExpr)
    def visit(self, node):
        r1 = node.left.accept(self)
        r2 = node.right.accept(self)
        operators = {
            '+', '-', '/', '*', '>', '>=',
            '<', '<=', '=='
        }

        if node.op in operators:
            return eval('a {} b'.format(node.op), {"a": r1, "b": r2})

    @when(AST.GroupedExpression)
    def visit(self, node):
        return node.interior.accept(self)

    @when(AST.FunctionExpression)
    def visit(self, node):
        self.memory.head[node.name] = node

    @when(AST.Declaration)
    def visit(self, node):
        node.inits.accept(self)

    @when(AST.AssignmentInstruction)
    def visit(self, node):
        expression = node.expr.accept(self)
        self.memory.set(node.id, expression)
        return expression

    @when(AST.Init)
    def visit(self, node):
        expression = node.expr.accept(self)
        self.memory.head[node.name] = expression
        return expression

    @when(AST.WhileInstruction)
    def visit(self, node):
        while node.condition.accept(self):
            try:
                node.instruction.accept(self)
            except BreakException:
                break
            except ContinueException:
                pass

    @when(AST.RepeatInstruction)
    def visit(self, node):
        while True:
            try:
                node.instructions.accept(self)
                if node.condition.accept(self):  # PASCAL STYLE BEACH
                    break
            except BreakException:
                break
            except ContinueException:
                pass

    @when(AST.ChoiceInstruction)
    def visit(self, node):
        if node.condition.accept(self):
            return node.action.accept(self)
        elif node.alternateAction:
            return node.alternateAction.accept(self)

    @when(AST.CompoundInstruction)
    def visit(self, node):
        node.declarations.accept(self)
        node.instructions.accept(self)

    @when(AST.InvocationExpression)
    def visit(self, node):
        function = self.memory.get(node.name)

        function_memory = Memory(node.name)

        for expression, argument in zip(node.args.children, function.args.children):
            function_memory[argument.accept(self)] = expression.accept(self)

        self.memory.push(function_memory)

        try:
            function.body.accept(self)
        except ReturnValueException as e:
            return e.value
        finally:
            self.memory.pop()

    @when(AST.Argument)
    def visit(self, node):
        return node.name

    @when(AST.Integer)
    def visit(self, node):
        return int(node.value)

    @when(AST.Float)
    def visit(self, node):
        return float(node.value)

    @when(AST.String)
    def visit(self, node):
        return node.value

    @when(AST.Variable)
    def visit(self, node):
        return self.memory.get(node.name)

    @when(AST.BreakInstruction)
    def visit(self, node):
        raise BreakException()

    @when(AST.ContinueInstruction)
    def visit(self, node):
        raise ContinueException()

    @when(AST.ReturnInstruction)
    def visit(self, node):
        raise ReturnValueException(node.expression.accept(self))

    @when(AST.PrintInstruction)
    def visit(self, node):
        print node.expr.accept(self)

    @when(AST.LabeledInstruction)
    def visit(self, node):
        pass

