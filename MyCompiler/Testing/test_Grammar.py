from unittest import TestCase

from BaseGrammar import BaseGrammar
from GrammarFileLoader import GrammarFileLoader
from Nonterminal import Nonterminal
from Terminal import Terminal


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
                g = BaseGrammar.from_string(grammar, action_dict)
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
                g = BaseGrammar.from_string(grammar)
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
                g = BaseGrammar.from_string(grammar)
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
                GrammarFileLoader.load('4.29'),
                [
                    (
                        Nonterminal('S'),
                        {'c'}
                    ),
                    (
                        Nonterminal('A'),
                        {'a'}
                    ),
                ]
            ),
            (
                # """
                # S -> A 'a' | 'b'
                # A -> A 'c' | S 'd' | 'ε'
                # """
                GrammarFileLoader.load('4.18'),
                [
                    (
                        Nonterminal('S'),
                        {'a', 'b', 'c'}
                    ),
                    (
                        Nonterminal('A'),
                        {'a', 'b', 'c', 'ε'}
                    ),
                ]
            ),
            (
                # """
                # S -> A 'a' | 'b'
                # A -> A 'c' | S 'd' | 'ε'
                # """
                # Actually 4.18. After removing left recursion the meanings of symbols can
                # change and new symbols can be introduced. Modifying the behavior of
                # simplify() or without_left_recursion() can break these tests despite still
                # having correct outputs.
                GrammarFileLoader.load('4.20'),
                [
                    (
                        Nonterminal('S'),
                        {'a', 'b', 'c'}
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
                GrammarFileLoader.load('4.28'),
                [
                    (
                        Nonterminal('E'),
                        {'(', 'id'}
                    ),
                    (
                        Nonterminal('Ep'),
                        {'+', 'ε'}
                    ),
                    (
                        Nonterminal('T'),
                        {'(', 'id'}
                    ),
                    (
                        Nonterminal('Tp'),
                        {'*', 'ε'}
                    ),
                    (
                        Nonterminal('F'),
                        {'(', 'id'}
                    ),
                ]
            ),
        ]

        for grammar, test_cases in grammars:
            if isinstance(grammar, BaseGrammar):
                g = grammar
            else:
                g = BaseGrammar.from_string(grammar)
            for find_start, expected_string in test_cases:
                with self.subTest(start_of=find_start, expected=expected_string):
                    actual = g.first(find_start)
                    expected = set([Terminal(str_version) for str_version in expected_string])
                    assert actual == expected

    def test_follow(self):
        grammars = [
            (
                # """
                # S -> 'c' A 'd'
                # A -> 'a' 'b' | 'a'
                # """
                GrammarFileLoader.load('4.29'),
                [
                    (
                        Nonterminal('S'),
                        {'$'}
                    ),
                    (
                        Nonterminal('A'),
                        {'d'}
                    ),
                ]
            ),
            (
                # """
                # S -> A 'a' | 'b'
                # A -> A 'c' | S 'd' | 'ε'
                # """
                GrammarFileLoader.load('4.18'),
                [
                    (
                        Nonterminal('S'),
                        {'$', 'd'}
                    ),
                    (
                        Nonterminal('A'),
                        {'a', 'c'}
                    ),
                ]
            ),
            (
                # """
                # S -> A 'a' | 'b'
                # A -> A 'c' | S 'd' | 'ε'
                # """
                # Actually 4.18. After removing left recursion the meanings of symbols can
                # change and new symbols can be introduced. Modifying the behavior of
                # simplify() or without_left_recursion() can break these tests despite still
                # having correct outputs.
                GrammarFileLoader.load('4.20'),
                [
                    (
                        Nonterminal('S'),
                        {'$'}
                    ),
                    (
                        Nonterminal('A_1'),
                        {'a'}
                    ),
                    (
                        Nonterminal('S_2'),
                        {'$'}
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
                GrammarFileLoader.load('4.28'),
                [
                    (
                        Nonterminal('E'),
                        {'$', ')'}
                    ),
                    (
                        Nonterminal('Ep'),
                        {'$', ')'}
                    ),
                    (
                        Nonterminal('T'),
                        {'+', '$', ')'}
                    ),
                    (
                        Nonterminal('Tp'),
                        {'+', '$', ')'}
                    ),
                    (
                        Nonterminal('F'),
                        {'*', '+', '$', ')'}
                    ),
                ]
            ),
        ]

        for grammar, test_cases in grammars:
            if isinstance(grammar, BaseGrammar):
                g = grammar
            else:
                g = BaseGrammar.from_string(grammar)
            for find_follow, expected_string in test_cases:
                with self.subTest(follow_of=find_follow, expected=expected_string):
                    actual = g.follow(find_follow)
                    expected = set([Terminal(str_version) for str_version in expected_string])
                    if not(actual == expected):
                        assert False


