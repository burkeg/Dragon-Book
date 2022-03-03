from ActionTables.BaseActionTable import BaseActionTable, ActionConflict
from Disambiguator import Disambiguator
from Tokens import EndToken
from BaseGrammar import BaseGrammar
from Enums import LRAction
from LR0Item import LR0Item
from LRState import LRState
from Nonterminal import Nonterminal
from Terminal import Terminal


class SLRParsingTable:
    def __init__(self, grammar):
        assert isinstance(grammar, BaseGrammar)
        self._grammar = grammar
        self._states = None
        self._action_table = BaseActionTable()
        self._goto_table = dict()
        self.start_state = None
        self.setup()

    def _find_state_with_item(self, item):
        assert isinstance(item, LR0Item)
        for state in self._states:
            assert isinstance(state, LRState)
            if item in state:
                return state

        return None

    def find_state(self, states, I):
        target_state = LRState(I)
        for state in states:
            if state == target_state:
                # print(f'I:{I}, target_state:{target_state}, found_state:{state}')
                return state
        else:
            return None

    def setup_goto(self):
        for i in self._states:
            assert isinstance(i, LRState)
            sorted_nonterminals = sorted(self._grammar.nonterminals)
            for A in sorted_nonterminals:
                if I_j := self._grammar.goto(i.I(), A):
                    if j := self.find_state(self._states, I_j):
                        self._goto_table[(i.ID, A)] = j.ID

    def setup_action(self):
        for state in self._states:
            # Let's determine the output transitions:
            for item in state:
                assert isinstance(item, LR0Item)
                if item.dot_position == len(item.production):
                    # Only if we are in the set that contains the starting symbol with the production
                    # where the dot is all the way on the right.
                    if item.A == self._grammar.start_symbol:
                        # (c)
                        # If [S' -> S] is in I_i, then set ACTION[i, $] to "accept."
                        key = (self._get_state_ID(state), EndToken)
                        value = (LRAction.ACCEPT, None)
                        try:
                            self._action_table.add_action(key, value)
                        except ActionConflict:
                            raise Exception('Grammar is not SLR(1), conflicting actions exist.')
                    else:
                        # (b)
                        # If [A -> α .] is in I_i, then set ACTION[i, a] to "reduce A -> α" for all
                        # a in FOLLOW(A); here A may not be S'.
                        for a in self._grammar.follow(item.A):
                            key = (self._get_state_ID(state), type(a.token))
                            value = (LRAction.REDUCE, item)
                            try:
                                self._action_table.add_action(key, value)
                            except ActionConflict:
                                raise Exception('Grammar is not SLR(1), conflicting actions exist.')
                else:
                    a = item.production[item.dot_position]

                    if isinstance(a, Terminal):
                        # (a)
                        # If [A -> α . a β] is in I_i and GOTO(I_i, a) = I_j, then set ACTION[i, a] to
                        # "shift j ." Here a must be a terminal.
                        if I_j := self._grammar.goto(state.I(), a):
                            if j := self.find_state(self._states, I_j):
                                key = (self._get_state_ID(state), type(a.token))
                                value = (LRAction.SHIFT, self._get_state_ID(j))
                                try:
                                    self._action_table.add_action(key, value)
                                except ActionConflict:
                                    raise Exception('Grammar is not SLR(1), conflicting actions exist.')

    def _get_state_ID(self, state):
        return state.ID

    def _get_state_from_ID(self, ID):
        return self._states[ID]

    def preprocess(self):
        pass

    def setup(self):
        self._states = self.get_states()


        self.start_state = self.get_start_state()
        self.preprocess()
        self.setup_goto()
        self.setup_action()

    def action(self, s, a):
        assert isinstance(s, LRState)
        assert isinstance(a, Terminal)
        key = (self._get_state_ID(s), type(a.token))
        action_table_entry = self._action_table.get_action(key)
        if action_table_entry is None:
            return LRAction.ERROR, None
        if isinstance(action_table_entry, Disambiguator):
            return action_table_entry
        action, data = action_table_entry
        if action == LRAction.SHIFT:
            return action, self._get_state_from_ID(data)
        else:
            return action, data

    def goto(self, t, A):
        assert isinstance(t, LRState)
        assert isinstance(A, Nonterminal)
        goto = self._goto_table[(self._get_state_ID(t), A)]
        return self._get_state_from_ID(goto)

    def get_states(self):
        if self._states is not None:
            return self._states
        states = [LRState(I, ID) for ID, I in enumerate(self._grammar.items())]

        # # Force the ordering to match figure 4.41
        # reorder = [9, 3, 7, 8, 5, 2, 6, 1, 4, 0]
        # states = [states[new_pos] for new_pos in reorder]
        # for i, item in enumerate(states):
        #     item.ID = i
        return states

        # states = [LRState(I, ID) for ID, I in enumerate(self._grammar.items())]
        # return states

    def get_start_state(self):
        return self._find_state_with_item(
            LR0Item(
                A=self._grammar.start_symbol,
                production=self._grammar.productions[self._grammar.start_symbol][0],
                dot_position=0))
