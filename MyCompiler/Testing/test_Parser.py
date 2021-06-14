from unittest import TestCase

import Grammar
import Parser
import LexicalAnalyzer


class Test(TestCase):
    def test_to_parse_tree(self):
        test_data = \
        [
            (
                Grammar.TextbookGrammar('ANSI C'),
                Parser.LR1Parser,
                LexicalAnalyzer.LexicalAnalyzer.ANSI_C_lexer(),
                [
                    """
                    int i;
                    """,
                    """
                    int main()
                    {
                    }
                    """,
                ]
            )
        ]
        for grammar, parser_type, lexer, test_cases in test_data:
            grammar.augment()
            parser = parser_type(grammar)
            for test_case  in test_cases:
                with self.subTest(parser=parser_type, lexer=type(lexer), test_case=test_case):
                    tokens = lexer.process(test_case)
                    list_tokens = list(tokens)
                    print(list_tokens)
                    productions = parser.produce_derivation(iter(list_tokens))
                    tree = parser.to_parse_tree(productions)
                    print(tree)
