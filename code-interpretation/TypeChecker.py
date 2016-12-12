#!/usr/bin/python
from collections import defaultdict
from symtable import SymbolTable

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

    def generic_visit(self, node):        # Called if no explicit visitor function exists for a node.
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

    def visit_Integer(self, node):
            return 'int'

    def visit_Float(self, node):
        return 'float'

    def visit_String(self, node):
        return 'string'

    def visit_BinExpr(self, node):
        type_left = self.visit(node.left)
        type_right = self.visit(node.right)
        op = node.op

        type = self.get_type(op, type_left, type_right)

        if type is None:
            print "Bad expression {} in line {}".format(node.op, node.line)

        return type

    def visit_RelExpr(self, node):
        type1 = self.visit(node.left)
        type2 = self.visit(node.right)
