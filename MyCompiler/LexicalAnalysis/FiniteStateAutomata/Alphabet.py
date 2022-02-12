from Elements import BaseElement


class Alphabet:
    # This describes all the elements of some alphabet sigma
    def __init__(self, elements):
        if isinstance(elements, list):
            elements = set(elements)
        assert isinstance(elements, set)
        self.elements = elements
        for element in elements:
            assert isinstance(element, BaseElement)

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
