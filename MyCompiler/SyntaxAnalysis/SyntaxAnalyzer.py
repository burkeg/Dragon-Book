import Parser
import Grammar
import LexicalAnalyzer


class SyntaxAnalyzer:
    # This is basically just the parser at this point.
    def __init__(self, parser):
        self.parser = parser
        assert isinstance(self.parser, Parser.Parser)

    def process(self, input_tokens):
        derivation = self.parser.produce_derivation(input_tokens)
        return self.parser.to_parse_tree(derivation)


def do_stuff():
    grammar = Grammar.TextbookGrammar('4.28')
    lexer = LexicalAnalyzer.LexicalAnalyzer.default_lexer()
    parser = Parser.LL1Parser(grammar)
    syntax_analyzer = SyntaxAnalyzer(parser)
    tokens = lexer.process(
        """
        variable_A*(last_var) + 
        one
        """
    )
    tree = syntax_analyzer.process(tokens)
    print(tree)


if __name__ == '__main__':
    do_stuff()