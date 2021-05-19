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

class EmptyExpression(Element):
    def __init__(self):
        super().__init__(None)


class Alphabet:
    # This describes all the elements of some alphabet sigma
    def __init__(self, elements):
        self.elements = elements

    def __contains__(self, item):
        return item in self.elements

    def __str__(self):
        return str(self.elements)
    __repr__ = __str__

    def union(self, other):
        assert isinstance(other, Alphabet)
        return Alphabet(list(set(self.elements).union(set(other.elements))))


class Transition:
    # This describes some transition between states on an automata
    def __init__(self, element, target):
        self.element = element
        self.target = target


class State:
    def __init__(self, name=None, accepting=False, outgoing=None):
        self.name = "" if name is None else name
        self.accepting = accepting
        self.outgoing = dict() if outgoing is None else outgoing

    def add_outgoing(self, transition):
        assert isinstance(transition, Transition)
        self._handle_add_outgoing(transition)

    def _handle_add_outgoing(self, transition):
        raise Exception('This should be handled by a more derived class.')


class NFAState(State):
    # Nondeterministic Finite Automata
    # outgoing is a dictionary of key value pairs where the keys are of type Element
    # and the values are lists Transitions
    def __init__(self, name=None, accepting=False, outgoing=None):
        super().__init__(name, accepting, outgoing)
        assert isinstance(self.outgoing, dict)
        for element, transition_list in self.outgoing.items():
            for transition in transition_list:
                assert isinstance(transition, Transition)
                assert element == transition.element

    def _handle_add_outgoing(self, transition):
        self.outgoing.setdefault(transition.element, []).append(transition)


class DFAState(State):
    # Deterministic Finite Automata
    # outgoing is a dictionary of key value pairs where the keys are of type Element
    # and the values of type Transition
    def __init__(self, name=None, accepting=False, outgoing=None):
        super().__init__(name, accepting, outgoing)
        assert isinstance(self.outgoing, dict)
        for element, transition in self.outgoing.items():
            assert isinstance(transition, Transition)
            assert element == transition.element

    def handle_add_outgoing(self, transition):
        if transition.element not in self.outgoing:
            raise Exception('Transition already exists for given Element.')
        self.outgoing[transition.element] = transition


class Automata:
    def __init__(self, start, alphabet):
        assert isinstance(start, State)
        assert isinstance(alphabet, Alphabet)
        self.start = start
        self.alphabet = alphabet


class DFA(Automata):
    pass


class NFA(Automata):
    @staticmethod
    def basis(element=None):
        element = EmptyExpression() if element is None else element
        assert isinstance(element, Element)
        end_state = NFAState('f', accepting=True)
        transition_to_end = Transition(element, end_state)
        start_state = NFAState('i', outgoing={None: [transition_to_end]})
        return NFA(start_state, Alphabet([element]))


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
        transition_to_end = Transition(element, end_state)
        start_state = NFAState('i', outgoing={element: [transition_to_end]})
        return NFAOneStartOneEnd(start_state, Alphabet([element]), end_state)



def do_stuff():
    sigma1 = Alphabet([Element('a'), Element('b')])
    sigma2 = Alphabet([Element('apples'), Element('oranges')])
    print(sigma2)
    nfa1 = NFA.basis()
    nfa2 = NFA.basis(Element('abc123'))
    print(nfa1.alphabet)
    print(nfa2.alphabet)


if __name__ == '__main__':
    do_stuff()
