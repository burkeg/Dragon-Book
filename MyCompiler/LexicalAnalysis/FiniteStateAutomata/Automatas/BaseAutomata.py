from Alphabet import Alphabet
from States import BaseState


class BaseAutomata:
    def __init__(self, start, alphabet):
        assert isinstance(start, BaseState)
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
            assert isinstance(curr, BaseState)
            if curr.accepting:
                end_states.add(curr)
            for transition in curr.outgoing_flat():
                w = transition.target
                if w not in visited:
                    visited.add(transition.target)
                    queue.append(transition.target)
        return end_states
