from BaseGrammar import BaseGrammar


class BaseParser:
    def __init__(self, grammar):
        assert isinstance(grammar, BaseGrammar)
        self._grammar = grammar

    def _verify(self):
        raise NotImplementedError()

    def _prepare_internals(self):
        raise NotImplementedError()

    def produce_derivation(self, w):
        raise NotImplementedError()

    def to_parse_tree(self, derivation_iterator):
        raise NotImplementedError()

    def _prepare_internals(self):
        raise NotImplementedError()

