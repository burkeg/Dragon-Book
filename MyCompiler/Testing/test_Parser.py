from unittest import TestCase

import Grammar
import Parser
import LexicalAnalyzer


class Test(TestCase):
    def test_to_parse_tree(self):
        test_data = \
            [
                # (
                #     Grammar.TextbookGrammar('ANSI C'),
                #     Parser.CanonicalLR1Parser,
                #     LexicalAnalyzer.LexicalAnalyzer.ANSI_C_lexer(),
                #     [
                #         """
                #         int i;
                #         """,
                #         """
                #         int main()
                #         {
                #         }
                #         """,
                #     ]
                # ),
                # (
                #     Grammar.TextbookGrammar('4.40_2'),
                #     Parser.SLR1Parser,
                #     LexicalAnalyzer.LexicalAnalyzer.ANSI_C_lexer(),
                #     [
                #         """
                #         a * b + c
                #         """,
                #         """
                #         a
                #         """,
                #         """
                #         (ab)
                #         """,
                #         """
                #         a*b*c
                #         """,
                #         """
                #         a+b*c
                #         """,
                #     ]
                # ),
                # (
                #     Grammar.TextbookGrammar('4.40'),
                #     Parser.SLR1Parser,
                #     LexicalAnalyzer.LexicalAnalyzer.ANSI_C_lexer(),
                #     [
                #         """
                #         a * b + c
                #         """,
                #         """
                #         a
                #         """,
                #         """
                #         (ab)
                #         """,
                #         """
                #         a*b*c
                #         """,
                #         """
                #         a+b*c
                #         """,
                #     ]
                # ),
                (
                    Grammar.TextbookGrammar('4.55'),
                    Parser.CanonicalLR1Parser,
                    LexicalAnalyzer.LexicalAnalyzer.ANSI_C_lexer(),
                    [
                        """
                        c c 1 c 1
                        """,
                    ]
                ),
            ]

        for grammar, parser_type, lexer, test_cases in test_data:
            grammar.augment()
            parser = parser_type(grammar)
            print(parser._parsing_table._action_table)
            print(parser._parsing_table._goto_table)
            for test_case in test_cases:
                with self.subTest(parser=parser_type, lexer=type(lexer), test_case=test_case):
                    tokens = lexer.process(test_case)
                    list_tokens = list(tokens)
                    # print(list_tokens)
                    productions = list(parser.produce_derivation(iter(list_tokens)))
                    # print(productions)
                    tree = parser.to_parse_tree(productions)
                    # print(tree)
