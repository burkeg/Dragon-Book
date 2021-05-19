class SymbolTableEntry:
    def __init__(self, name, type):
        self.name = name
        self.type = type
        pass


class SymbolTable:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = dict()

    def add_symbol(self, symbol):
        assert isinstance(symbol, SymbolTableEntry)
        if symbol.name in self.symbols:
            raise Exception('Added same symbol twice in the same scope')

        self.symbols[symbol.name] = symbol

    def find_symbol(self, name):
        curr_table = self
        while curr_table is not None:
            if name in self.symbols:
                return self.symbols
            curr_table = self.parent