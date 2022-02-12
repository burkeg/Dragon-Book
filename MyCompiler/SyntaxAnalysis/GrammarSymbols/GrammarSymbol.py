class GrammarSymbol:
    def __init__(self, string):
        self.string = string

    # https://stackoverflow.com/questions/2909106/whats-a-correct-and-good-way-to-implement-hash
    def _key(self):
        return self.string

    def __hash__(self):
        return hash(self._key())

    def __eq__(self, other):
        if isinstance(other, GrammarSymbol):
            return self._key() == other._key()
        return NotImplemented

    def __repr__(self):
        return repr(self.string)

    def __lt__(self, other):
        return self.string < other.string
