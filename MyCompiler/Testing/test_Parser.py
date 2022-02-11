from unittest import TestCase

import Grammar
import Parser
import LexicalAnalyzer


class Test(TestCase):
    def test_to_parse_tree(self):
        test_data = \
            [
                # ( # last time I ran this it took 6 and a half hours only to fail...
                #     Grammar.TextbookGrammar('ANSI C'),
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
                    Grammar.TextbookGrammar('4.40_2'),
                    Parser.SLR1Parser,
                    LexicalAnalyzer.LexicalAnalyzer.ANSI_C_lexer(),
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
                    Grammar.TextbookGrammar('4.40'),
                    Parser.SLR1Parser,
                    LexicalAnalyzer.LexicalAnalyzer.ANSI_C_lexer(),
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
                    Grammar.TextbookGrammar('4.55'),
                    Parser.CanonicalLR1Parser,
                    LexicalAnalyzer.LexicalAnalyzer.ANSI_C_lexer(),
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
                    Grammar.TextbookGrammar('4.55'),
                    Parser.SpaceConsumingLALRParser,
                    LexicalAnalyzer.LexicalAnalyzer.ANSI_C_lexer(),
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
