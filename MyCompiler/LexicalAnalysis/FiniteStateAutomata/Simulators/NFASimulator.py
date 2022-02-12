from AutomataOperationUtility import AutomataOperationUtility
from BaseSimulator import BaseSimulator
from Elements import EOF
from NFA import NFA


class NFASimulator(BaseSimulator):
    def __init__(self, automata):
        assert isinstance(automata, NFA)
        super().__init__(automata)
        self.expression = None

    def next_element(self):
        for element in self.expression:
            yield element
        yield EOF()

    def simulate(self, expression):
        self.expression = expression
        F = self.automata.ending_states()
        S = AutomataOperationUtility.epsilon_closure(self.automata.start)
        element_gen = self.next_element()
        c = next(element_gen)
        while not isinstance(c, EOF):
            S = AutomataOperationUtility.epsilon_closure(AutomataOperationUtility.move(S, c))
            c = next(element_gen)
        return len(S.intersection(F)) != 0

    def simulate_gen(self, expression):
        self.expression = expression
        F = self.automata.ending_states()
        S = AutomataOperationUtility.epsilon_closure(self.automata.start)
        element_gen = self.next_element()
        c = next(element_gen)
        stop_sim = False
        while not isinstance(c, EOF):
            S = AutomataOperationUtility.epsilon_closure(AutomataOperationUtility.move(S, c))
            yield S.intersection(F)
            if len(S) == 0:
                # We hit a state with a transition that is unmatchable.
                break
            c = next(element_gen)
        yield EOF()
