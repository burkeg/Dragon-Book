from Tokens import EmptyToken


class ParseTree:
    def __init__(self, symbol):
        self.symbol = symbol
        self.children = []

    # https://stackoverflow.com/questions/20242479/printing-a-tree-data-structure-in-python
    def __str__(self, level=0):
        ret = "|   "*level+repr(self)+"\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret

    def __repr__(self):
        if isinstance(self.symbol, EmptyToken):
            return 'ε'
        return repr(self.symbol)
