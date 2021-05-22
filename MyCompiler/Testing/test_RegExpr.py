from unittest import TestCase


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
        }
        # for regex, test in TestSimulator.positive_tests.items():
        #     for testcase in test:
        #         with self.subTest(regex=regex, testcase=testcase):
        #             expr = RegExpr.from_string(regex)
        #             nfa = RegExpr_to_NFA(expr)
        #             dfa = NFAtoDFA(nfa)
        #             dfaSim = DFASimulator(dfa)
        #             assert dfaSim.simulate(Element.element_list_from_string(testcase))
