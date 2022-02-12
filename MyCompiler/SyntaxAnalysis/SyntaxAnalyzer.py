import LexicalAnalyzer
from GrammarFileLoader import GrammarFileLoader


class SyntaxAnalyzer:
    # This is basically just the parser at this point.
    def __init__(self, parser):
        self.parser = parser
        assert isinstance(self.parser, Parser.BaseParser)

    def process(self, input_tokens):
        derivation = self.parser.produce_derivation(input_tokens)
        return self.parser.to_parse_tree(derivation)


def do_stuff():
    grammar = GrammarFileLoader.load('ANSI C refactored2')
    lexer = LexicalAnalyzer.LexicalAnalyzer.ANSI_C_lexer()
    parser = Parser.LL1Parser(grammar, bypass_checks=False)
    syntax_analyzer = SyntaxAnalyzer(parser)
    tokens = lexer.process(
        """int x;"""
#         """
# int main() {
#    printf("Hello, World!");
#    return 0;
# }
#         """
    )
    tree = syntax_analyzer.process(tokens)
    print(tree)


if __name__ == '__main__':
    do_stuff()