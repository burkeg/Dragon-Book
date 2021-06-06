import copy
import itertools

import Grammar
import Tokens


class ParseTree:
    def __init__(self, symbol):
        self.symbol = symbol
        self.children = []

    # https://stackoverflow.com/questions/20242479/printing-a-tree-data-structure-in-python
    def __str__(self, level=0):
        ret = "|   "*level+repr(self.symbol)+"\n"
        for child in self.children:
            ret += child.__str__(level+1)
        return ret

    def __repr__(self):
        return repr(self.symbol)


class Parser:
    pass


class LL1Parser(Parser):
    def __init__(self, grammar, bypass_checks=False):
        self._grammar = grammar
        self._table = dict()
        self._bypass_checks = bypass_checks
        self._verify()
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
            for i, j in itertools.combinations(range(len(productions)), 2):
                alpha = productions[i]
                beta = productions[j]
                first_alpha = self._grammar.first(alpha)
                first_beta = self._grammar.first(beta)

                # condition 1 and 2. AKA FIRST(α) and FIRST(β) are disjoint sets.
                assert len(first_alpha.intersection(first_beta)) == 0

                follow_A = self._grammar.follow(A)
                # condition 3. AKA if ε is in FIRST(β), FIRST(α) and FOLLOW(A) must be disjoint sets,
                # likewise if ε is in FIRST(α).
                if Grammar.Terminal.epsilon in first_beta:
                    assert len(first_alpha.intersection(follow_A)) == 0
                if Grammar.Terminal.epsilon in first_alpha:
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
                        self._table[A].setdefault(a, set()).add(tuple(alpha))

                # 2. If ε is in FIRST(α), then for each terminal b in FOLLOW(A), add A -> α
                # to M[A,b]. If ε is in FIRST(α) and $ is in FOLLOW(A), add A -> α to
                # M[A,$] as well.
                if Grammar.Terminal.epsilon in first_alpha:
                    for b in follow_A:
                        if isinstance(b, Grammar.Terminal):
                            self._table[A].setdefault(b, set()).add(tuple(alpha))
                            # if Grammar.Terminal(string='$') in follow_A:
                            #     self._table[A].setdefault(Grammar.Terminal(string='$'), set()).add(tuple(alpha))

        for A, rules in self._table.items():
            if Grammar.Terminal.epsilon in rules.keys():
                del self._table[A][Grammar.Terminal.epsilon]

        if self._bypass_checks:
            return
        for A, rules in self._table.items():
            for a, rule in rules.items():
                assert len(rule) == 1, "This should only fail if the grammar is ambiguous which it shouldn't be."

    def produce_derivation(self, w):
        input_string = [Grammar.Terminal(token=term) for term in w] + [Grammar.Terminal.end]
        stack = [Grammar.Terminal.end, self._grammar.start_symbol]
        a = input_string.pop(0)
        X = stack[-1]
        while X != Grammar.Terminal.end:
            if X == a:
                stack.pop()
                a = input_string.pop(0)
            elif isinstance(X, Grammar.Terminal):
                raise Exception('Error')
            elif a not in self._table[X]:
                raise Exception('Error')
            else:
                # output the production
                productions = self._table[X][a]
                if len(productions) > 1:
                    raise Exception('Special care needed here, this grammar is ambiguous')
                production = next(iter(productions))
                yield (X, production)
                stack.pop()
                stack.extend(reversed([_ for _ in production if _ != Grammar.Terminal.epsilon]))
            X = stack[-1]

    def to_parse_tree(self, derivation_iterator):
        A, production = next(derivation_iterator)
        curr_node = ParseTree(A)
        for i, child in enumerate(production):
            child_to_add = None
            if isinstance(child, Grammar.Terminal):
                child_to_add = ParseTree(child)
            else:
                child_to_add = self.to_parse_tree(derivation_iterator)
            curr_node.children.append(child_to_add)

        return curr_node





def do_stuff():
    g = Grammar.TextbookGrammar('4.28')
    print(g)
    ll1 = LL1Parser(g)

    as_strings = ['id', '+', 'id', '*', 'id']
    productions = ll1.produce_derivation([Tokens.Token.create(string) for string in as_strings])
    tree = ll1.to_parse_tree(productions)
    print(tree)


if __name__ == '__main__':
    do_stuff()