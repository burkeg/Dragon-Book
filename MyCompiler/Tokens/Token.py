from Tokens import Tag


class Token:
    def __init__(self, tag, name, lexeme, value=None, symbol_table_entry=None):
        self.lexeme = lexeme
        assert isinstance(lexeme, str)
        self.name = name
        self.tag = tag
        self.value = value
        self.symbol_table_entry = symbol_table_entry
        assert isinstance(tag, Tag)
        assert isinstance(name, str)