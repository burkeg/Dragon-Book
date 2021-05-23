from Automata import Automata, NFA, Transition, EmptyExpression, NFAState, Element, NFAOneStartOneEnd, DFA, DFAState, \
    State
from RegExpr import RegExpr, RegExprParseTree, Operation


class Simulator:
    def __init__(self, automata):
        assert isinstance(automata, Automata)
        self.automata = automata

class EOF:
    pass

class AutomataUtils:
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
            for u in AutomataUtils.epsilon_touching(t):
                if u not in epsilon_closure:
                    epsilon_closure.add(u)
                    stack.append(u)
        return epsilon_closure

    @staticmethod
    def move(T, a):
        if isinstance(T, State):
            T = {T}
        # Set of NFA states to which there is a transition on input symbol a from some state s
        assert isinstance(T, set) or isinstance(T, frozenset)
        assert isinstance(a, Element)
        moveable_states = set()
        for state in T:
            assert isinstance(state, State)
            for transition in state.outgoing_flat():
                if transition.element == a:
                    moveable_states.add(transition.target)
        return moveable_states

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
        S = AutomataUtils.epsilon_closure(self.automata.start)
        element_gen = self.next_element()
        c = next(element_gen)
        while not isinstance(c, EOF):
            S = AutomataUtils.epsilon_closure(AutomataUtils.move(S, c))
            c = next(element_gen)
        return len(S.intersection(F)) != 0

class DFASimulator(Simulator):
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
            S = AutomataUtils.epsilon_closure(AutomataUtils.move({s}, c))
            if len(S) == 0:
                # We hit a state with a transition that is unmatchable.
                return False
            s = S.pop()
            c = next(element_gen)
        return s in F


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
        # r = s+
        elif parse_tree.operation == Operation.PLUS:
            N_s = recursive_parse_tree_to_NFA(parse_tree.left)

            end_state = NFAState('f', accepting=True)
            end_transition = Transition(EmptyExpression, end_state)
            N_s.stop.accepting = False
            N_s.stop.add_outgoing(end_transition)

            N_s_start_transition = Transition(EmptyExpression, N_s.start)
            start_state = NFAState('i')
            start_state.add_outgoing(N_s_start_transition)

            # skip_transition = Transition(EmptyExpression, end_state)
            loop_transition = Transition(EmptyExpression, N_s.start)
            # start_state.add_outgoing(skip_transition)
            N_s.stop.add_outgoing(loop_transition)
            return NFAOneStartOneEnd(start_state, N_s.alphabet, end_state)
        # r = s?
        elif parse_tree.operation == Operation.QUESTION:
            N_s = recursive_parse_tree_to_NFA(parse_tree.left)

            end_state = NFAState('f', accepting=True)
            end_transition = Transition(EmptyExpression, end_state)
            N_s.stop.accepting = False
            N_s.stop.add_outgoing(end_transition)

            N_s_start_transition = Transition(EmptyExpression, N_s.start)
            start_state = NFAState('i')
            start_state.add_outgoing(N_s_start_transition)

            skip_transition = Transition(EmptyExpression, end_state)
            # loop_transition = Transition(EmptyExpression, N_s.start)
            start_state.add_outgoing(skip_transition)
            # N_s.stop.add_outgoing(loop_transition)
            return NFAOneStartOneEnd(start_state, N_s.alphabet, end_state)
        # r = (s)
        elif parse_tree.operation == Operation.GROUP:
            return recursive_parse_tree_to_NFA(parse_tree.left)
        else:
            raise Exception('Hey dummy you forgot to implement the graph operation for an operator')

    return recursive_parse_tree_to_NFA(regexpr.parse_tree)

def NFAtoDFA(nfa):
    assert isinstance(nfa, NFA)
    Dtran = dict()
    # intially e-closure(s_0) is the only state in Dstates
    start_dstate = frozenset(AutomataUtils.epsilon_closure(nfa.start))
    Dstates = {start_dstate}
    marked_states = set()
    while True:
        # while there is an unmarked state T in Dstates
        unmarked_states = Dstates.difference(marked_states)
        if len(unmarked_states) == 0:
            break
        T = unmarked_states.pop()
        # mark T
        marked_states.add(T)
        # for each input symbol a
        for a in nfa.alphabet:
            assert isinstance(a, Element)
            U = frozenset(AutomataUtils.epsilon_closure(AutomataUtils.move(T, a)))
            if U not in Dstates:
                Dstates.add(U)
            Dtran[(T, a)] = U

    count = 0
    DFA_states = dict()
    for dstate in Dstates:
        ID = count
        count += 1
        accepting = any([state.accepting for state in dstate])
        outgoing = None # We need to build all states before doing this
        DFA_states[dstate] = DFAState(accepting=accepting, outgoing=outgoing, ID=ID)

    # 2nd pass to add transitions based on Dtran
    for dstate in Dstates:
        DFA_state = DFA_states[dstate]
        for element in nfa.alphabet:
            target_dstate = Dtran[(dstate, element)]
            target_DFA_state = DFA_states[target_dstate]
            DFA_state.add_outgoing(Transition(element, target_DFA_state))

    start_DFA_state = DFA_states[start_dstate]
    return DFA(start_DFA_state, nfa.alphabet)

def do_stuff():
    expr = RegExpr.from_string('(a|b)*abb')
    nfa = RegExpr_to_NFA(expr)
    nfa.relabel()
    print(nfa)
    nfaSim = NFASimulator(nfa)
    print(nfaSim.simulate(Element.element_list_from_string('aa')))
    dfa = NFAtoDFA(nfa)
    dfa.relabel()
    print(dfa)
    dfaSim = DFASimulator(dfa)
    print(dfaSim.simulate(Element.element_list_from_string('aa')))


if __name__ == '__main__':
    do_stuff()
