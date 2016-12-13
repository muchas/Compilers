#!/usr/bin/python
from collections import defaultdict
from SymbolTable import SymbolTable, FunctionSymbol, VariableSymbol
import AST

class NodeVisitor(object):
    def __init__(self):
        self.ttype = self.init_ttype()

    def init_ttype(self):
        ttype = defaultdict(lambda: defaultdict(dict))

        for op in ['+', '-', '*', '/', '%', '<', '>', '<<', '>>', '|', '&', '^', '<=', '>=', '==', '!=']:
            ttype[op]['int']['int'] = 'int'

        for op in ['+', '-', '*', '/']:
            ttype[op]['int']['float'] = 'float'
            ttype[op]['float']['int'] = 'float'
            ttype[op]['float']['float'] = 'float'

        for op in ['<', '>', '<=', '>=', '==', '!=']:
            ttype[op]['int']['float'] = 'int'
            ttype[op]['float']['int'] = 'int'
            ttype[op]['float']['float'] = 'int'

        ttype['+']['string']['string'] = 'string'
        ttype['*']['string']['int'] = 'string'

        for op in ['<', '>', '<=', '>=', '==', '!=']:
            ttype[op]['string']['string'] = 'int'

        return ttype

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):  # Called if no explicit visitor function exists for a node.
        if isinstance(node, list):
            for elem in node:
                self.visit(elem)
        else:
            for child in node.children:
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, AST.Node):
                            self.visit(item)
                elif isinstance(child, AST.Node):
                    self.visit(child)

    def get_type(self, operator, type_left, type_right):
        if operator not in self.ttype:
            return None

        if type_left not in self.ttype[operator]:
            return None

        if type_right not in self.ttype[operator][type_left]:
            return None

        return self.ttype[operator][type_left][type_right]


class TypeChecker(NodeVisitor):
    def __init__(self):
        super(TypeChecker, self).__init__()

        self.table = SymbolTable(None, 'root')
        self.current_function = None
        self.current_type = None
        self.isValid = True

    def visit_Integer(self, node):
        return 'int'

    def visit_Float(self, node):
        return 'float'

    def visit_String(self, node):
        return 'string'

    def visit_BinExpr(self, node):
        type_left = self.visit(node.left)
        type_right = self.visit(node.right)
        operator = node.op

        result_type = self.get_type(operator, type_left, type_right)

        if result_type is None:
            return self.raiseItKanaKana("Bad expression {} in line {}".format(node.op, node.line))

        return result_type

    def visit_Variable(self, node):
        symbol = self.table.get(node.name)

        if symbol is None:
            return self.raiseItKanaKana("Undefined symbol {} in line {}".format(node.name, node.line))

        return symbol.type

    def visit_AssignmentInstruction(self, node):
        symbol = self.table.get(node.id)
        expression_type = self.visit(node.expr)

        if symbol is None:
            return self.raiseItKanaKana("Used undefined symbol {} in line {}".format(node.id, node.line))

        if symbol.type == "float" and expression_type == "int":
            return symbol.type

        if expression_type != symbol.type:
            return self.raiseItKanaKana(
                "Bad assignment of {} to {} in line {}.".format(expression_type, symbol.type, node.line)
            )

        return symbol.type

    def visit_GroupedExpression(self, node):
        return self.visit(node.interior)

    def visit_FunctionExpression(self, node):
        if self.table.symbols.get(node.name):
            return self.raiseItKanaKana("Function {} already defined. Line: {}".format(node.name, node.line))

        function = FunctionSymbol(node.name, node.retType)
        self.table.put(node.name, function)

        self.table = self.table.push_scope(node.name)
        self.current_function = function

        if node.args is not None:
            self.visit(node.args)
        self.visit(node.body)

        self.current_function = None
        self.table = self.table.pop_scope()

    def visit_CompoundInstruction(self, node):
        self.table = self.table.push_scope("inner_scope")

        if node.declarations is not None:
            self.visit(node.declarations)
        self.visit(node.instructions)

        self.table = self.table.pop_scope()

    def visit_ArgumentList(self, node):
        for arg in node.children:
            self.visit(arg)

        self.current_function.params = [x.type for x in self.table.symbols.values()]

    def visit_Argument(self, node):
        if self.table.symbols.get(node.name) is not None:
            return self.raiseItKanaKana("Argument {} already defined. Line: {}".format(node.name, node.line))

        self.table.put(node.name, VariableSymbol(node.name, node.type))

    def visit_InvocationExpression(self, node):
        function_symbol = self.table.get(node.name)

        if function_symbol is None or not isinstance(function_symbol, FunctionSymbol):
            return self.raiseItKanaKana("Function {} not defined. Line: {}".format(node.name, node.line))

        if len(node.args) != len(function_symbol.params):
            return self.raiseItKanaKana(
                "Invalid number of arguments in line {}. Expected {}".format(node.line, len(function_symbol.params))
            )

        types = [self.visit(x) for x in node.args.children]

        for actual, expected in zip(types, function_symbol.params):
            if actual != expected and not (actual == "int" and expected == "float"):
                return self.raiseItKanaKana(
                    "Mismatching argument types in line {}. Expected {}, got {}".format(node.line, expected, actual)
                )

        return function_symbol.type

    def visit_ChoiceInstruction(self, node):
        self.visit(node.condition)
        self.visit(node.action)

        if node.alternateAction is not None:
            self.visit(node.alternateAction)

    def visit_WhileInstruction(self, node):
        self.visit(node.condition)
        self.visit(node.instruction)

    def visit_RepeatInstruction(self, node):
        self.visit(node.condition)
        self.visit(node.instructions)

    def visit_ReturnInstruction(self, node):
        if self.current_function is not None:
            expression_type = self.visit(node.expression)

            if self.current_function.type == 'float' and expression_type == 'int':
                return self.current_function.type

            if expression_type != self.current_function.type:
                return self.raiseItKanaKana(
                    "Invalid return type of {} in line {}. Expected {}". \
                        format(expression_type, node.line, self.current_function.type)
                )

            return expression_type

        self.raiseItKanaKana("Return placed outside of a function in line {}".format(node.line))

    def visit_Declaration(self, node):
        self.current_type = node.type
        self.visit(node.inits)
        self.current_type = None

    def visit_Init(self, node):
        expression_type = self.visit(node.expr)

        if (expression_type == self.current_type or
                (expression_type == "int" and self.current_type == "float") or
                (expression_type == "float" and self.current_type == "int")):

            if self.table.symbols.get(node.name) is not None:
                return self.raiseItKanaKana(
                    "Invalid definition of {} in line: {}. Entity redefined".format(node.name, node.line)
                )

            self.table.put(node.name, VariableSymbol(node.name, self.current_type))
        else:
            return self.raiseItKanaKana(
                "Bad assignment of {} to {} in line {}".format(expression_type, self.current_type, node.line)
            )

    def visit_PrintInstruction(self, node):
        self.visit(node.expr)

    def visit_LabeledInstruction(self, node):
        self.visit(node.instr)

    def visit_Program(self, node):
        self.visit(node.program_blocks)

    def visit_ProgramBlockList(self, node):
        for program_block in node.children:
            self.visit(program_block)

    def visit_ProgramBlock(self, node):
        self.visit(node.block)

    def raiseItKanaKana(self, msg):
        self.isValid = False
        print msg
