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

    def test_left_factored(self):
        grammars = [
            """
            stmt -> 'if' expr 'then' stmt 'else' stmt
                |  'if' expr 'then' stmt
            """,
            """
            S -> 'i' E 't' S | 'i' E 't' S 'e' S | 'a'
            E -> 'b'
            """,
        ]

        for grammar in grammars:
            with self.subTest(grammar=grammar):
                g = Grammar.Grammar.from_string(grammar)
                print('Before:\n', g)
                left_factored = g.left_factored()
                print('After:\n', left_factored)

                # The problem of determining if two grammars produce the same language is
                # undecidable. I'm not going to make any assertion in this test
                # and will rely on manual inspection that these match the outputs
                # in the textbook.

    def test_without_left_recursion(self):
        grammars = [
            """
            S -> A 'a' | 'b'
            A -> A 'c' | S 'd' | 'ε'
            """,
        ]

        for grammar in grammars:
            with self.subTest(grammar=grammar):
                g = Grammar.Grammar.from_string(grammar)
                print('Before:\n', g)
                without_left_recursion = g.without_left_recursion()
                print('After:\n', without_left_recursion)

                # The problem of determining if two grammars produce the same language is
                # undecidable. I'm not going to make any assertion in this test
                # and will rely on manual inspection that these match the outputs
                # in the textbook.

    def test_first(self):
        grammars = [
            (
                # """
                # S -> 'c' A 'd'
                # A -> 'a' 'b' | 'a'
                # """
                Grammar.TextbookGrammar('4.29'),
                [
                    (
                        Grammar.Nonterminal('S'),
                        {'c'}
                    ),
                    (
                        Grammar.Nonterminal('A'),
                        {'a'}
                    ),
                ]
            ),
            (
                # """
                # S -> A 'a' | 'b'
                # A -> A 'c' | S 'd' | 'ε'
                # """
                Grammar.TextbookGrammar('4.18'),
                [
                    (
                        Grammar.Nonterminal('S'),
                        {'a', 'b', 'c'}
                    ),
                    (
                        Grammar.Nonterminal('A'),
                        {'a', 'b', 'c', 'ε'}
                    ),
                ]
            ),
            (
                # """
                # S -> A 'a' | 'b'
                # A -> A 'c' | S 'd' | 'ε'
                # """
                # But with the left recursion removal algorithm applied.
                Grammar.TextbookGrammar('4.20'),
                [
                    (
                        Grammar.Nonterminal('S'),
                        {'a', 'b', 'c'}
                    ),
                    (
                        Grammar.Nonterminal('A'),
                        {'a', 'b', 'c', 'ε'}
                    ),
                ]
            ),
            (
                # """
                # E -> T Ep
                # Ep -> '+' T Ep | 'ε'
                # T -> F Tp
                # Tp -> '*' F Tp | 'ε'
                # F -> '(' E ')' | 'id'
                # """
                Grammar.TextbookGrammar('4.28'),
                [
                    (
                        Grammar.Nonterminal('E'),
                        {'(', 'id'}
                    ),
                    (
                        Grammar.Nonterminal('Ep'),
                        {'+', 'ε'}
                    ),
                    (
                        Grammar.Nonterminal('T'),
                        {'(', 'id'}
                    ),
                    (
                        Grammar.Nonterminal('Tp'),
                        {'*', 'ε'}
                    ),
                    (
                        Grammar.Nonterminal('F'),
                        {'(', 'id'}
                    ),
                ]
            ),
        ]

        for grammar, test_cases in grammars:
                if isinstance(grammar, Grammar.Grammar):
                    g = grammar
                else:
                    g = Grammar.Grammar.from_string(grammar)
                for find_start, expected_string in test_cases:
                    with self.subTest(start_of=find_start, expected=expected_string):
                        actual = g.first(find_start)
                        expected = set([Grammar.Terminal(str_version) for str_version in expected_string])
                        assert actual == expected


