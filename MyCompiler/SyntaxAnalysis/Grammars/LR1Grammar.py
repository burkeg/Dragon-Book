import copy
from LRItemGroup import LRItemGroup
from BaseGrammar import BaseGrammar
from Nonterminal import Nonterminal
from LR1Item import LR1Item
from Terminal import Terminal, end_terminal


class LR1Grammar(BaseGrammar):
    def closure(self, I):
        assert isinstance(I, LRItemGroup)
        if I in self._closure_cache:
            return self._closure_cache[I]

        self.augment()

        if len(I) == 0:
            self._closure_cache[I] = I
            return I

        # Initially, add every item in I to CLOSURE(I)
        closure = copy.copy(I)
        last_len = None

        # If A -> α . B β is in CLOSURE(I) and B -> γ is a production, then add the
        # item B -> . γ to CLOSURE(I), if it is not already there. Apply this rule
        # until no more new items can be added to CLOSURE(I).
        while last_len != len(closure):
            last_len = len(closure)

            for item in closure.get_items():
                assert isinstance(item, LR1Item)
                A = item.A
                production = item.production
                if item.dot_position >= len(production):
                    # This means the dot is to the right of the final symbol
                    continue

                alpha = production[:item.dot_position]
                B = production[item.dot_position]
                beta = production[(item.dot_position + 1):]
                a = item.lookahead
                if isinstance(B, Nonterminal):
                    for gamma in self.productions[B]:
                        for b in self.first((*beta, a)):
                            closure.add(
                                LR1Item(
                                A=B,
                                production=gamma,
                                dot_position=0,
                                lookahead=b))

        self._closure_cache[I] = closure
        return closure

    def goto(self, I, X):
        # Returns the closure of the set of all items [A -> α X . β] such that [A -> α . X β] is in I.
        assert isinstance(I, LRItemGroup)
        if (I, X) in self._goto_cache:
            return self._goto_cache[(I, X)]

        self.augment()

        goto = LRItemGroup(set())
        last_len = None

        for item in I.get_items():
            assert isinstance(item, LR1Item)
            A = item.A
            production = item.production
            if item.dot_position >= len(production):
                # This means the dot is to the right of the final symbol
                continue

            alpha = production[:item.dot_position]
            potential_X = production[item.dot_position]
            beta = production[(item.dot_position + 1):]

            if potential_X == X:
                goto.add(
                    LR1Item(
                    A=A,
                    production=item.production,
                    dot_position=item.dot_position + 1,
                    lookahead=item.lookahead))

        retval = self.closure(goto)
        self._goto_cache[(I, X)] = retval
        return retval

    def items(self):
        if self._items_cache is not None:
            return self._items_cache

        self._items_cache = dict()

        self.augment()

        C = {
            self.closure(
                LRItemGroup(
                    {
                        LR1Item(
                            A=self.start_symbol,
                            production=(self._prev_start_symbol, ),
                            dot_position=0,
                            lookahead=end_terminal)}))}

        last_len = None

        while last_len != len(C):
            last_len = len(C)

            for I in copy.copy(C):
                assert isinstance(I, LRItemGroup)
                for X in self.terminals.union(self.nonterminals):
                    goto = self.goto(I, X)
                    if len(goto) > 0:
                        C.add(goto)

        self._items_cache = C
        return sorted(C)

    def compute_all_first(self):
        super().compute_all_first()
        self._first_cache[end_terminal] = {end_terminal}
