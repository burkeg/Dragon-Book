import copy
from itertools import combinations, tee
import pprint as pp
from enum import Enum
from functools import reduce

import Automata
import Grammar
import Tokens
import LexicalAnalyzer


class ParseTree:
    def __init__(self, symbol):
        self.symbol = symbol
        self.children = []

    # https://stackoverflow.com/questions/20242479/printing-a-tree-data-structure-in-python
    def __str__(self, level=0):
        ret = "|   "*level+repr(self)+"\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret

    def __repr__(self):
        if isinstance(self.symbol, Tokens.EmptyToken):
            return 'ε'
        return repr(self.symbol)


class Parser:
    def __init__(self, grammar):
        assert isinstance(grammar, Grammar.Grammar)
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


class LL1Parser(Parser):
    def __init__(self, grammar, bypass_checks=False):
        super().__init__(grammar)
        self._table = dict()
        self._bypass_checks = bypass_checks
        self._prepare_internals()
        self._verify()

    def _prepare_internals(self):
        self._build_parsing_table()

    def _verify(self):
        assert isinstance(self._grammar, Grammar.Grammar)

        if self._bypass_checks:
            return
        # A grammar G is LL(1) if and only if whenever A -> α | β are two distinct
        # productions of G, the following conditions hold:
        # 1. For no terminal a do both α and β derive strings beginning with a.
        # 2. At most one of α and β can derive the empty string.
        # 3. If β =*> ε, then α does not derive any string beginning with a terminal
        # in FOLLOW(A). Likewise, if α =*> ε, then β does not derive any string
        # beginning with a terminal in FOLLOW(A).

        for A, productions in self._grammar.productions.items():
            for i, j in combinations(range(len(productions)), 2):
                alpha = productions[i]
                beta = productions[j]
                first_alpha = self._grammar.first(alpha)
                first_beta = self._grammar.first(beta)

                # condition 1 and 2. AKA FIRST(α) and FIRST(β) are disjoint sets.
                assert len(first_alpha.intersection(first_beta)) == 0

                follow_A = self._grammar.follow(A)
                # condition 3. AKA if ε is in FIRST(β), FIRST(α) and FOLLOW(A) must be disjoint sets,
                # likewise if ε is in FIRST(α).
                if Grammar.Terminal._epsilon in first_beta:
                    assert len(first_alpha.intersection(follow_A)) == 0
                if Grammar.Terminal._epsilon in first_alpha:
                    assert len(first_beta.intersection(follow_A)) == 0

    def _build_parsing_table(self):
        for nonterminal in self._grammar.nonterminals:
            self._table[nonterminal] = dict()

        for A, productions in self._grammar.productions.items():
            for alpha in productions:
                first_alpha = self._grammar.first(alpha)
                follow_A = self._grammar.follow(A)

                # 1. For each terminal a in FIRST(α), add A -> α to M[A,a].
                for a in first_alpha:
                    if isinstance(a, Grammar.Terminal):
                        self._table[A].setdefault(type(a.token), set()).add(tuple(alpha))

                # 2. If ε is in FIRST(α), then for each terminal b in FOLLOW(A), add A -> α
                # to M[A,b]. If ε is in FIRST(α) and $ is in FOLLOW(A), add A -> α to
                # M[A,$] as well.
                if Grammar.Terminal._epsilon in first_alpha:
                    for b in follow_A:
                        if isinstance(b, Grammar.Terminal):
                            self._table[A].setdefault(type(b.token), set()).add(tuple(alpha))

        for A, rules in self._table.items():
            if Grammar.Terminal._epsilon in rules.keys():
                del self._table[A][Tokens.EmptyToken]

        if self._bypass_checks:
            return
        for A, rules in self._table.items():
            for a, rule in rules.items():
                assert len(rule) == 1, "This should only fail if the grammar is ambiguous which it shouldn't be."

    def produce_derivation(self, w):
        def to_input_string(tokens):
            for token in tokens:
                yield token
            yield Tokens.EndToken()

        # The input string is a
        input_string = to_input_string(w)
        stack = [Grammar.Terminal._end, self._grammar.start_symbol]
        a = next(input_string)
        X = stack[-1]
        while X != Grammar.Terminal._end:
            if isinstance(X, Grammar.Terminal) and isinstance(X.token, type(a)):
                stack.pop()
                yield a, None
                a = next(input_string)
            elif isinstance(X, Grammar.Terminal):
                raise Exception('Error')
            elif type(a) not in self._table[X]:
                raise Exception('Error')
            else:
                # output the production
                productions = self._table[X][type(a)]
                if len(productions) > 1:
                    raise Exception('Special care needed here, this grammar is ambiguous')
                production = next(iter(productions))
                # print((X, production))
                yield (X, production)
                stack.pop()
                stack.extend(reversed([_ for _ in production if _ != Grammar.Terminal._epsilon]))
            X = stack[-1]
        yield a

    def to_parse_tree(self, derivation_iterator):
        A, production = next(derivation_iterator)
        curr_node = ParseTree(A)
        for i, child in enumerate(production):
            child_to_add = None
            if isinstance(child, Grammar.Terminal):
                if isinstance(child.token, Tokens.EmptyToken):
                    child_to_add = ParseTree(Tokens.EmptyToken())
                else:
                    child_to_add = ParseTree(next(derivation_iterator))
            else:
                child_to_add = self.to_parse_tree(derivation_iterator)
            curr_node.children.append(child_to_add)

        return curr_node


class LRState(Automata.DFAState):
    def __init__(self, lr_set, ID=-1):
        assert isinstance(lr_set, Grammar.LRItemGroup)
        super().__init__(name=repr(lr_set), ID=ID)
        self._lr_set = lr_set

    def I(self):
        return self._lr_set

    def get_core_hash(self):
        # By looking at each LR1 item as an LR0 item we can hash on each item to find shared cores
        return hash(tuple(sorted({hash(Grammar.LR0Item._key(item)) for item in self})))

    # https://stackoverflow.com/questions/2909106/whats-a-correct-and-good-way-to-implement-hash
    def _key(self):
        return self._lr_set

    def __hash__(self):
        return hash(self._key())

    def __eq__(self, other):
        if isinstance(other, LRState):
            return self._key() == other._key()
        return NotImplemented

    def __repr__(self):
        return f'LRState({repr(self._lr_set)}, ID={self.ID})'

    def __contains__(self, key):
        return key in self._lr_set.get_items()

    def __iter__(self):
        return iter(self._lr_set.get_items())

    def __lt__(self, other):
        if isinstance(other, LRState):
            return self._lr_set < other._lr_set
        return NotImplemented

    def union(self, other):
        assert isinstance(other, LRState)
        return MultiLRState(self).union(other)


class MultiLRState(LRState):
    def __init__(self, lrstate):
        assert isinstance(lrstate, LRState)
        super().__init__(lr_set=lrstate._lr_set, ID=lrstate.ID)
        self.sub_states = [lrstate]

    def __repr__(self):
        return 'Multi' + super().__repr__()

    def union(self, other):
        assert isinstance(other, LRState)
        new_multi_lr_state = MultiLRState(LRState(self.sub_states[0]._lr_set, self.sub_states[0].ID))
        new_multi_lr_state.sub_states.extend(self.sub_states[1:])

        new_multi_lr_state._lr_set = self._lr_set.union(other._lr_set)
        new_multi_lr_state.ID = f'{self.ID}{other.ID}'
        if isinstance(other, MultiLRState):
            new_multi_lr_state.sub_states.extend(other.sub_states)
        else:
            new_multi_lr_state.sub_states.append(other)
        return new_multi_lr_state



class LRAction(Enum):
    SHIFT = 1
    REDUCE = 2
    ACCEPT = 3
    ERROR = 4


class SLRParsingTable:
    def __init__(self, grammar):
        assert isinstance(grammar, Grammar.Grammar)
        self._grammar = grammar
        self._states = []
        self._action_table = dict()
        self._goto_table = dict()
        self.start_state = None
        self.setup()

    def _find_state_with_item(self, item):
        assert isinstance(item, Grammar.LR0Item)
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
                assert isinstance(item, Grammar.LR0Item)
                if item.dot_position == len(item.production):
                    # Only if we are in the set that contains the starting symbol with the production
                    # where the dot is all the way on the right.
                    if item.A == self._grammar.start_symbol:
                        # (c)
                        # If [S' -> S] is in I_i, then set ACTION[i, $] to "accept."
                        key = (state.ID, Tokens.EndToken)
                        value = (LRAction.ACCEPT, None)
                        assert key not in self._action_table or self._action_table[key] == value, \
                            'Grammar is not SLR(1), conflicting actions exist.'
                        self._action_table[key] = value
                    else:
                        # (b)
                        # If [A -> α .] is in I_i, then set ACTION[i, a] to "reduce A -> α" for all
                        # a in FOLLOW(A); here A may not be S'.
                        for a in self._grammar.follow(item.A):
                            key = (state.ID, type(a.token))
                            value = (LRAction.REDUCE, item)
                            assert key not in self._action_table or self._action_table[key] == value, \
                                'Grammar is not SLR(1), conflicting actions exist.'
                            self._action_table[key] = value
                else:
                    a = item.production[item.dot_position]

                    if isinstance(a, Grammar.Terminal):
                        # (a)
                        # If [A -> α . a β] is in I_i and GOTO(I_i, a) = I_j, then set ACTION[i, a] to
                        # "shift j ." Here a must be a terminal.
                        if I_j := self._grammar.goto(state.I(), a):
                            if j := self.find_state(self._states, I_j):
                                key = (state.ID, type(a.token))
                                value = (LRAction.SHIFT, j.ID)
                                assert key not in self._action_table or self._action_table[key] == value, \
                                    'Grammar is not SLR(1), conflicting actions exist.'

                                self._action_table[key] = value

    def setup(self):
        self._states = self.get_states()

        self.start_state = self.get_start_state()

        self.setup_goto()
        self.setup_action()

    def action(self, s, a):
        assert isinstance(s, LRState)
        assert isinstance(a, Grammar.Terminal)
        key = (s.ID, type(a.token))
        if key not in self._action_table:
            return LRAction.ERROR, None
        action, data = self._action_table[key]
        if action == LRAction.SHIFT:
            return action, self._states[data]
        else:
            return action, data

    def goto(self, t, A):
        assert isinstance(t, LRState)
        assert isinstance(A, Grammar.Nonterminal)
        goto = self._goto_table[(t.ID, A)]
        return self._states[goto]

    def get_states(self):
        return [LRState(I, ID) for ID, I in enumerate(self._grammar.items())]

    def get_start_state(self):
        return self._find_state_with_item(
            Grammar.LR0Item(
                A=self._grammar.start_symbol,
                production=self._grammar.productions[self._grammar.start_symbol][0],
                dot_position=0))

class CanonicalLRParsingTable(SLRParsingTable):
    def __init__(self, grammar):
        assert isinstance(grammar, Grammar.LR1Grammar)
        super().__init__(grammar)

    def setup_action(self):
        for state in self._states:
            # Let's determine the output transitions:
            for item in state:
                assert isinstance(item, Grammar.LR1Item)
                if item.dot_position == len(item.production):
                    # Only if we are in the set that contains the starting symbol with the production
                    # where the dot is all the way on the right.
                    if item.A == self._grammar.start_symbol and isinstance(item.lookahead.token, Tokens.EndToken):
                        # (c)
                        # If [S' -> S, $] is in I_i, then set ACTION[i, $] to "accept."
                        key = (state.ID, Tokens.EndToken)
                        value = (LRAction.ACCEPT, None)
                        assert not (key in self._action_table and self._action_table[key] != value), \
                            'Grammar is not LR(1), conflicting actions exist.'
                        self._action_table[key] = value
                    else:
                        # (b)
                        # If [A -> α .] is in I_i, A != S' then set ACTION[i, a] to "reduce A -> α"
                        key = (state.ID, type(item.lookahead.token))
                        value = (LRAction.REDUCE, item)
                        assert not (key in self._action_table and self._action_table[key] != value), \
                            'Grammar is not LR(1), conflicting actions exist.'
                        self._action_table[key] = value
                else:
                    a = item.production[item.dot_position]

                    if isinstance(a, Grammar.Terminal):
                        # (a)
                        # If [A -> α . a β, b] is in I_i and GOTO(I_i, a) = I_j, then set ACTION[i, a] to
                        # "shift j ." Here a must be a terminal.
                        if I_j := self._grammar.goto(state.I(), a):
                            if j := self.find_state(self._states, I_j):
                                key = (state.ID, type(a.token))
                                value = (LRAction.SHIFT, j.ID)
                                assert not (key in self._action_table and self._action_table[key] != value), \
                                    'Grammar is not LR(1), conflicting actions exist.'

                                self._action_table[key] = value

    def get_start_state(self):
        return self._find_state_with_item(
            Grammar.LR1Item(
                A=self._grammar.start_symbol,
                production=self._grammar.productions[self._grammar.start_symbol][0],
                dot_position=0,
                lookahead=Grammar.Terminal._end))


class SLR1Parser(Parser):
    def __init__(self, grammar):
        assert isinstance(grammar, Grammar.Grammar)
        super().__init__(grammar)
        self._parsing_table = None
        self._prepare_internals()
        self._verify()

    def _verify(self):
        pass

    def _prepare_internals(self):
        self._parsing_table = SLRParsingTable(self._grammar)

    def produce_derivation(self, w):
        assert isinstance(self._parsing_table, SLRParsingTable)
        def to_input_string(tokens):
            for token in tokens:
                yield Grammar.Terminal(token=token)
            yield Grammar.Terminal._end

        # The input string is a
        input_string = to_input_string(w)
        stack = [self._parsing_table.start_state]
        a = next(input_string)
        while True:
            s = stack[-1]
            action, data = self._parsing_table.action(s, a)
            if action == LRAction.SHIFT:
                t = data
                assert isinstance(t, LRState)
                stack.append(t)
                yield a.token, None
                a = next(input_string)

            elif action == LRAction.REDUCE:
                item = data
                assert isinstance(item, Grammar.LR0Item)
                for _ in item.production:
                    stack.pop(-1)
                t = stack[-1]
                stack.append(self._parsing_table.goto(t, item.A))
                yield item.A, item.production

            elif action == LRAction.ACCEPT:
                # Success!
                break
            elif action == LRAction.ERROR:
                # Handle error
                break
            else:
                raise Exception('Unknown action.')

    def to_parse_tree(self, derivation_iterator):
        children = []
        for data in derivation_iterator:
            if data[1] == None:
                child_token = data[0]
                # This is a terminal, we just shifted out a token
                children.append(ParseTree(child_token))
            else:
                parent = data[0]
                production = data[1]
                # assert len(production) == len(children)
                parent_tree = ParseTree(parent)
                parent_tree.children = children[-len(production):]
                children[-len(production):] = [parent_tree]
        assert len(children) == 1
        return children[0]


class CanonicalLR1Parser(SLR1Parser):
    def _prepare_internals(self):
        if not isinstance(self._grammar, Grammar.LR1Grammar):
            self._grammar = Grammar.LR1Grammar(
                terminals=self._grammar.terminals,
                nonterminals=self._grammar.nonterminals,
                productions=self._grammar.productions,
                start_symbol=self._grammar.start_symbol,
                prev_start_symbol=self._grammar._prev_start_symbol)
        self._parsing_table = CanonicalLRParsingTable(self._grammar)


class SpaceConsumingLALRParser(CanonicalLR1Parser):
    def _prepare_internals(self):
        if not isinstance(self._grammar, Grammar.LALRGrammar):
            self._grammar = Grammar.LALRGrammar(
                terminals=self._grammar.terminals,
                nonterminals=self._grammar.nonterminals,
                productions=self._grammar.productions,
                start_symbol=self._grammar.start_symbol,
                prev_start_symbol=self._grammar._prev_start_symbol)
        self._parsing_table = SpaceConsumingLALRParsingTable(self._grammar)


class SpaceConsumingLALRParsingTable(CanonicalLRParsingTable):
    def __init__(self, grammar):
        assert isinstance(grammar, Grammar.LALRGrammar)
        super().__init__(grammar)

    def get_states(self):
        # Construct C = {I0, I1, ..., In}, the collection of sets of LR(1) items.
        C = super().get_states()

        # For each core present among the set of LR(1) items, find all sets having
        # that core, and replace these sets by their union.
        # Let Cp = {J0, J1, ..., Jn} be the resulting sets of LR(1) items.
        Cp = self.join_cores(C)
        return Cp

    def setup_action(self):
        # The parsing actions for state i are constructed from Ji in the same manner as
        # in Algorithm 4.56. If there is a parsing action conflict, the algorithm fails
        # to produce a parser, and the grammar is said not to be LALR(1).
        super().setup_action()

    def setup_goto(self):
        super().setup_goto()
        old_goto_table = self._goto_table
        print()

    def join_cores(self, C):
        core_dict = dict()
        for I in C:
            assert isinstance(I, LRState)
            core_dict.setdefault(I.get_core_hash(), []).append(I)

        # For any two I with the same core hash, combine them by taking their union.
        Cp = [reduce(LRState.union, states) for states in core_dict.values()]
        return Cp


def do_stuff():
    # grammar = Grammar.TextbookGrammar('4.28')
    # grammar = Grammar.TextbookGrammar('4.40_2')
    grammar = Grammar.TextbookGrammar('4.55')
    # parser = LL1Parser(grammar)
    # parser = SLR1Parser(grammar)
    parser = CanonicalLR1Parser(grammar)
    lexer = LexicalAnalyzer.LexicalAnalyzer.ANSI_C_lexer()
    tokens = lexer.process(
        # """
        # a + b * c
        # """
        """
        c 0 c 0
        """
    )
    list_tokens = list(tokens)
    # pp.pprint(list_tokens)
    productions = parser.produce_derivation(iter(list_tokens))
    list_productions = list(productions)
    # pp.pprint(list_productions)
    tree = parser.to_parse_tree(iter(list_productions))
    # print(tree)


    # g = Grammar.TextbookGrammar('4.40_2')
    # g.augment()
    # lr1 = LR1Parser(g)
    # lexer = LexicalAnalyzer.LexicalAnalyzer.default_lexer()
    # tokens = lexer.process(
    #     """
    #     a*b+c
    #     """
    # )
    # list_tokens = list(tokens)
    # print(list_tokens)
    # productions = lr1.produce_derivation(iter(list_tokens))
    # tree = lr1.to_parse_tree(productions)
    # print(tree)

    # g = Grammar.TextbookGrammar('4.28')
    # ll1 = LL1Parser(g)
    # lexer = LexicalAnalyzer.LexicalAnalyzer.default_lexer()
    # tokens = list(lexer.process(
    #     """
    #     a*b+c
    #     """
    # ))
    # print(tokens)
    # productions = ll1.produce_derivation(iter(tokens))
    # tree = ll1.to_parse_tree(productions)
    # print(tree)


if __name__ == '__main__':
    do_stuff()
