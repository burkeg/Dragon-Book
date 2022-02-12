import copy

from Alphabet import Alphabet
from Elements import EmptyExpression, BaseElement, UnmatchableElement
from NFA import NFA
from States import BaseState, NFAState
from Transition import Transition


class NFAOneStartOneEnd(NFA):
    def __init__(self, start, alphabet, stop):
        assert isinstance(stop, BaseState)
        self.stop = stop
        super().__init__(start, alphabet)

    @staticmethod
    def basis(element=None):
        element = EmptyExpression() if element is None else element
        assert isinstance(element, BaseElement)
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
