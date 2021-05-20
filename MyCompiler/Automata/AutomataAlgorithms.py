from Automata.Automata import Automata, NFA, Transition, EmptyExpression, NFAState, Element, NFAOneStartOneEnd
from Automata.RegExpr import RegExpr, RegExprParseTree, Operation


class Simulator:
    def __init__(self, automata):
        assert isinstance(automata, Automata)
        self.automata = automata

class EOF:
    pass


class NFASimulator(Simulator):
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
        S = self.epsilon_closure(self.automata.start)
        element_gen = self.next_element()
        c = next(element_gen)
        while not isinstance(c, EOF):
            S = self.epsilon_closure(self.move(S, c))
            c = next(element_gen)
        return len(S.intersection(F)) != 0

    @staticmethod
    def epsilon_touching(s):
        states = set()
        for transition in s.outgoing_flat():
            assert isinstance(transition, Transition)
            if transition.element == EmptyExpression:
                states.add(transition.target)
        return states

    @staticmethod
    def epsilon_closure(T):
        if isinstance(T, NFAState):
            T = {T}

        # Set of NFA states reachable from NFA state s on epsilon-transitions alone.
        assert isinstance(T, set)
        stack = list(T)
        epsilon_closure = T
        while len(stack) > 0:
            t = stack.pop()
            for u in NFASimulator.epsilon_touching(t):
                if u not in epsilon_closure:
                    epsilon_closure.add(u)
                    stack.append(u)
        return epsilon_closure

    @staticmethod
    def move(T, a):
        # Set of NFA states to which there is a transition on input symbol a from some state s
        assert isinstance(T, set)
        assert isinstance(a, Element)
        moveable_states = set()
        for state in T:
            assert isinstance(state, NFAState)
            for transition in state.outgoing_flat():
                if transition.element == a:
                    moveable_states.add(transition.target)
        return moveable_states


def RegExpr_to_NFA(regexpr):
    # https://en.wikipedia.org/wiki/Thompson%27s_construction
    assert isinstance(regexpr, RegExpr)

    def recursive_parse_tree_to_NFA(parse_tree):
        assert isinstance(parse_tree, RegExprParseTree)
        if parse_tree.operation == Operation.IDENTITY:
            return NFAOneStartOneEnd.basis(parse_tree.left)

        # r = s|t
        if parse_tree.operation == Operation.UNION:
            N_s = recursive_parse_tree_to_NFA(parse_tree.left)
            N_t = recursive_parse_tree_to_NFA(parse_tree.right)

            end_state = NFAState('f', accepting=True)
            end_transition = Transition(EmptyExpression, end_state)
            N_s.stop.accepting = False
            N_t.stop.accepting = False
            N_s.stop.add_outgoing(end_transition)
            N_t.stop.add_outgoing(end_transition)

            N_s_start_transition = Transition(EmptyExpression, N_s.start)
            N_t_start_transition = Transition(EmptyExpression, N_t.start)
            start_state = NFAState('i')
            start_state.add_outgoing(N_s_start_transition)
            start_state.add_outgoing(N_t_start_transition)
            return NFAOneStartOneEnd(start_state, N_s.alphabet.union(N_t.alphabet), end_state)
        # r = st
        elif parse_tree.operation == Operation.CONCAT:
            N_s = recursive_parse_tree_to_NFA(parse_tree.left)
            N_t = recursive_parse_tree_to_NFA(parse_tree.right)

            N_s.stop.accepting = False

            for transition_list in N_t.start.outgoing.values():
                for transition in transition_list:
                    N_s.stop.add_outgoing(transition)

            return NFAOneStartOneEnd(N_s.start, N_s.alphabet.union(N_t.alphabet), N_t.stop)
        # r = s*
        elif parse_tree.operation == Operation.KLEENE:
            N_s = recursive_parse_tree_to_NFA(parse_tree.left)

            end_state = NFAState('f', accepting=True)
            end_transition = Transition(EmptyExpression, end_state)
            N_s.stop.accepting = False
            N_s.stop.add_outgoing(end_transition)

            N_s_start_transition = Transition(EmptyExpression, N_s.start)
            start_state = NFAState('i')
            start_state.add_outgoing(N_s_start_transition)

            skip_transition = Transition(EmptyExpression, end_state)
            loop_transition = Transition(EmptyExpression, N_s.start)
            start_state.add_outgoing(skip_transition)
            N_s.stop.add_outgoing(loop_transition)
            return NFAOneStartOneEnd(start_state, N_s.alphabet, end_state)
        # r = (s)
        elif parse_tree.operation == Operation.GROUP:
            return recursive_parse_tree_to_NFA(parse_tree.left)

    return recursive_parse_tree_to_NFA(regexpr.parse_tree)

def do_stuff():
    expr = RegExpr.from_string('(a|b)*a')
    nfa = RegExpr_to_NFA(expr)
    nfa.relabel()
    print(nfa)
    nfaSim = NFASimulator(nfa)
    nfaSim.simulate(Element.element_list_from_string('aa'))


if __name__ == '__main__':
    do_stuff()
