from unittest import TestCase

from CanonicalLR1Parser import CanonicalLR1Parser
from GrammarFileLoader import GrammarFileLoader
from LexicalAnalyzer import LexicalAnalyzer
from SLR1Parser import SLR1Parser
from SpaceConsumingLALRParser import SpaceConsumingLALRParser


class Test(TestCase):
    def test_to_parse_tree(self):
        test_data = \
            [
                # ( # last time I ran this it took 6 and a half hours only to fail...
                #     GrammarFileLoader.load('ANSI C'),
                #     Parser.CanonicalLR1Parser,
                #     LexicalAnalyzer.LexicalAnalyzer.ANSI_C_lexer(),
                #     [
                #         """
                #         int main()
                #         {
                #             return 0
                #         }
                #         """,
                #     ]
                # ),
                (
                    GrammarFileLoader.load('4.40_2'),
                    SLR1Parser,
                    LexicalAnalyzer.ANSI_C_lexer(),
                    [
                        """
                        a * b + c
                        """,
                        """
                        a
                        """,
                        """
                        (ab)
                        """,
                        """
                        a*b*c
                        """,
                        """
                        a+b*c
                        """,
                    ]
                ),
                (
                    GrammarFileLoader.load('4.40'),
                    SLR1Parser,
                    LexicalAnalyzer.ANSI_C_lexer(),
                    [
                        """
                        a * b + c
                        """,
                        """
                        a
                        """,
                        """
                        (ab)
                        """,
                        """
                        a*b*c
                        """,
                        """
                        a+b*c
                        """,
                    ]
                ),
                (
                    GrammarFileLoader.load('4.55'),
                    CanonicalLR1Parser,
                    LexicalAnalyzer.ANSI_C_lexer(),
                    [
                        """
                        1 1
                        """,
                        """
                        c 1 1
                        """,
                        """
                        c c c 1 1
                        """,
                        """
                        c 1 c c c 1
                        """,
                        """
                        1 c 1
                        """,
                    ]
                ),
                (
                    GrammarFileLoader.load('4.55'),
                    SpaceConsumingLALRParser,
                    LexicalAnalyzer.ANSI_C_lexer(),
                    [
                        """
                        1 1
                        """,
                        """
                        c 1 1
                        """,
                        """
                        c c c 1 1
                        """,
                        """
                        c 1 c c c 1
                        """,
                        """
                        1 c 1
                        """,
                    ]
                ),
            ]

        for grammar, parser_type, lexer, test_cases in test_data:
            grammar.augment()
            parser = parser_type(grammar)
            for test_case in test_cases:
                with self.subTest(grammar=grammar, parser=parser_type, lexer=type(lexer), test_case=test_case.strip()):
                    tokens = lexer.process(test_case)
                    list_tokens = list(tokens)
                    productions = parser.produce_derivation(iter(list_tokens))
                    tree = parser.to_parse_tree(productions)
                    print(tree)
