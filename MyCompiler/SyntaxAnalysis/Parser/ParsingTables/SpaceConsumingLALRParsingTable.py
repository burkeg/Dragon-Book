from functools import reduce, lru_cache

from CanonicalLRParsingTable import CanonicalLRParsingTable
from LALRGrammar import LALRGrammar
from LRState import LRState
from MultiLRState import MultiLRState


class SpaceConsumingLALRParsingTable(CanonicalLRParsingTable):
    def __init__(self, grammar):
        self._id_to_core_group_ids = dict()
        assert isinstance(grammar, LALRGrammar)
        super().__init__(grammar)

    def get_core_states(self):
        # Construct C = {I0, I1, ..., In}, the collection of sets of LR(1) items.
        C = super().get_states()

        # For each core present among the set of LR(1) items, find all sets having
        # that core, and replace these sets by their union.
        # Let Cp = {J0, J1, ..., Jn} be the resulting sets of LR(1) items.
        Cp = self.join_cores(C)
        return Cp

    def preprocess(self):
        Cp = self.get_core_states()
        # Cp groups are states with the same core
        # Let's invert the mapping to make a dictionary from original state ID to a group
        for core_group in Cp:
            for item_id in core_group:
                self._id_to_core_group_ids[item_id] = core_group

    def setup_action(self):
        # The parsing actions for state i are constructed from Ji in the same manner as
        # in Algorithm 4.56. If there is a parsing action conflict, the algorithm fails
        # to produce a parser, and the grammar is said not to be LALR(1).
        super().setup_action()
        # To accomplish this, I am overriding _get_state_ID to produce a tuple of the merged state IDs

    @lru_cache(maxsize=100)
    def _get_state_ID(self, state):
        if not isinstance(state.ID, int):
            return super()._get_state_ID(state)
        else:
            return self._id_to_core_group_ids[state.ID]

    @lru_cache(maxsize=100)
    def _get_state_from_ID(self, ID):
        if isinstance(ID, int):
            return super()._get_state_from_ID(ID)
        compound_ID = ID
        return reduce(MultiLRState.union, [MultiLRState(self._states[id]) for id in compound_ID])

    def setup_goto(self):
        super().setup_goto()
        old_goto_table = self._goto_table
        self._goto_table = dict()


        # The GOTO table is constructed as follows. If J is the union of one or
        # more sets of LR(1) items, that is, J = I1 ∪ I2 ∪ ... ∪ Ik , then the
        # cores of GOTO(I1, X), GOTO(I2, X), ..., GOTO(Ik, X) are the same, since
        # I1, I2, ..., Ik all have the same core. Let K be the union of all sets of
        # items having the same core as GOTO(I1, X). Then GOTO(J, X) = K.

        # for (I_k, X), GOTO(I_k, X) in GOTO of LR(1) items
        for (start_state, nonterminal_to_move_on), target_state in old_goto_table.items():
            start_core = self._id_to_core_group_ids[start_state]
            target_core = self._id_to_core_group_ids[target_state]
            self._goto_table[(start_core, nonterminal_to_move_on)] = target_core

        return


    def join_cores(self, C):
        core_dict = dict()
        for I in C:
            assert isinstance(I, LRState)
            core_dict.setdefault(I.get_core_hash(), []).append(I)

        # For any two I with the same core hash, combine them by taking their union.
        Cp = [tuple(sorted([state.ID for state in states])) for states in core_dict.values()]
        return Cp
