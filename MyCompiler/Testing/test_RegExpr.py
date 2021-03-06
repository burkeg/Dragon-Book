from unittest import TestCase

# from RegExpr import RegularDefinition, RegExprParseTree
from RegExpr import *

class TestRegularDefinition(TestCase):
    def test_from_string(self):
        regular_definitions = {
            'simplest non-empty':
                r'A a',
            '2 definitions no nesting':
                r'A a' + '\n' +
                r'B b',
            '2 definitions nesting':
                r'A a' + '\n' +
                r'B {A}b',
            'kleene':
                r'A a' + '\n' +
                r'B {A}*b',
            'numbers and identifiers':
                r'delim [ \t\n]' + '\n' +
                r'ws {delim}+' + '\n' +
                r'letter a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z' + '\n' +
                r'letter_ {letter}|_' + '\n' +
                r'digit 0|1|2|3|4|5|6|7|8|9' + '\n' +
                r'id {letter_}({letter_}|{digit})*' + '\n' +
                r'number {digit}+(\.{digit}+)?(E[+-]?{digit}+)?',
        }
        for name, regular_definition in regular_definitions.items():
            with self.subTest(name=name, regular_definition=regular_definition):
                reg_def = RegularDefinition.from_string(regular_definition)
                assert isinstance(reg_def, RegularDefinition)


class TestRegExprParseTree(TestCase):
    def test_range_over_chars(self):
        positive_cases = [
            ('a', 'b'),
            ('a', 'a'),
            ('a', 'z'),
            ('b', 'y'),
            ('A', 'B'),
            ('A', 'A'),
            ('A', 'Z'),
            ('B', 'Y'),
            ('0', '1'),
            ('0', '0'),
            ('0', '9'),
            ('1', '8'),
        ]
        negative_cases = [
            ('b', 'a'),
            ('a', 'A'),
            ('a', 'Z'),
            ('1', 'a'),
            ('1', 'a'),
            ('', 'a'),
            ('[', '-'),
            ('[', ']'),
            ('multicharacter string', 'b'),
            (None, None),
        ]
        for start, stop in positive_cases:
            with self.subTest(start=start, stop=stop):
                char_set = RegExprParseTree.range_over_chars(start, stop)
                assert isinstance(char_set, set)
                for ascii_num in range(ord(start), ord(stop) + 1):
                    assert chr(ascii_num) in char_set

        for start, stop in negative_cases:
            with self.subTest(start=start, stop=stop):
                should_fail = lambda: RegExprParseTree.range_over_chars(start, stop)
                self.assertRaises(Exception, should_fail)
