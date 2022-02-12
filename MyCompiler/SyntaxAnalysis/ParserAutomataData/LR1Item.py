from Terminal import Terminal
from LR0Item import LR0Item


class LR1Item(LR0Item):
    def __init__(self, A, production, dot_position, lookahead):
        super().__init__(A, production, dot_position)
        assert isinstance(lookahead, Terminal)
        self.lookahead = lookahead

    def __repr__(self):
        ret_str = f'{repr(self.A)} -> '
        production_strs = []
        for term in self.production:
            production_strs.append(repr(term))
        production_strs.insert(self.dot_position, '.')
        return f"LR1Item({ret_str + ' '.join(production_strs)}, {self.lookahead})"

    # https://stackoverflow.com/questions/2909106/whats-a-correct-and-good-way-to-implement-hash
    def _key(self):
        return self.A, self.production, self.dot_position, self.lookahead
