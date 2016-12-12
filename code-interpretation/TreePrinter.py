import AST


def addToClass(cls):
    def decorator(func):
        setattr(cls, func.__name__,func)
        return func
    return decorator


class TreePrinter:

    @addToClass(AST.Node)
    def printTree(self, indent=0):
        raise Exception("printTree not defined in class " + self.__class__.__name__)

    @addToClass(AST.Const)
    def printTree(self, indent=0):
        return "| " * indent + str(self.value) + "\n"

    @addToClass(AST.ExpressionList)
    def printTree(self, indent=0):
        return "".join(x.printTree(indent+1) for x in self.children)

    @addToClass(AST.ArgumentList)
    def printTree(self, indent=0):
        return "".join(x.printTree(indent) for x in self.children)

    @addToClass(AST.GroupedExpression)
    def printTree(self, indent=0):
        return self.interior.printTree(indent)

    @addToClass(AST.Argument)
    def printTree(self, indent=0):
        return "| " * indent + "ARG " + self.name + "\n"

    @addToClass(AST.BinExpr)
    def printTree(self, indent=0):
        return "| " * indent + self.op + "\n" + self.left.printTree(indent + 1) + self.right.printTree(indent + 1)

    @addToClass(AST.CompoundInstruction)
    def printTree(self, indent=0):
        return ("" if self.declarations is None else self.declarations.printTree(indent + 1)) + \
            self.instructions.printTree(indent + 1)

    @addToClass(AST.LabeledInstruction)
    def printTree(self, indent=0):
        return "| " * indent + "LABEL\n" + "| " * (indent + 1) + str(self.id) + "\n" + \
               self.instr.printTree(indent + 1)

    @addToClass(AST.InvocationExpression)
    def printTree(self, indent=0):
        return "| " * indent + "FUNCALL\n" + "| " * (indent + 1) + str(self.name) + "\n" + \
            self.args.printTree(indent+1)

    @addToClass(AST.DeclarationList)
    def printTree(self, indent=0):
        return "".join(x.printTree(indent) for x in self.declarations)

    @addToClass(AST.Declaration)
    def printTree(self, indent=0):
        return "| " * indent + "DECL\n" + self.inits.printTree(indent+1)

    @addToClass(AST.FunctionExpression)
    def printTree(self, indent=0):
        return "| " * indent + "FUNDEF\n" + "| " * (indent + 1) + str(self.name) + "\n" + \
               "| " * (indent + 1) + "RET " + str(self.retType) + "\n" + self.args.printTree(indent + 1) + \
               self.body.printTree(indent)

    @addToClass(AST.InitList)
    def printTree(self, indent=0):
        return "".join(x.printTree(indent) for x in self.children)

    @addToClass(AST.Init)
    def printTree(self, indent=0):
        return "| " * indent + "=\n" + "| " * (indent+1) + str(self.name) + "\n" + \
            self.expr.printTree(indent + 1)

    @addToClass(AST.ChoiceInstruction)
    def printTree(self, indent=0):
        return "| " * indent + "IF\n" + self.condition.printTree(indent + 1) + self.action.printTree(
            indent + 1) + \
               ("" if self.alternateAction is None else "| " * indent + "ELSE\n" +
                                                        self.alternateAction.printTree(indent + 1))

    @addToClass(AST.InstructionList)
    def printTree(self, indent=0):
        return "".join(x.printTree(indent) for x in self.children)

    @addToClass(AST.PrintInstruction)
    def printTree(self, indent=0):
        return "| " * indent + "PRINT\n" + self.expr.printTree(indent + 1)

    @addToClass(AST.AssignmentInstruction)
    def printTree(self, indent=0):
        return "| " * indent + "=\n" + "| " * (indent + 1) + str(self.id) + "\n" + \
            self.expr.printTree(indent + 1)
				
    @addToClass(AST.WhileInstruction)
    def printTree(self, indent=0):
        return "| " * indent + "WHILE\n" + self.condition.printTree(indent + 1) + self.instruction.printTree(indent)
		
    @addToClass(AST.RepeatInstruction)
    def printTree(self, indent=0):
        return "| " * indent + "REPEAT\n" + self.instructions.printTree(indent + 1) + "| " * indent + \
            "UNTIL\n" + self.condition.printTree(indent + 1)

    @addToClass(AST.ReturnInstruction)
    def printTree(self, indent=0):
        return "| " * indent + "RETURN\n" + self.expression.printTree(indent + 1)

    @addToClass(AST.BreakInstruction)
    def printTree(self, indent=0):
        return "| " * indent + "BREAK\n"

    @addToClass(AST.ContinueInstruction)
    def printTree(self, indent=0):
        return "| " * indent + "CONTINUE\n"

    @addToClass(AST.Program)
    def printTree(self, indent=0):
        return self.program_blocks.printTree(indent)

    @addToClass(AST.ProgramBlockList)
    def printTree(self, indent=0):
        return "".join(x.printTree(indent) for x in self.children)

    @addToClass(AST.ProgramBlock)
    def printTree(self, indent=0):
        return self.block.printTree(indent)
