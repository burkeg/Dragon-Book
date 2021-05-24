import Automata
import RegExpr


class Simulator:
    def __init__(self, automata):
        assert isinstance(automata, Automata.Automata)
        self.automata = automata


class EOF:
    pass


class AutomataUtils:
    @staticmethod
    def epsilon_touching(s):
        states = set()
        for transition in s.outgoing_flat():
            assert isinstance(transition, Automata.Transition)
            if isinstance(transition.element, Automata.EmptyExpression):
                states.add(transition.target)
        return states

    @staticmethod
    def epsilon_closure(T):
        if isinstance(T, Automata.NFAState):
            T = {T}

        # Set of NFA states reachable from NFA state s on epsilon-transitions alone.
        assert isinstance(T, set)
        stack = list(T)
        epsilon_closure = T
        while len(stack) > 0:
            t = stack.pop()
            for u in AutomataUtils.epsilon_touching(t):
                if u not in epsilon_closure:
                    epsilon_closure.add(u)
                    stack.append(u)
        return epsilon_closure

    @staticmethod
    def move(T, a):
        if isinstance(T, Automata.State):
            T = {T}
        # Set of NFA states to which there is a transition on input symbol a from some state s
        assert isinstance(T, set) or isinstance(T, frozenset)
        assert isinstance(a, Automata.Element)
        moveable_states = set()
        for state in T:
            assert isinstance(state, Automata.State)
            for transition in state.outgoing_flat():
                if transition.element == a:
                    moveable_states.add(transition.target)
        return moveable_states


class NFASimulator(Simulator):
    def __init__(self, automata):
        assert isinstance(automata, Automata.NFA)
        super().__init__(automata)
        self.expression = None

    def next_element(self):
        for element in self.expression:
            yield element
        yield EOF()


    def simulate(self, expression):
        self.expression = expression
        F = self.automata.ending_states()
        S = AutomataUtils.epsilon_closure(self.automata.start)
        element_gen = self.next_element()
        c = next(element_gen)
        while not isinstance(c, EOF):
            S = AutomataUtils.epsilon_closure(AutomataUtils.move(S, c))
            c = next(element_gen)
        return len(S.intersection(F)) != 0


    def simulate_gen(self, expression):
        self.expression = expression
        F = self.automata.ending_states()
        S = AutomataUtils.epsilon_closure(self.automata.start)
        element_gen = self.next_element()
        c = next(element_gen)
        stop_sim = False
        while not isinstance(c, EOF):
            S = AutomataUtils.epsilon_closure(AutomataUtils.move(S, c))
            yield S.intersection(F)
            if len(S) == 0:
                # We hit a state with a transition that is unmatchable.
                break
            c = next(element_gen)
        yield EOF()


class DFASimulator(Simulator):
    def __init__(self, automata):
        assert isinstance(automata, Automata.DFA)
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
            S = AutomataUtils.epsilon_closure(AutomataUtils.move({s}, c))
            if len(S) == 0:
                # We hit a state with a transition that is unmatchable.
                return False
            s = S.pop()
            c = next(element_gen)
        return s in F


def do_stuff():
    expr = RegExpr.RegExpr.from_string('a{1}')
    nfa = expr.to_NFA()
    nfa.relabel()
    print(nfa)
    nfaSim = NFASimulator(nfa)
    print(nfaSim.simulate(Automata.Element.element_list_from_string('a')))


if __name__ == '__main__':
    do_stuff()
