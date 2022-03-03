from Enums import Associativity
from Tokens import BaseToken


class Disambiguator:
    def __init__(self, precedence_associativity):
        assert isinstance(precedence_associativity, list)
        for token, associativity in precedence_associativity:
            assert issubclass(token, BaseToken)
            assert isinstance(associativity, Associativity)
        self._precedence_list = precedence_associativity
