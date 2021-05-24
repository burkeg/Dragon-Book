import Tokens.Token


class SymbolTableEntry:
    def __init__(self, token):
        self.token = token
        assert isinstance(token, Tokens.Token.Token)
        token.symbol_table_entry = self

class SymbolTableManager:
    def __init__(self):
        self._symbol_table_root = SymbolTable()

    def curr_table(self):
        return self._symbol_table_root

class SymbolTable:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = []

    def create_symbol(self, token):
        assert isinstance(token, Tokens.Token.Token)
        self.symbols.append(SymbolTableEntry(token))