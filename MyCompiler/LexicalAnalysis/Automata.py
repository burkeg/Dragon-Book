import copy
import math

import Enums
import AutomataAlgorithms
import RegExpr


class Element:
    # This is some element of a language. It can be any arbitrary object,
    # not necessarily an ASCII character.
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if not isinstance(other, Element):
            return False
        return hash(self) == hash(other)

    def __str__(self):
        return str(self.value)
    __repr__ = __str__

    @staticmethod
    def element_list_from_string(string):
        assert isinstance(string, str)
        elements = []
        for character in string:
            elements.append(Element(character))
        return elements


class EmptyExpression(Element):
    def __init__(self):
        super().__init__(None)


# Should be produced whenever an impossible pattern is encountered.
class UnmatchableElement(Element):
    def __init__(self):
        super().__init__(None)


class EscapedCharElement(Element):
    def __init__(self, special_escaped_character):
        assert isinstance(special_escaped_character, Enums.SpecialEscapedCharacter)
        super().__init__(special_escaped_character)


class CharClassElement(Element):
    def __init__(self, char_class):
        assert isinstance(char_class, Enums.ShorthandCharacterClass)
        super().__init__(char_class)


class QuantifierElement(Element):
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop
        assert isinstance(start, int)
        assert isinstance(stop, int) or stop == math.inf
        value = f'{{{start},{stop}}}'
        if start == 0 and stop == math.inf:
            value = '*'
        elif start == 1 and stop == math.inf:
            value = '+'
        if start == 0 and stop == 1:
            value = '?'
        super().__init__(value)


class Alphabet:
    # This describes all the elements of some alphabet sigma
    def __init__(self, elements):
        if isinstance(elements, list):
            elements = set(elements)
        assert isinstance(elements, set)
        self.elements = elements
        for element in elements:
            assert isinstance(element, Element)

    def __contains__(self, item):
        return item in self.elements

    def __str__(self):
        return str(self.elements)
    __repr__ = __str__

    def union(self, other):
        assert isinstance(other, Alphabet)
        return Alphabet(set(self.elements).union(set(other.elements)))

    def union_update(self, other):
        assert isinstance(other, Alphabet)
        self.elements = set(self.elements).union(set(other.elements))

    def __iter__(self):
        return iter(self.elements)

    def __len__(self):
        return len(self.elements)

    def __eq__(self, other):
        if not isinstance(other, Alphabet):
            return False
        if len(self) !=  len(other):
            return False
        if self is other:
            return True
        for element in self:
            if element not in other:
                return False
        return True


class Transition:
    # This describes some transition between states on an automata
    def __init__(self, element, target):
        assert isinstance(element, Element)
        assert isinstance(target, State)
        self.element = element
        self.target = target

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}
        if self in memo:
            existing = memo.get(self)
            return existing

        duplicate = Transition(
            element=copy.deepcopy(self.element, memo),
            target=copy.deepcopy(self.target, memo)
        )

        memo[self] = duplicate

        return duplicate


class State:
    def __init__(self, name=None, accepting=False, outgoing=None, ID=None):
        self.name = "" if name is None else name
        self.accepting = accepting
        self.outgoing = dict() if outgoing is None else outgoing
        self.ID = -1 if ID is None else ID

    def add_outgoing(self, transition):
        assert isinstance(transition, Transition)
        self._add_outgoing(transition)

    def _add_outgoing(self, transition):
        raise Exception('This should be handled by a more derived class.')

    def outgoing_flat(self):
        return self._outgoing_flat()

    def _outgoing_flat(self):
        raise Exception('This should be handled by a more derived class.')

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}
        if self in memo:
            existing = memo.get(self)
            return existing

        duplicate = type(self)(  # Using type(self) here so I use a more derived constructor if it exists
            name=copy.deepcopy(self.name, memo),
            accepting=self.accepting,
            ID=copy.deepcopy(self.ID, memo)
        )

        memo[self] = duplicate

        for transition in self.outgoing_flat():
            duplicate.add_outgoing(copy.deepcopy(transition, memo))

        return duplicate


class NFAState(State):
    # Nondeterministic Finite LexicalAnalysis
    # outgoing is a dictionary of key value pairs where the keys are of type Element
    # and the values are lists Transitions
    def __init__(self, name=None, accepting=False, outgoing=None, ID=None):
        super().__init__(name, accepting, outgoing, ID)
        assert isinstance(self.outgoing, dict)
        for element, transition_list in self.outgoing.items():
            for transition in transition_list:
                assert isinstance(transition, Transition)
                assert element == transition.element

    def _add_outgoing(self, transition):
        self.outgoing.setdefault(transition.element, []).append(transition)

    def _outgoing_flat(self):
        return [transition for transition_list in self.outgoing.values() for transition in transition_list]


class ProductionState(NFAState):
    def __init__(self, action, d_i):
        assert callable(action)
        assert isinstance(d_i, RegExpr.RegExpr)
        self.action = action
        self.d_i = d_i
        super().__init__(accepting=True)


class DFAState(State):
    # Deterministic Finite LexicalAnalysis
    # outgoing is a dictionary of key value pairs where the keys are of type Element
    # and the values of type Transition
    def __init__(self, name=None, accepting=False, outgoing=None, ID=None):
        super().__init__(name, accepting, outgoing, ID)
        assert isinstance(self.outgoing, dict)
        for element, transition in self.outgoing.items():
            assert isinstance(transition, Transition)
            assert element == transition.element

    def _add_outgoing(self, transition):
        if transition.element in self.outgoing:
            raise Exception('Transition already exists for given Element.')
        self.outgoing[transition.element] = transition

    def _outgoing_flat(self):
        return [transition for transition in self.outgoing.values()]


class Automata:
    def __init__(self, start, alphabet):
        assert isinstance(start, State)
        assert isinstance(alphabet, Alphabet)
        self.start = start
        self.alphabet = alphabet

    def relabel(self):
        visited = {self.start}
        count = 0
        queue = [self.start]
        while len(queue) > 0:
            curr = queue.pop(0)
            curr.ID = count
            count += 1
            for transition in curr.outgoing_flat():
                w = transition.target
                if w not in visited:
                    visited.add(transition.target)
                    queue.append(transition.target)

    def ending_states(self):
        end_states = set()
        visited = {self.start}
        queue = [self.start]
        while len(queue) > 0:
            curr = queue.pop(0)
            assert isinstance(curr, State)
            if curr.accepting:
                end_states.add(curr)
            for transition in curr.outgoing_flat():
                w = transition.target
                if w not in visited:
                    visited.add(transition.target)
                    queue.append(transition.target)
        return end_states


class DFA(Automata):
    pass


class NFA(Automata):
    def to_DFA(self):
        Dtran = dict()
        # intially e-closure(s_0) is the only state in Dstates
        start_dstate = frozenset(AutomataAlgorithms.AutomataUtils.epsilon_closure(self.start))
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
            for a in self.alphabet:
                assert isinstance(a, Element)
                U = frozenset(
                    AutomataAlgorithms.AutomataUtils.epsilon_closure(
                        AutomataAlgorithms.AutomataUtils.move(T, a)))
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
            for element in self.alphabet:
                target_dstate = Dtran[(dstate, element)]
                target_DFA_state = DFA_states[target_dstate]
                DFA_state.add_outgoing(Transition(element, target_DFA_state))

        start_DFA_state = DFA_states[start_dstate]
        return DFA(start_DFA_state, self.alphabet)


class NFAOneStartOneEnd(NFA):
    def __init__(self, start, alphabet, stop):
        assert isinstance(stop, State)
        self.stop = stop
        super().__init__(start, alphabet)

    @staticmethod
    def basis(element=None):
        element = EmptyExpression() if element is None else element
        assert isinstance(element, Element)
        end_state = NFAState('f', accepting=True)
        if not isinstance(element, UnmatchableElement):
            transition_to_end = Transition(element, end_state)
            start_state = NFAState('i', outgoing={element: [transition_to_end]})
        else:
            # In order to create an ummatchable element we'll make this basis disjoint so it's
            # impossible to reach an end state unless we can find a new path through UNION, KLEENE, etc.
            start_state = NFAState('i')
        return NFAOneStartOneEnd(start_state, Alphabet([element]), end_state)

    def __deepcopy__(self, memo=None):
        # I want to copy the structure of the graph but keep references to the same elements in transitions

        # # This should recursively rebuild the whole graph from the start point
        # start = copy.copy(self.start)

        # To get the end point let's search through the graph. It's possible the accepting state
        # is unreachable though so we'll need to handle that too
        if memo is None:
            memo = {}
        if self in memo:
            existing = memo.get(self)
            return existing

        duplicate = NFAOneStartOneEnd(
            copy.deepcopy(self.start, memo),
            copy.deepcopy(self.alphabet, memo),
            copy.deepcopy(self.stop, memo)
        )

        return duplicate


def do_stuff():
    nfa = NFAOneStartOneEnd.basis(Element('abc123'))
    nfa2 = copy.deepcopy(nfa)
    print(nfa.alphabet)


if __name__ == '__main__':
    do_stuff()
