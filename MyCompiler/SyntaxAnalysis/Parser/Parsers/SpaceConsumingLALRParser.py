from CanonicalLR1Parser import CanonicalLR1Parser
from LALRGrammar import LALRGrammar
from SpaceConsumingLALRParsingTable import SpaceConsumingLALRParsingTable


class SpaceConsumingLALRParser(CanonicalLR1Parser):
    def _prepare_internals(self):
        if not isinstance(self._grammar, LALRGrammar):
            self._grammar = LALRGrammar(
                terminals=self._grammar.terminals,
                nonterminals=self._grammar.nonterminals,
                productions=self._grammar.productions,
                start_symbol=self._grammar.start_symbol,
                prev_start_symbol=self._grammar._prev_start_symbol)
        self._parsing_table = SpaceConsumingLALRParsingTable(self._grammar)
