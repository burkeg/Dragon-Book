from Elements import EmptyExpression
from States import NFAState
from Transition import Transition
from States import BaseState
from Elements import BaseElement


class AutomataOperationUtility:
    @staticmethod
    def epsilon_touching(s):
        states = set()
        for transition in s.outgoing_flat():
            assert isinstance(transition, Transition)
            if isinstance(transition.element, EmptyExpression):
                states.add(transition.target)
        return states

    @classmethod
    def epsilon_closure(cls, T):
        if isinstance(T, NFAState):
            T = {T}

        # Set of NFA states reachable from NFA state s on epsilon-transitions alone.
        assert isinstance(T, set)
        stack = list(T)
        epsilon_closure = T
        while len(stack) > 0:
            t = stack.pop()
            for u in cls.epsilon_touching(t):
                if u not in epsilon_closure:
                    epsilon_closure.add(u)
                    stack.append(u)
        return epsilon_closure

    @staticmethod
    def move(T, a):
        if isinstance(T, BaseState):
            T = {T}
        # Set of NFA states to which there is a transition on input symbol a from some state s
        assert isinstance(T, set) or isinstance(T, frozenset)
        assert isinstance(a, BaseElement)
        movable_states = set()
        for state in T:
            assert isinstance(state, BaseState)
            for transition in state.outgoing_flat():
                if transition.element == a:
                    movable_states.add(transition.target)
        return movable_states
