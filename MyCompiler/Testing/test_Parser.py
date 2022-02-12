from unittest import TestCase

from CanonicalLR1Parser import CanonicalLR1Parser
from GrammarFileLoader import GrammarFileLoader
from LexicalAnalyzer import LexicalAnalyzer
from SLR1Parser import SLR1Parser
from SpaceConsumingLALRParser import SpaceConsumingLALRParser


class Test(TestCase):
    def test_ANSI_C_to_parse_tree(self):
        return # Last time I ran this it took 6 hours...
        grammar_file_name = 'ANSI C'
        grammar = GrammarFileLoader.load(grammar_file_name)
        parser = CanonicalLR1Parser(grammar)
        lexer = LexicalAnalyzer.ANSI_C_lexer()
        test_cases = [
            """
            int main()
            {
                return 0
            }
            """,
        ]
        create_parse_tree(self, grammar_file_name, grammar, parser, lexer, test_cases)

    def test_4_40_2_SLR1_to_parse_tree(self):
        grammar_file_name = '4.40_2'
        grammar = GrammarFileLoader.load(grammar_file_name)
        parser = SLR1Parser(grammar)
        lexer = LexicalAnalyzer.ANSI_C_lexer()
        test_cases = [
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
        create_parse_tree(self, grammar_file_name, grammar, parser, lexer, test_cases)

    def test_4_40_SLR1_to_parse_tree(self):
        grammar_file_name = '4.40'
        grammar = GrammarFileLoader.load(grammar_file_name)
        parser = SLR1Parser(grammar)
        lexer = LexicalAnalyzer.ANSI_C_lexer()
        test_cases = [
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
        create_parse_tree(self, grammar_file_name, grammar, parser, lexer, test_cases)

    def test_4_55_CanonicalLR1_to_parse_tree(self):
        grammar_file_name = '4.55'
        grammar = GrammarFileLoader.load(grammar_file_name)
        parser = CanonicalLR1Parser(grammar)
        lexer = LexicalAnalyzer.ANSI_C_lexer()
        test_cases = [
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
        create_parse_tree(self, grammar_file_name, grammar, parser, lexer, test_cases)

    def test_4_55_SpaceConsumingLALR_to_parse_tree(self):
        grammar_file_name = '4.55'
        grammar = GrammarFileLoader.load(grammar_file_name)
        parser = SpaceConsumingLALRParser(grammar)
        lexer = LexicalAnalyzer.ANSI_C_lexer()
        test_cases = [
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
        create_parse_tree(self, grammar_file_name, grammar, parser, lexer, test_cases)


def create_parse_tree(test, grammar_file_name, grammar, parser, lexer, test_cases):
    for test_case in test_cases:
        with test.subTest(
                grammar=grammar_file_name,
                parser=parser.__class__.__name__,
                lexer=lexer.__class__.__name__,
                test_case=test_case.strip()):
            tokens = lexer.process(test_case)
            list_tokens = list(tokens)
            productions = parser.produce_derivation(iter(list_tokens))
            tree = parser.to_parse_tree(productions)
            print(tree)

