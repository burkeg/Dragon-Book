from AutomataOperationUtility import AutomataOperationUtility
from BaseSimulator import BaseSimulator
from DFA import DFA
from Elements import EOF


class DFASimulator(BaseSimulator):
    def __init__(self, automata):
        assert isinstance(automata, DFA)
        super().__init__(automata)
        self.expression = None

    def next_element(self):
        for element in self.expression:
            yield element
        yield EOF()


    def simulate(self, expression):
        self.expression = expression
        F = self.automata.ending_states()
        s = self.automata.start
        element_gen = self.next_element()
        c = next(element_gen)
        while not isinstance(c, EOF):
            S = AutomataOperationUtility.epsilon_closure(AutomataOperationUtility.move({s}, c))
            if len(S) == 0:
                # We hit a state with a transition that is unmatchable.
                return False
            s = S.pop()
            c = next(element_gen)
        return s in F