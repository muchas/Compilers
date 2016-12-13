

class Memory(dict):

    def __init__(self, name, **kwargs):
        super(Memory, self).__init__(**kwargs)
        self.name = name


class MemoryStack(object):
                                                                             
    def __init__(self, memory=None):
        self.stack = [memory if memory else Memory("base")]

    def get(self, name):
        for memory in reversed(self.stack):
            if name in memory:
                return memory[name]

    def insert(self, name, value):
        self.stack[-1].put(name, value)

    def set(self, name, value):
        for memory in reversed(self.stack):
            if name in memory:
                memory[name] = value
                break

    def push(self, memory):
        self.stack.append(memory)

    def pop(self):
        return self.stack.pop()

    @property
    def head(self):
        return self.stack[-1]
