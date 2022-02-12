import copy

from Elements import BaseElement
import States


class Transition:
    # This describes some transition between states on an automata
    def __init__(self, element, target):
        assert isinstance(element, BaseElement)
        assert isinstance(target, States.BaseState)
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
