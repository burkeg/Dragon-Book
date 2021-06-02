from unittest import TestCase

import Grammar

class TestGrammar(TestCase):
    def test_from_string(self):
        grammars = [
            (
                """
                E -> E '+' T | T
                T -> T '*' F
                    | F
                F -> '(' E ')' | 'id'
                """,
                {

                }
            ),
            (
                """
                Ep -> E
                E -> E '+' T | T
                T -> T '*' F
                    | F
                F -> '(' E ')' | 'id'
                """,
                {

                }
            ),
            (
                """
                Ep -> E
                E -> E '+' {test} T | T
                T -> T '*' F
                    | F
                F -> '(' E ')' | 'id'
                """,
                {
                    'test':
                        lambda: print('test')
                }
            ),
        ]

        for grammar, action_dict in grammars:
            with self.subTest(grammar=grammar):
                g = Grammar.Grammar.from_string(grammar, action_dict)
                print('productions: ', g.productions)
