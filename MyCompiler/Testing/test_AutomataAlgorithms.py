from unittest import TestCase

from AutomataAlgorithms import *
from RegExpr import *

class TestSimulator(TestCase):
    def test_simulate(self):
        positive_tests = {
            r'.': ['a'],
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
            r'\t': ['\t'],
            r'\n': ['\n'],
            r'\s': ['\n', '\t', ' '],
            r'[\t]': ['\t'],
            r'[\t\d]': ['\t', '0', '2', '9'],
            r'[\d+]': ['+', '0', '2', '9'],
            r'[\d]+': ['0', '2', '9', '11', '123456789'],
            r'[\s]+': [' ', '      \t    \n'],
            r'[\d]': ['0', '1', '9'],

        }
        negative_tests = {
            r'(a|b)*a': ['', 'aaaaaab', 'baaaab', 'abaab'],
            r'(a|b)*abb': ['bb', 'aaabaaa', 'baaaab', 'ababa'],
            r'a*b*a*b*': ['baba', 'bbbabbbaaa', 'ababa'],
            r'a+': [''],
            r'a?': ['aa'],
            r'[ab]': [''],
        }

        with self.subTest(simulator='NFA'):
            for regex, test in positive_tests.items():
                for testcase in test:
                    with self.subTest(regex=regex, testcase=testcase):
                        expr = RegExpr.from_string(regex)
                        nfa = RegExpr_to_NFA(expr)
                        nfaSim = NFASimulator(nfa)
                        assert nfaSim.simulate(Element.element_list_from_string(testcase))

            for regex, test in negative_tests.items():
                for testcase in test:
                    with self.subTest(regex=regex, testcase=testcase):
                        expr = RegExpr.from_string(regex)
                        nfa = RegExpr_to_NFA(expr)
                        nfaSim = NFASimulator(nfa)
                        assert not nfaSim.simulate(Element.element_list_from_string(testcase))

        with self.subTest(simulator='DFA'):
            for regex, test in positive_tests.items():
                for testcase in test:
                    with self.subTest(regex=regex, testcase=testcase):
                        expr = RegExpr.from_string(regex)
                        nfa = RegExpr_to_NFA(expr)
                        dfa = NFAtoDFA(nfa)
                        dfaSim = DFASimulator(dfa)
                        assert dfaSim.simulate(Element.element_list_from_string(testcase))

            for regex, test in negative_tests.items():
                for testcase in test:
                    with self.subTest(regex=regex, testcase=testcase):
                        expr = RegExpr.from_string(regex)
                        nfa = RegExpr_to_NFA(expr)
                        dfa = NFAtoDFA(nfa)
                        dfaSim = DFASimulator(dfa)
                        assert not dfaSim.simulate(Element.element_list_from_string(testcase))
