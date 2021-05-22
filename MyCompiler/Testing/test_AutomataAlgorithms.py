from unittest import TestCase

from AutomataAlgorithms import *
from RegExpr import *

class TestSimulator(TestCase):
    def test_simulate(self):
        positive_tests = {
            '(a|b)*a': ['aa', 'aaaaaa', 'baaaa', 'abaa'],
            '(a|b)*abb': ['abb', 'aaaaaabb', 'baaaabb', 'abaabb'],
            'a*': ['', 'a', 'aa', 'aaaaaaaaa'],
            'a*b*a*b*': ['', 'a', 'aa', 'ab', 'ba', 'bbbbbaaaaaaabbbb', 'aaaabbaaaaab']
        }
        negative_tests = {
            '(a|b)*a': ['', 'aaaaaab', 'baaaab', 'abaab'],
            '(a|b)*abb': ['bb', 'aaabaaa', 'baaaab', 'ababa'],
            'a*b*a*b*': ['baba', 'bbbabbbaaa', 'ababa']
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
