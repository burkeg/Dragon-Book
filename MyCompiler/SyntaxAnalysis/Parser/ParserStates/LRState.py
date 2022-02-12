from LR0Item import LR0Item
from LRItemGroup import LRItemGroup
from States import DFAState


class LRState(DFAState):
    def __init__(self, lr_set, ID=-1):
        assert isinstance(lr_set, LRItemGroup)
        super().__init__(name=repr(lr_set), ID=ID)
        self._lr_set = lr_set

    def I(self):
        return self._lr_set

    def get_core_hash(self):
        # By looking at each LR1 item as an LR0 item we can hash on each item to find shared cores
        return hash(tuple(sorted({hash(LR0Item._key(item)) for item in self})))

    # https://stackoverflow.com/questions/2909106/whats-a-correct-and-good-way-to-implement-hash
    def _key(self):
        return self._lr_set

    def __hash__(self):
        return hash(self._key())

    def __eq__(self, other):
        if isinstance(other, LRState):
            return self._key() == other._key()
        return NotImplemented

    def __repr__(self):
        return f'LRState({repr(self._lr_set)}, ID={self.ID})'

    def __contains__(self, key):
        return key in self._lr_set.get_items()

    def __iter__(self):
        return iter(self._lr_set.get_items())

    def __lt__(self, other):
        if isinstance(other, LRState):
            return self._lr_set < other._lr_set
        return NotImplemented

    # def union(self, other):
    #     assert isinstance(other, LRState)
    #     return MultiLRState(self).union(other)
