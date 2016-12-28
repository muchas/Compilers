
FUNCTION_MEMORY_PREFIX = "function"


class Memory(dict):

    def __init__(self, name, **kwargs):
        super(Memory, self).__init__(**kwargs)
        self.name = name


class MemoryStack(object):
                                                                             
    def __init__(self, memory=None):
        self.stack = [memory if memory else Memory("default")]

    def get(self, name, default=None):
        for memory in reversed(self.stack):
            if name in memory:
                return memory[name]
            elif memory.name.startswith(FUNCTION_MEMORY_PREFIX):
                break
        return default

    def insert(self, name, value):
        self.stack[-1][name] = value

    def set(self, name, value):
        for memory in reversed(self.stack):
            if name in memory:
                memory[name] = value
                return True
            elif memory.name.startswith(FUNCTION_MEMORY_PREFIX):
                return False

    def push(self, memory):
        self.stack.append(memory)

    def pop(self):
        return self.stack.pop()
