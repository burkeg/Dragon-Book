import math

from Enums import SpecialEscapedCharacter, ShorthandCharacterClass


class BaseElement:
    # This is some element of a language. It can be any arbitrary object,
    # not necessarily an ASCII character.
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other):
        if not isinstance(other, BaseElement):
            return False
        return hash(self) == hash(other)

    def __str__(self):
        return str(self.value)
    __repr__ = __str__

    @staticmethod
    def element_list_from_string(string):
        assert isinstance(string, str)
        elements = []
        for character in string:
            elements.append(BaseElement(character))
        return elements


class EOF(BaseElement):
    def __init__(self):
        super().__init__(value=None)


class EmptyExpression(BaseElement):
    def __init__(self):
        super().__init__(None)


# Should be produced whenever an impossible pattern is encountered.
class UnmatchableElement(BaseElement):
    def __init__(self):
        super().__init__(None)


class EscapedCharElement(BaseElement):
    def __init__(self, special_escaped_character):
        assert isinstance(special_escaped_character, SpecialEscapedCharacter)
        super().__init__(special_escaped_character)


class CharClassElement(BaseElement):
    def __init__(self, char_class):
        assert isinstance(char_class, ShorthandCharacterClass)
        super().__init__(char_class)


class QuantifierElement(BaseElement):
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop
        assert isinstance(start, int)
        assert isinstance(stop, int) or stop == math.inf
        value = f'{{{start},{stop}}}'
        if start == 0 and stop == math.inf:
            value = '*'
        elif start == 1 and stop == math.inf:
            value = '+'
        if start == 0 and stop == 1:
            value = '?'
        super().__init__(value)
