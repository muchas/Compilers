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

    def visit(self, node, **kwargs):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, **kwargs)

    def generic_visit(self, node, **kwargs):        # Called if no explicit visitor function exists for a node.
        if isinstance(node, list):
            for elem in node:
                self.visit(elem, **kwargs)
        else:
            for child in node.children:
                if isinstance(child, list):
                    for item in child:
                        if isinstance(item, AST.Node):
                            self.visit(item, **kwargs)
                elif isinstance(child, AST.Node):
                    self.visit(child, **kwargs)

    def get_type(self, operator, type_left, type_right):
        if operator not in self.ttype:
            return None

        if type_left not in self.ttype[operator]:
            return None

        if type_right not in self.ttype[operator][type_left]:
            return None

        return self.ttype[operator][type_left][type_right]


class TypeChecker(NodeVisitor):

    WHILE_SCOPE = 'while_instruction'
    REPEAT_SCOPE = 'repeat_instruction'

    LOOP_SCOPES = (WHILE_SCOPE, REPEAT_SCOPE)

    def __init__(self):
        super(TypeChecker, self).__init__()
        
        self.is_valid = True

        self.table = SymbolTable(None, 'root')
        self.current_function = None
        self.current_type = None
        self.returned_type = None
        
    def log_error(self, message):
        self.is_valid = False
        
        print message

    def visit_Integer(self, node, **kwargs):
        return 'int'

    def visit_Float(self, node, **kwargs):
        return 'float'

    def visit_String(self, node, **kwargs):
        return 'string'

    def visit_BinExpr(self, node, **kwargs):
        type_left = self.visit(node.left)
        type_right = self.visit(node.right)
        operator = node.op

        result_type = self.get_type(operator, type_left, type_right)

        if result_type is None:
            self.log_error("Error: Illegal operation, {} {} {}: line {}".format(
                type_left, node.op, type_right, node.line
            ))
            return None

        return result_type

    def visit_Variable(self, node, **kwargs):
        symbol = self.table.get(node.name)

        if symbol is None:
            self.log_error("Error: Usage of undeclared variable '{}': line {}".format(
                node.name, node.line
            ))
            return None

        if isinstance(symbol, FunctionSymbol):
            self.log_error("Error: Function identifier '{0}' used as a variable: line {1}".format(node.name, node.line))

        return symbol.type

    def visit_AssignmentInstruction(self, node, **kwargs):
        symbol = self.table.get(node.id)
        expression_type = self.visit(node.expr)

        if symbol is None:
            self.log_error("Error: Variable '{}' undefined in current scope: line {}".format(
                node.id, node.line
            ))
        elif symbol.type == "float" and expression_type == "int":
            return symbol.type
        elif expression_type and expression_type != symbol.type:
            self.log_error("Error: Illegal assignment of {} to {}: line {}.".format(expression_type, symbol.type, node.line))
            return symbol.type

    def visit_GroupedExpression(self, node, **kwargs):
        return self.visit(node.interior)

    def visit_FunctionExpression(self, node, **kwargs):
        if self.table.symbols.get(node.name):
            self.log_error("Error: Redefinition of function '{}': line {}".format(node.name, node.line))
        else:
            function = FunctionSymbol(node.name, node.retType, node.args)
            self.table.put(node.name, function)

            self.table = self.table.push_scope(node.name)
            self.current_function = function
            self.returned_type = None

            if node.args is not None:
                self.visit(node.args)
            self.visit(node.body, after_fun_def=True)

            self.current_function = None
            self.table = self.table.pop_scope()

            if self.returned_type is None:
                self.log_error("Error: Missing return statement in function '{}' returning {}: line {}".format(
                    node.name, node.retType, node.line
                ))

    def visit_CompoundInstruction(self, node, **kwargs):
        after_fun_def = kwargs.get('after_fun_def')
        if not after_fun_def:
            self.table = self.table.push_scope("inner_scope")

        if node.declarations is not None:
            self.visit(node.declarations)
        self.visit(node.instructions)

        if not after_fun_def:
            self.table = self.table.pop_scope()

    def visit_ArgumentList(self, node, **kwargs):
        for arg in node.children:
            self.visit(arg)

    def visit_Argument(self, node, **kwargs):
        if self.table.symbols.get(node.name) is not None:
            self.log_error("Error: Variable '{}' already declared: line {}".format(node.name, node.line))
        else:
            self.table.put(node.name, VariableSymbol(node.name, node.type))

    def visit_InvocationExpression(self, node, **kwargs):
        function_symbol = self.table.get(node.name)

        if function_symbol is None or not isinstance(function_symbol, FunctionSymbol):
            self.log_error("Error: Call of undefined function '{}': line {}".format(node.name, node.line))
        else:
            if len(node.args) != len(function_symbol.args):
                self.log_error("Error: Improper number of args in {} call: line {}".format(
                    node.name, node.line
                ))

            else:
                types = [self.visit(x) for x in node.args.children]

                for actual, expected in zip(types, function_symbol.args):
                    if actual != expected.type and not (actual == "int" and expected.type == "float"):
                        self.log_error("Error: Improper type of args in {} call: line {}".format(node.name, node.line))
                        break

            return function_symbol.type

    def visit_ChoiceInstruction(self, node, **kwargs):
        self.visit(node.condition)
        self.visit(node.action)

        if node.alternateAction is not None:
            self.visit(node.alternateAction)

    def visit_WhileInstruction(self, node, **kwargs):
        self.visit(node.condition)

        self.table = self.table.push_scope(self.WHILE_SCOPE)
        self.visit(node.instruction)
        self.table = self.table.pop_scope()

    def visit_RepeatInstruction(self, node, **kwargs):
        self.visit(node.condition)

        self.table = self.table.push_scope(self.REPEAT_SCOPE)
        self.visit(node.instructions)
        self.table = self.table.pop_scope()

    def visit_ReturnInstruction(self, node, **kwargs):
        if self.current_function is None:
            self.log_error("Error: return instruction outside a function: line {}".format(node.line))
            return None

        expression_type = self.visit(node.expression)

        if self.current_function.type == 'float' and expression_type == 'int':
            return self.current_function.type

        if expression_type and expression_type != self.current_function.type:
            self.log_error("Error: Improper returned type, expected {}, got {}: line {}".format(
                self.current_function.type, expression_type, node.line
            ))

        self.returned_type = expression_type
        return expression_type

    def visit_Declaration(self, node, **kwargs):
        self.current_type = node.type
        self.visit(node.inits)
        self.current_type = None

    def visit_ContinueInstruction(self, node, **kwargs):
        if not any(self.table.has_scope_name(name) for name in self.LOOP_SCOPES):
            self.log_error("Error: continue instruction outside a loop: line {}".format(node.line))

    def visit_BreakInstruction(self, node, **kwargs):
        if not any(self.table.has_scope_name(name) for name in self.LOOP_SCOPES):
            self.log_error("Error: break instruction outside a loop: line {}".format(node.line))

    def visit_Init(self, node, **kwargs):
        expression_type = self.visit(node.expr)

        definition = self.table.get(node.name)
        if definition is not None and isinstance(definition, FunctionSymbol):
            self.log_error("Error: Function identifier '{0}' used as a variable: line {1}".format(node.name, node.line))
            return None

        if (expression_type == self.current_type or
                (expression_type == "int" and self.current_type == "float") or
                (expression_type == "float" and self.current_type == "int")):

            if self.table.symbols.get(node.name) is not None:
                self.log_error("Error: Variable '{}' already declared: line {}".format(node.name, node.line))
            else:
                self.table.put(node.name, VariableSymbol(node.name, self.current_type))
        else:
            self.log_error("Error: Assignment of {} to {}: line {}".format(expression_type, self.current_type, node.line))

    def visit_PrintInstruction(self, node, **kwargs):
        self.visit(node.expr)

    def visit_LabeledInstruction(self, node, **kwargs):
        self.visit(node.instr)

    def visit_Program(self, node, **kwargs):
        self.visit(node.program_blocks)

    def visit_ProgramBlockList(self, node, **kwargs):
        for program_block in node.children:
            self.visit(program_block)

    def visit_ProgramBlock(self, node, **kwargs):
        self.visit(node.block)
