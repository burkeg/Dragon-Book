from GrammarSymbol import GrammarSymbol


class Nonterminal(GrammarSymbol):
    def derive_from(self, suffix_gen):
        return Nonterminal(f'{self.string}_{str(next(suffix_gen))}')
