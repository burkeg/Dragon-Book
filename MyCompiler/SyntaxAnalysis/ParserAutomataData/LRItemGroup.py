from LR0Item import LR0Item


class LRItemGroup:
    def __init__(self, lr_items):
        assert isinstance(lr_items, set)
        for item in lr_items:
            assert isinstance(item, LR0Item)
        self.items = sorted(lr_items)

    def add(self, item):
        assert isinstance(item, LR0Item)
        if item not in self.items:
            self.items = sorted(self.items + [item])

    def get_items(self):
        return tuple(self.items)

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        item_strs = []
        for term in self.items:
            item_strs.append(repr(term))
        return f"LRItemGroup([{','.join(item_strs)}])"

    def __hash__(self):
        return hash(self._key())

    def __eq__(self, other):
        if isinstance(other, LRItemGroup):
            return hash(self) == hash(other)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, LRItemGroup):
            if len(self._key()) == len(other._key()):
                for A, B in zip(self.get_items(), other.get_items()):
                    if A == B:
                        continue
                    return A < B
                return False # We made it all the way through the loop and all elements were equal
            else:
                return len(self._key()) < len(other._key())
        return NotImplemented

    # https://stackoverflow.com/questions/2909106/whats-a-correct-and-good-way-to-implement-hash
    def _key(self):
        return self.get_items()

    def union(self, other):
        assert isinstance(other, LRItemGroup)
        return LRItemGroup(set(other.get_items()).union(set(self.get_items())))
