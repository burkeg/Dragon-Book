import copy

import Transition


class BaseState:
    def __init__(self, name=None, accepting=False, outgoing=None, ID=None):
        self.name = "" if name is None else name
        self.accepting = accepting
        self.outgoing = dict() if outgoing is None else outgoing
        self.ID = -1 if ID is None else ID

    def add_outgoing(self, transition):
        assert isinstance(transition, Transition.Transition)
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


class NFAState(BaseState):
    # Nondeterministic Finite LexicalAnalysis
    # outgoing is a dictionary of key value pairs where the keys are of type Element
    # and the values are lists Transitions
    def __init__(self, name=None, accepting=False, outgoing=None, ID=None):
        super().__init__(name, accepting, outgoing, ID)
        assert isinstance(self.outgoing, dict)
        for element, transition_list in self.outgoing.items():
            for transition in transition_list:
                assert isinstance(transition, Transition.Transition)
                assert element == transition.element

    def _add_outgoing(self, transition):
        self.outgoing.setdefault(transition.element, []).append(transition)

    def _outgoing_flat(self):
        return [transition for transition_list in self.outgoing.values() for transition in transition_list]


class ProductionState(NFAState):
    def __init__(self, action, d_i):
        assert callable(action)
        # assert isinstance(d_i, RegExpr)
        self.action = action
        self.d_i = d_i
        super().__init__(accepting=True)


class DFAState(BaseState):
    # Deterministic Finite LexicalAnalysis
    # outgoing is a dictionary of key value pairs where the keys are of type Element
    # and the values of type Transition
    def __init__(self, name=None, accepting=False, outgoing=None, ID=None):
        super().__init__(name, accepting, outgoing, ID)
        assert isinstance(self.outgoing, dict)
        for element, transition in self.outgoing.items():
            assert isinstance(transition, Transition.Transition)
            assert element == transition.element

    def _add_outgoing(self, transition):
        if transition.element in self.outgoing:
            raise Exception('Transition already exists for given Element.')
        self.outgoing[transition.element] = transition

    def _outgoing_flat(self):
        return [transition for transition in self.outgoing.values()]
