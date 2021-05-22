from Tokens.Token import Token


class SymbolTableEntry:
    def __init__(self, token=None):
        self.token = token
        assert isinstance(token, Token)
        token.symbol_table_entry = self

class SymbolTableManager:
    def __init__(self):
        self.symbol_table_root = SymbolTable()

class SymbolTable:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = []

    def create_symbol(self, token):
        assert isinstance(token, Token)
        self.symbols.append(SymbolTableEntry())