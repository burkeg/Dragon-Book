class ActionConflict(Exception):
    pass


class BaseActionTable:
    def __init__(self):
        self._table = dict()

    def add_action(self, key, value):
        if key in self._table:
            if self._table[key] == value:
                return
            else:
                raise ActionConflict()
        self._table[key] = value

    def get_action(self, key):
        if key not in self._table:
            return None
