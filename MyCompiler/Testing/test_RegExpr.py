from unittest import TestCase

from RegExpr import RegularDefinition


class TestRegularDefinition(TestCase):
    def test_from_string(self):
        regular_definitions = {
            # 'numbers and identifiers':
            #     'delim \ ' + '\n' +
            #     'ws {delim}+' + '\n' +
            #     'letter a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z' + '\n' +
            #     'digit 0|1|2|3|4|5|6|7|8|9' + '\n' +
            #     'id {letter}({letter}|{digit})*' + '\n' +
            #     'number {digit}+(\.{digit}+)?(E[+-]?{digit}+)?',
            'simplest non-empty':
                'A a',
            '2 definitions no nesting':
                'A a' + '\n' +
                'B b',
            '2 definitions nesting':
                'A a' + '\n' +
                'B {A}b',
            'kleene':
                'A a' + '\n' +
                'B {A}*b',
        }
        for name, regular_definition in regular_definitions.items():
            with self.subTest(name=name, regular_definition=regular_definition):
                reg_def = RegularDefinition.from_string(regular_definition)
