from AmbiguousLALRParsingTable import AmbiguousLALRParsingTable, Disambiguator
from SpaceConsumingLALRParser import SpaceConsumingLALRParser
from LALRGrammar import LALRGrammar


class AmbiguousLALRParser(SpaceConsumingLALRParser):
    def __init__(self, grammar, disambiguator):
        assert isinstance(disambiguator, Disambiguator)
        self._disambiguator = disambiguator
        super().__init__(grammar=grammar)

    def _prepare_internals(self):
        if not isinstance(self._grammar, LALRGrammar):
            self._grammar = LALRGrammar(
                terminals=self._grammar.terminals,
                nonterminals=self._grammar.nonterminals,
                productions=self._grammar.productions,
                start_symbol=self._grammar.start_symbol,
                prev_start_symbol=self._grammar._prev_start_symbol)
        self._parsing_table = AmbiguousLALRParsingTable(self._grammar, self._disambiguator)
