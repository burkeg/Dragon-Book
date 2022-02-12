import copy

from LRState import LRState


class MultiLRState(LRState):
    def __init__(self, lrstate):
        assert isinstance(lrstate, LRState)
        super().__init__(lr_set=lrstate._lr_set, ID=lrstate.ID)
        self.sub_states = [lrstate]

    def __repr__(self):
        return 'Multi' + super().__repr__()

    def union(self, other):
        assert isinstance(other, LRState)
        new_multi_lr_state = MultiLRState(LRState(
            lr_set=self.sub_states[0]._lr_set,
            ID=self.sub_states[0].ID))
        new_multi_lr_state.sub_states.extend(self.sub_states[1:])

        new_multi_lr_state._lr_set = self._lr_set.union(other._lr_set)
        new_multi_lr_state.ID = copy.deepcopy(self.as_list(self.ID))
        new_multi_lr_state.ID.extend(self.as_list(other.ID))
        new_multi_lr_state.ID = tuple(sorted(new_multi_lr_state.ID))
        if isinstance(other, MultiLRState):
            new_multi_lr_state.sub_states.extend(other.sub_states)
        else:
            new_multi_lr_state.sub_states.append(other)
        return new_multi_lr_state

    @staticmethod
    def as_list(id):
        unsorted_ids = [id] if not isinstance(id, list) else id
        return sorted(unsorted_ids)
