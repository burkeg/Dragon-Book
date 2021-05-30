from unittest import TestCase

import AutomataAlgorithms
import RegExpr
import Automata

class TestSimulator(TestCase):
    def test_simulate(self):
        positive_tests = {
            r'(a|b)*a': ['aa', 'aaaaaa', 'baaaa', 'abaa'],
            r'(a|b)*abb': ['abb', 'aaaaaabb', 'baaaabb', 'abaabb'],
            r'a*': ['', 'a', 'aa', 'aaaaaaaaa'],
            r'a+': ['a', 'aa', 'aaaaaaaaa'],
            r'a?': ['', 'a'],
            r'a*b*a*b*': ['', 'a', 'aa', 'ab', 'ba', 'bbbbbaaaaaaabbbb', 'aaaabbaaaaab'],
            r'[a]': ['a'],
            r'[ab]': ['a', 'b'],
            r'[a-d]': ['a', 'b', 'c', 'd'],
            r'[A-D]': ['A', 'B', 'C', 'D'],
            r'[0-1]': ['0', '1'],
            r'[0-9]': ['0', '1', '9'],
            r'[a-bA-B]': ['a', 'b', 'A', 'B'],
            r'[-ab]': ['-', 'a', 'b'],
            r'[-a-bA-B]': ['a', 'b', 'A', 'B', '-'],
            r'[\[]': ['['],
            r'\d': ['0', '1', '9'],
            r'\w': ['0', '1', '9', '_', 'a'],
            r'\t': ['\t'],
            r'\n': ['\n'],
            r'\s': ['\n', '\t', ' '],
            r'[\t]': ['\t'],
            r'[\t\d]': ['\t', '0', '2', '9'],
            r'[\d+]': ['+', '0', '2', '9'],
            r'[\d]+': ['0', '2', '9', '11', '123456789'],
            r'[\s]+': [' ', '      \t    \n'],
            r'[\d]': ['0', '1', '9'],
            r'[\D]': ['a', 'b', ' '],
            r'[\D\d]': ['a', 'b', ' ', '1'],
            r'[\S]': ['a', 'b', '1'],
            r'[^a-c^]': ['1', ' ', '\n', 'Z'],
            r'.': ['a'],
            r'a{0,}': ['', 'a', 'aa'],
            r'a{1,}': ['a', 'aa'],
            r'a{0,1}': ['', 'a'],
            r'a{0,2}': ['', 'a', 'aa'],
            r'a{0,8}': ['', 'a', 'aaaaaaa', 'aaaaaaaa'],
            r'a{1,8}': ['a', 'aaaaaaa', 'aaaaaaaa'],
            r'a{5,8}': ['aaaaa', 'aaaaaaaa'],
            r'a{5,}': ['aaaaa', 'aaaaaaa', 'aaaaaaaa'],
            r'(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}':
                [
                    '123-456-7890',
					'(123) 456-7890',
					'123 456 7890',
					'123.456.7890',
					'+91 (123) 456-7890',
                ],
            r'\d{3}': ['111'],
            r'(\w)+': ['a123'],
            r'(\w+\s*)+': ['a123 1 _abc'],
            r'\d+(\.\d+)?(E[+-]?\d+)?': ['123', '1E-9', '1E9', '1.2E-9'],
            r'(=|\+=|-=|\*=|/=)': ['=', '+=', '-=', '*=', '/=', ],
            r'a|bb': ['a'],
        }

        negative_tests = {
            # r'(a|b)*a': ['', 'aaaaaab', 'baaaab', 'abaab'],
            # r'(a|b)*abb': ['bb', 'aaabaaa', 'baaaab', 'ababa'],
            # r'a*b*a*b*': ['baba', 'bbbabbbaaa', 'ababa'],
            # r'a+': [''],
            # r'a?': ['aa'],
            # r'[ab]': [''],
            # r'[^\S\s]': [''],
            # r'[]': ['literally anything'],
            # r'[^a-c^]': ['a', 'b', 'c', '^'],
            # r'a{1,}': [''],
            # r'a{0,1}': ['aa', 'aaa'],
            # r'a{0,2}': ['aaa', 'aaaa'],
            # r'a{0,8}': ['aaaaaaaaa', 'aaaaaaaaaa', 'aaaaaaaaaaa', ],
            # r'a{1,8}': ['', 'aaaaaaaaa', 'aaaaaaaaaa', 'aaaaaaaaaaa', ],
            # r'a{5,8}': ['', 'a', 'aa', 'aaa', 'aaaa', 'aaaaaaaaa','aaaaaaaaaa',],
            # r'a{5,}': ['', 'a', 'aa', 'aaa', 'aaaa'],
        }

        with self.subTest(simulator='NFA'):
            with self.subTest(type='Positive'):
                for regex, test in positive_tests.items():
                    expr = RegExpr.RegExpr.from_string(regex)
                    nfa = expr.to_NFA()
                    nfaSim = AutomataAlgorithms.NFASimulator(nfa)
                    for testcase in test:
                        with self.subTest(regex=regex, testcase=testcase):
                            assert nfaSim.simulate(Automata.Element.element_list_from_string(testcase))

            with self.subTest(type='Negative'):
                for regex, test in negative_tests.items():
                    expr = RegExpr.RegExpr.from_string(regex)
                    nfa = expr.to_NFA()
                    nfaSim = AutomataAlgorithms.NFASimulator(nfa)
                    for testcase in test:
                        with self.subTest(regex=regex, testcase=testcase):
                            assert not nfaSim.simulate(Automata.Element.element_list_from_string(testcase))

        with self.subTest(simulator='DFA'):
            with self.subTest(type='Positive'):
                for regex, test in positive_tests.items():
                    expr = RegExpr.RegExpr.from_string(regex)
                    nfa = expr.to_NFA()
                    dfa = nfa.to_DFA()
                    dfaSim = AutomataAlgorithms.DFASimulator(dfa)
                    for testcase in test:
                        with self.subTest(regex=regex, testcase=testcase):
                            assert dfaSim.simulate(Automata.Element.element_list_from_string(testcase))

            with self.subTest(type='Negative'):
                for regex, test in negative_tests.items():
                    expr = RegExpr.RegExpr.from_string(regex)
                    nfa = expr.to_NFA()
                    dfa = nfa.to_DFA()
                    dfaSim = AutomataAlgorithms.DFASimulator(dfa)
                    for testcase in test:
                        with self.subTest(regex=regex, testcase=testcase):
                            assert not dfaSim.simulate(Automata.Element.element_list_from_string(testcase))
