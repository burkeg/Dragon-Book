import string
from enum import Enum


class Operation(Enum):
    CONCAT = 1
    UNION = 2
    # KLEENE = 3
    GROUP = 4
    IDENTITY = 5
    # PLUS = 6
    # QUESTION = 7
    CHAR_CLASS = 8
    QUANTIFIER = 9


class SpecialCharacter(Enum):
    LEFT_PAREN = 1
    RIGHT_PAREN = 2
    UNION = 3
    KLEENE = 4
    EMPTY = 5
    PLUS = 6
    QUESTION = 7
    LEFT_SQUARE_BRACKET = 8
    RIGHT_SQUARE_BRACKET = 9
    DOT = 10
    WORD = 11
    DIGIT = 12
    WHITESPACE = 13

    def __str__(self):
            if self == SpecialCharacter.LEFT_PAREN:
                return '('
            elif self == SpecialCharacter.RIGHT_PAREN:
                return ')'
            elif self == SpecialCharacter.UNION:
                return '|'
            elif self == SpecialCharacter.KLEENE:
                return '*'
            elif self == SpecialCharacter.EMPTY:
                return 'epsilon'
            elif self == SpecialCharacter.PLUS:
                return '+'
            elif self == SpecialCharacter.QUESTION:
                return '?'
            elif self == SpecialCharacter.LEFT_SQUARE_BRACKET:
                return '['
            elif self == SpecialCharacter.RIGHT_SQUARE_BRACKET:
                return ']'
            elif self == SpecialCharacter.DOT:
                return '.'
            elif self == SpecialCharacter.WORD:
                return r'\w'
            elif self == SpecialCharacter.DIGIT:
                return r'\d'
            elif self == SpecialCharacter.WHITESPACE:
                return r'\s'
            elif self == SpecialCharacter.NEGATED_WORD:
                return r'\W'
            elif self == SpecialCharacter.NEGATED_DIGIT:
                return r'\D'
            elif self == SpecialCharacter.NEGATED_WHITESPACE:
                return r'\S'
            raise Exception('Hey dummy you forgot to add a string representation')
    __repr__ = __str__


class ShorthandCharacterClass(Enum):
    WORD = 1
    DIGIT = 2
    WHITESPACE = 3
    DOT = 4
    NEGATED_WORD = 5
    NEGATED_DIGIT = 6
    NEGATED_WHITESPACE = 7

    def to_char_set(self):
        if self == ShorthandCharacterClass.WORD:
            return set('_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        elif self == ShorthandCharacterClass.DIGIT:
            return set('0123456789')
        elif self == ShorthandCharacterClass.WHITESPACE:
            return set(' \n\t')
        elif self == ShorthandCharacterClass.DOT:
            return set(string.printable).difference(set('\n'))
        elif self == ShorthandCharacterClass.NEGATED_WORD:
            return set(string.printable).difference(ShorthandCharacterClass.WORD.to_char_set())
        elif self == ShorthandCharacterClass.NEGATED_DIGIT:
            return set(string.printable).difference(ShorthandCharacterClass.DIGIT.to_char_set())
        elif self == ShorthandCharacterClass.NEGATED_WHITESPACE:
            return set(string.printable).difference(ShorthandCharacterClass.WHITESPACE.to_char_set())
        else:
            raise Exception('Not a shorthand for a character class.')


class SpecialEscapedCharacter(Enum):
    WORD = 1
    DIGIT = 2
    WHITESPACE = 3
    TAB = 4
    NEWLINE = 5

    def __str__(self):
        # Only provide strings for escaped characters that aren't character classes
        if self == SpecialEscapedCharacter.TAB:
            return '\t'
        elif self == SpecialEscapedCharacter.NEWLINE:
            return '\n'
        raise Exception('Hey dummy you forgot to add a string representation')
    __repr__ = __str__


class Tag(Enum):
    NUM = 1,
    ID = 2,
    TRUE = 3,
    FALSE = 4