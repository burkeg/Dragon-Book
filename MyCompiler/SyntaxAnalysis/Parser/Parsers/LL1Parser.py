

class LL1Parser(BaseParser):
    def __init__(self, grammar, bypass_checks=False):
        super().__init__(grammar)
        self._table = dict()
        self._bypass_checks = bypass_checks
        self._prepare_internals()
        self._verify()

    def _prepare_internals(self):
        self._build_parsing_table()

    def _verify(self):
        assert isinstance(self._grammar, BaseGrammar)

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
                if epsilon_terminal in first_beta:
                    assert len(first_alpha.intersection(follow_A)) == 0
                if epsilon_terminal in first_alpha:
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
                    if isinstance(a, Terminal):
                        self._table[A].setdefault(type(a.token), set()).add(tuple(alpha))

                # 2. If ε is in FIRST(α), then for each terminal b in FOLLOW(A), add A -> α
                # to M[A,b]. If ε is in FIRST(α) and $ is in FOLLOW(A), add A -> α to
                # M[A,$] as well.
                if epsilon_terminal in first_alpha:
                    for b in follow_A:
                        if isinstance(b, Terminal):
                            self._table[A].setdefault(type(b.token), set()).add(tuple(alpha))

        for A, rules in self._table.items():
            if epsilon_terminal in rules.keys():
                del self._table[A][EmptyToken]

        if self._bypass_checks:
            return
        for A, rules in self._table.items():
            for a, rule in rules.items():
                assert len(rule) == 1, "This should only fail if the grammar is ambiguous which it shouldn't be."

    def produce_derivation(self, w):
        def to_input_string(tokens):
            for token in tokens:
                yield token
            yield EndToken()

        # The input string is a
        input_string = to_input_string(w)
        stack = [end_terminal, self._grammar.start_symbol]
        a = next(input_string)
        X = stack[-1]
        while X != end_terminal:
            if isinstance(X, Terminal) and isinstance(X.token, type(a)):
                stack.pop()
                yield a, None
                a = next(input_string)
            elif isinstance(X, Terminal):
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
                stack.extend(reversed([_ for _ in production if _ != epsilon_terminal]))
            X = stack[-1]
        yield a

    def to_parse_tree(self, derivation_iterator):
        A, production = next(derivation_iterator)
        curr_node = ParseTree(A)
        for i, child in enumerate(production):
            child_to_add = None
            if isinstance(child, Terminal):
                if isinstance(child.token, EmptyToken):
                    child_to_add = ParseTree(EmptyToken())
                else:
                    child_to_add = ParseTree(next(derivation_iterator))
            else:
                child_to_add = self.to_parse_tree(derivation_iterator)
            curr_node.children.append(child_to_add)

        return curr_node
