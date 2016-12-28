#!/usr/bin/python
from symtable import Symbol


class VariableSymbol(Symbol):
    def __init__(self, name, type):
        self.name = name
        self.type = type


class FunctionSymbol(Symbol):
    def __init__(self, name, type, args):
        self.name = name
        self.type = type
        self.args = args


class SymbolTable(object):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.symbols = {}

    def put(self, name, symbol):
        self.symbols[name] = symbol

    def has_scope_name(self, name):
        if self.name == name:
            return True

        if self.parent:
            return self.parent.has_scope_name(name)

        return False

    def get(self, name):
        return self.symbols.get(name, self.parent.get(name) if self.parent else None)

    def push_scope(self, name):
        return SymbolTable(self, name)

    def pop_scope(self):
        return self.parent
