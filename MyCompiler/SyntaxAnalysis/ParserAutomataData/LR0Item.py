from Nonterminal import Nonterminal


class LR0Item:
    def __init__(self, A, production, dot_position):
        assert isinstance(A, Nonterminal)
        assert isinstance(production, tuple)
        assert isinstance(dot_position, int)
        self.A = A
        self.production = production
        self.dot_position = dot_position

    def __repr__(self):
        ret_str = f'{repr(self.A)} -> '
        production_strs = []
        for term in self.production:
            production_strs.append(repr(term))
        production_strs.insert(self.dot_position, '.')
        return f"LR0Item({ret_str + ' '.join(production_strs)})"

    # https://stackoverflow.com/questions/2909106/whats-a-correct-and-good-way-to-implement-hash
    def _key(self):
        return self.A, self.production, self.dot_position

    def __hash__(self):
        return hash(self._key())

    def __eq__(self, other):
        if isinstance(other, LR0Item):
            return hash(self) == hash(other)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, LR0Item):
            return self._key() < other._key()
        return NotImplemented
