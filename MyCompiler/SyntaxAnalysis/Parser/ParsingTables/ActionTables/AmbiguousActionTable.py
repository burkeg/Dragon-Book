from BaseActionTable import BaseActionTable
from Disambiguator import Disambiguator


class AmbiguousActionTable(BaseActionTable):
    def __init__(self, disambiguator):
        super().__init__()
        assert isinstance(disambiguator, Disambiguator)
        self._disambiguator = disambiguator

    def add_action(self, key, value):
        self._table.setdefault(key, set()).add(value)

    def get_action(self, key):
        if key not in self._table:
            return None
        action_table_entry = list(self._table[key])
        if len(action_table_entry) == 1:
            return action_table_entry[0]
        else:
            raise Exception('Need to disambiguate.')

        #  We need to make a decision on how to resolve this ambiguity
