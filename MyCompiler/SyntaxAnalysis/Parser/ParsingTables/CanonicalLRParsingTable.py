from Tokens import EndToken
from Enums import LRAction
from LR1Grammar import LR1Grammar
from LR1Item import LR1Item
from SLRParsingTable import SLRParsingTable
from Terminal import Terminal, end_terminal


class CanonicalLRParsingTable(SLRParsingTable):
    def __init__(self, grammar):
        assert isinstance(grammar, LR1Grammar)
        super().__init__(grammar)

    def setup_action(self):
        for state in self._states:
            # Let's determine the output transitions:
            for item in state:
                assert isinstance(item, LR1Item)
                if item.dot_position == len(item.production):
                    # Only if we are in the set that contains the starting symbol with the production
                    # where the dot is all the way on the right.
                    if item.A == self._grammar.start_symbol and isinstance(item.lookahead.token, EndToken):
                        # (c)
                        # If [S' -> S, $] is in I_i, then set ACTION[i, $] to "accept."
                        key = (self._get_state_ID(state), EndToken)
                        value = (LRAction.ACCEPT, None)
                        assert not (key in self._action_table and self._action_table[key] != value), \
                            'Grammar is not LR(1), conflicting actions exist.'
                        self._action_table[key] = value
                    else:
                        # (b)
                        # If [A -> α .] is in I_i, A != S' then set ACTION[i, a] to "reduce A -> α"
                        key = (self._get_state_ID(state), type(item.lookahead.token))
                        value = (LRAction.REDUCE, item)
                        assert not (key in self._action_table and self._action_table[key] != value), \
                            'Grammar is not LR(1), conflicting actions exist.'
                        self._action_table[key] = value
                else:
                    a = item.production[item.dot_position]

                    if isinstance(a, Terminal):
                        # (a)
                        # If [A -> α . a β, b] is in I_i and GOTO(I_i, a) = I_j, then set ACTION[i, a] to
                        # "shift j ." Here a must be a terminal.
                        if I_j := self._grammar.goto(state.I(), a):
                            if j := self.find_state(self._states, I_j):
                                key = (self._get_state_ID(state), type(a.token))
                                value = (LRAction.SHIFT, self._get_state_ID(j))
                                assert not (key in self._action_table and self._action_table[key] != value), \
                                    'Grammar is not LR(1), conflicting actions exist.'

                                self._action_table[key] = value

    def get_start_state(self):
        return self._find_state_with_item(
            LR1Item(
                A=self._grammar.start_symbol,
                production=self._grammar.productions[self._grammar.start_symbol][0],
                dot_position=0,
                lookahead=end_terminal))
