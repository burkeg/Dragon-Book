from GrammarSymbol import GrammarSymbol
from Tokens import BaseToken


class Terminal(GrammarSymbol):
    _epsilon = None
    _end = None
    def __init__(self, string=None, token=None):
        self.token = None
        assert string is not None or token is not None
        if token is not None and string is not None:
            assert isinstance(token, BaseToken)
            self.token = token
            self.string = string
        elif string is not None:
            self.token = BaseToken.create(string)
            self.string = f"'{self.token.lexeme}'"
        elif token is not None:
            self.token = token
            self.string = f"'{self.token.lexeme}'"
        else:
            raise Exception('Not a valid terminal')
        super().__init__(self.string)

    def __str__(self):
        return self.string

    __repr__ = __str__


epsilon_terminal = Terminal(string='ε')
end_terminal = Terminal(string='$')
