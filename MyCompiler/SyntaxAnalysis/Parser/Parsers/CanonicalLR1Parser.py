import LexicalAnalyzer
from GrammarFileLoader import GrammarFileLoader
from SLR1Parser import SLR1Parser
from LR1Grammar import LR1Grammar
from CanonicalLRParsingTable import CanonicalLRParsingTable

class CanonicalLR1Parser(SLR1Parser):
    def _prepare_internals(self):
        if not isinstance(self._grammar, LR1Grammar):
            self._grammar = LR1Grammar(
                terminals=self._grammar.terminals,
                nonterminals=self._grammar.nonterminals,
                productions=self._grammar.productions,
                start_symbol=self._grammar.start_symbol,
                prev_start_symbol=self._grammar._prev_start_symbol)
        self._parsing_table = CanonicalLRParsingTable(self._grammar)



def do_stuff():
    grammar = GrammarFileLoader.load('4.55')
    parser = CanonicalLR1Parser(grammar)
    lexer = LexicalAnalyzer.LexicalAnalyzer.ANSI_C_lexer()
    tokens = lexer.process(
        """
        c 0 c 0
        """
    )
    list_tokens = list(tokens)
    productions = parser.produce_derivation(iter(list_tokens))
    list_productions = list(productions)
    tree = parser.to_parse_tree(iter(list_productions))
    print(tree)


if __name__ == '__main__':
    do_stuff()