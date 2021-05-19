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


class Alphabet:
    # This describes all the elements of some alphabet sigma
    def __init__(self, elements):
        self.elements = elements


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


class Automata:
    def __init__(self, start, alphabet):
        assert isinstance(start, State)
        assert isinstance(alphabet, Alphabet)
        self.start = start
        self.alphabet = alphabet
