import copy
import re
import os

import Tokens


class GrammarSymbol:
    def __init__(self, string):
        self.string = string

    # https://stackoverflow.com/questions/2909106/whats-a-correct-and-good-way-to-implement-hash
    def _key(self):
        return self.string

    def __hash__(self):
        return hash(self._key())

    def __eq__(self, other):
        if isinstance(other, GrammarSymbol):
            return self._key() == other._key()
        return NotImplemented

    def __repr__(self):
        return repr(self.string)

    def __lt__(self, other):
        return self.string < other.string


class Terminal(GrammarSymbol):
    _epsilon = None
    _end = None
    def __init__(self, string=None, token=None):
        self.token = None
        assert string is not None or token is not None
        if token is not None and string is not None:
            assert isinstance(token, Tokens.Token)
            self.token = token
            self.string = string
        elif string is not None:
            self.token = Tokens.Token.create(string)
            self.string = f"'{self.token.lexeme}'"
        elif token is not None:
            self.token = token
            self.string = f"'{self.token.lexeme}'"
        else:
            raise Exception('Not a valid terminal')
        super().__init__(self.string)

    def __str__(self):
        return self.string

    __repr__ = __str__


Terminal._epsilon = Terminal(string='ε')
Terminal._end = Terminal(string='$')


class ActionTerminal(Terminal):
    def __init__(self, action_name, action):
        super().__init__(action_name, Tokens.ActionToken(action_name, action))


class Nonterminal(GrammarSymbol):
    def derive_from(self, suffix_gen):
        return Nonterminal(f'{self.string}_{str(next(suffix_gen))}')


class LR0Item:
    def __init__(self, A, production, dot_position):
        assert isinstance(A, Nonterminal)
        assert isinstance(production, tuple)
        assert isinstance(dot_position, int)
        self.A = A
        self.production = production
        self.dot_position = dot_position

    def __repr__(self):
        ret_str = f'{repr(self.A)} -> '
        production_strs = []
        for term in self.production:
            production_strs.append(repr(term))
        production_strs.insert(self.dot_position, '.')
        return f"LR0Item({ret_str + ' '.join(production_strs)})"

    # https://stackoverflow.com/questions/2909106/whats-a-correct-and-good-way-to-implement-hash
    def _key(self):
        return (self.A, self.production, self.dot_position)

    def __hash__(self):
        return hash(self._key())

    def __eq__(self, other):
        if isinstance(other, LR0Item):
            return hash(self) == hash(other)
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, LR0Item):
            return self._key() < other._key()
        return NotImplemented



class LR1Item(LR0Item):
    def __init__(self, A, production, dot_position, lookahead):
        super().__init__(A, production, dot_position)
        assert isinstance(lookahead, Terminal)
        self.lookahead = lookahead

    def __repr__(self):
        ret_str = f'{repr(self.A)} -> '
        production_strs = []
        for term in self.production:
            production_strs.append(repr(term))
        production_strs.insert(self.dot_position, '.')
        return f"LR1Item({ret_str + ' '.join(production_strs)}, {self.lookahead})"

    # https://stackoverflow.com/questions/2909106/whats-a-correct-and-good-way-to-implement-hash
    def _key(self):
        return (self.A, self.production, self.dot_position, self.lookahead)


class Grammar:
    def __init__(self, terminals, nonterminals, productions, start_symbol, prev_start_symbol=None):
        assert isinstance(terminals, set)
        assert isinstance(nonterminals, set)
        assert isinstance(productions, dict)
        self.terminals = terminals  # A set of terminals
        self.nonterminals = nonterminals  # A set of nonterminals
        self.productions = productions  # A dictionary of nonterminals to lists of terminals/nonterminals
        self.start_symbol = start_symbol  # The starting point for all derivations from this grammar
        self._verify()
        self._first_cache = None
        self._follow_cache = None
        self._closure_cache = dict()
        self._goto_cache = dict()
        self._items_cache = None
        self._prev_start_symbol = prev_start_symbol
        self._suffix_gen = self._suffix_gen_func()

    def __str__(self):
        return '------------------------\n' \
               f'terminals: {self.terminals}\n' \
               f'nonterminals: {self.nonterminals}\n' \
               f'productions: {self.productions}\n' \
               f'start_symbol: {self.start_symbol}'

    __repr__ = __str__

    @staticmethod
    def _suffix_gen_func():
        cnt = 1
        while True:
            yield cnt
            cnt += 1

    def simplify(self):
        for A, productions in self.productions.items():
            new_productions = []
            for production in productions:
                new_production = []
                for term in production:
                    if isinstance(term, Terminal) and \
                            isinstance(term.token, Tokens.EmptyToken):
                        continue
                    else:
                        new_production.append(term)
                if len(new_production) == 1 and new_production[0] == A:
                    continue
                elif len(new_production) == 0:
                    new_productions.append((Terminal(string='ε'),))
                else:
                    new_productions.append(tuple(new_production))
            self.productions[A] = new_productions

        found_terminals = set()
        for terminal in self.terminals:
            for A, productions in self.productions.items():
                for production in productions:
                    for symbol in production:
                        if isinstance(symbol, Terminal):
                            found_terminals.add(symbol)

        found_nonterminals = {self.start_symbol}
        for nonterminal in self.nonterminals:
            for A, productions in self.productions.items():
                if A == nonterminal:
                    continue
                for production in productions:
                    for symbol in production:
                        if isinstance(symbol, Nonterminal):
                            found_nonterminals.add(symbol)

        self.terminals = found_terminals
        for nonterminal in self.nonterminals.difference(found_nonterminals):
            del self.productions[nonterminal]
        self.nonterminals = found_nonterminals

    def _verify(self):
        for nonterminal, production_list in self.productions.items():
            assert isinstance(nonterminal, Nonterminal)
            for production in production_list:
                assert isinstance(production, tuple)
                for item in production:
                    assert isinstance(item, Terminal) or isinstance(item, Nonterminal)

    def __copy__(self):
        new_start_symbol = self.start_symbol
        new_terminals = copy.copy(self.terminals)
        new_nonterminals = copy.copy(self.nonterminals)
        new_productions = dict()
        for nonterminal, production_list in self.productions.items():
            productions = [copy.copy(production) for production in production_list]
            new_productions[nonterminal] = productions
        new_grammar = self.__class__(
            terminals=new_terminals,
            nonterminals=new_nonterminals,
            productions=new_productions,
            start_symbol=new_start_symbol,
            prev_start_symbol=self._prev_start_symbol)
        new_grammar._prev_start_symbol = self._prev_start_symbol
        return new_grammar

    @staticmethod
    def from_string(grammar_as_string, action_dict=None):
        # Nonterminals are strings of \w.
        # Terminals are strings enclosed in quotes.
        # A production is a Nonterminal followed by -> and a list of terminals/nonterminals.
        # As shorthand multiple productions can be separated by a | on the right hand side.
        # A single production rule must be contained on 1 line.
        # All terminals and non terminals are separated by whitespace.
        # Start symbol is the first nonterminal defined.
        start_symbol = None
        productions = dict()
        current_nonterminal = None
        for line in grammar_as_string.split('\n'):
            rest_of_line = line.strip()
            if len(rest_of_line) == 0:
                continue
            if m := re.match(r'^(\w+)\s*->(.*)$', rest_of_line):
                # This is a definition of a nonterminal, let's figure out its name
                current_nonterminal = Nonterminal(m.group(1))
                rest_of_line = m.group(2).strip()
                if start_symbol is None:
                    start_symbol = current_nonterminal
            elif m := re.match(r'^\|(.*)$', rest_of_line):
                # we are on a new line doing a shorthand production
                rest_of_line = m.group(1).strip()
            if len(rest_of_line) == 0:
                continue

            current_rule = []
            # Let's keep grabbing productions rules from the string until none remain
            while len(rest_of_line) > 0:
                if m := re.match(r'^(\w+)(.*)$', rest_of_line):
                    # Found nonterminal
                    current_rule.append(Nonterminal(m.group(1)))
                    rest_of_line = m.group(2).strip()
                elif m := re.match(r'^\'([^\']+?)\'(.*)$', rest_of_line):
                    # Found terminal
                    terminal_str = m.group(1)
                    current_rule.append(Terminal(terminal_str))
                    rest_of_line = m.group(2).strip()
                elif m := re.match(r'^{([^{]+?)}(.*)$', rest_of_line):
                    # Found action
                    action_terminal_str = m.group(1)
                    assert action_terminal_str in action_dict.keys(), 'Action not found in action dictionary'
                    current_rule.append(ActionTerminal(action_terminal_str, action_dict[action_terminal_str]))
                    rest_of_line = m.group(2).strip()
                elif m := re.match(r'^\|(.*)$', rest_of_line):
                    # shorthand for starting up another production on this line
                    productions.setdefault(current_nonterminal, []).append(tuple(current_rule))
                    current_rule = []
                    rest_of_line = m.group(1).strip()
                else:
                    raise Exception('Expected a nonterminal, terminal or | before "' + rest_of_line + '"')

            productions.setdefault(current_nonterminal, []).append(tuple(current_rule))
        nonterminals = set(productions.keys())
        all_rhs_symbols = set([symbol
                               for productions_for_rule in productions.values()
                               for production in productions_for_rule
                               for symbol in production])
        terminals = all_rhs_symbols.difference(nonterminals)
        return Grammar(terminals, nonterminals, productions, start_symbol)

    def without_left_recursion(self):
        new_grammar = copy.copy(self)
        # A = list(reversed(sorted(list(new_grammar.nonterminals))))
        A = sorted(new_grammar.nonterminals)
        for i in range(len(A)):
            for j in range(i):
                # Replace each production of the form A_i -> A_j y by the
                # productions A_i -> s_1 y | s_2 y | ... s_k y, where
                # A_j -> s_1 | s_2 | ... s_k for all current A_j productions
                replaced_productions = []
                for production_i in new_grammar.productions[A[i]]:
                    if production_i[0] == A[j]:
                        y = production_i[1:]
                        for s in new_grammar.productions[A[j]]:
                            replaced_productions.append(s + y)
                    else:
                        replaced_productions.append(production_i)
                new_grammar.productions[A[i]] = replaced_productions

            # eliminate the immediate left recursion among the A_i-productions
            A_i_productions, A_ip_and_productions = self.without_immediate_left_recursion(
                A=A[i],
                productions=new_grammar.productions[A[i]])

            new_grammar.productions[A[i]] = A_i_productions
            if A_ip_and_productions:
                A_ip, A_ip_productions = A_ip_and_productions
                new_grammar.productions[A_ip] = A_ip_productions
                new_grammar.nonterminals.add(A_ip)
                new_grammar.terminals.add(Terminal(string='ε'))
        new_grammar.simplify()
        return new_grammar

    def without_immediate_left_recursion(self, A, productions):
        assert isinstance(A, Nonterminal)
        # Immediate left recursion can be elminated by the following technique, which
        # works for any number of A-productions. First group the productions as
        # A -> A α_1 | A α_2 | ... A α_m | β_1 | β_2 | ... | β_n
        # where no β_i begins with an A. Then, replace the A-production by
        # A -> β_1 A' | β_2 A' | ... | β_n A'
        # A' -> α_1 A' | α_2 A' | ... | α_m A' | ε
        including_A_i_prefix = []  # productions including α
        not_including_A_i_prefix = []  # productions including β
        for production in productions:
            if production[0] == A:
                including_A_i_prefix.append(production)
            else:
                not_including_A_i_prefix.append(production)
        if len(including_A_i_prefix) == 0:
            return productions, None

        A_productions = []
        Ap_productions = []

        Ap = A.derive_from(self._suffix_gen)
        for beta in not_including_A_i_prefix:
            A_productions.append(beta + (Ap,))

        for alpha in including_A_i_prefix:
            Ap_productions.append(
                alpha[1:] +
                (Ap,))
        Ap_productions.append([Terminal(string='ε')])
        return A_productions, (Ap, Ap_productions)

    def left_factored(self):
        new_grammar = copy.copy(self)
        changed = True
        while changed:
            changed = False
            new_productions = dict()
            for A, productions in new_grammar.productions.items():
                # Find the longest prefix α common to two or more of its alternatives
                production_tuples = [tuple(x) for x in productions]
                sorted_production_tuples = sorted(production_tuples)
                longest_prefix_length = -1
                curr_range = range(2)
                longest_prefix_range = None
                while curr_range.stop <= len(sorted_production_tuples):
                    prefix = os.path.commonprefix([sorted_production_tuples[i] for i in curr_range])
                    if len(prefix) > longest_prefix_length:
                        longest_prefix_length = len(prefix)
                        longest_prefix_range = curr_range
                        curr_range = range(curr_range.start, curr_range.stop + 1)
                    else:
                        if curr_range.start < curr_range.stop - 2:
                            curr_range = range(curr_range.start + 1, curr_range.stop)
                        else:
                            curr_range = range(curr_range.start + 1, curr_range.stop + 1)

                if longest_prefix_length < 1:
                    new_productions[A] = productions
                    continue
                changed = True
                # Replace all of the A-productions A -> α β_1 | α β_2 | ... | α β_n | γ
                # where γ represents all alternatives that do not begin with α, by
                # A -> α A' | γ
                # A' -> β_1 | β_2 | ... | β_n
                Ap = A.derive_from(self._suffix_gen)
                alpha = list(production_tuples[longest_prefix_range.start][:longest_prefix_length])

                gamma = []
                for i, production in enumerate(sorted_production_tuples):
                    if i not in longest_prefix_range:
                        gamma.append(list(production))

                betas = []
                for i, production in enumerate(sorted_production_tuples):
                    if i in longest_prefix_range:
                        new_production = list(production[longest_prefix_length:])
                        if len(new_production) > 0:
                            betas.append(new_production)
                        else:
                            betas.append([Terminal(string='ε')])
                            new_grammar.terminals.add(Terminal(string='ε'))

                new_productions[A] = [alpha + [Ap]]
                new_productions[A].extend(gamma)
                new_productions[Ap] = betas
                new_grammar.nonterminals.add(Ap)
                new_grammar.productions = new_productions
        new_grammar.simplify()
        return new_grammar

    def first(self, symbol_string):
        if self._first_cache == None:
            self.compute_all_first()

        if isinstance(symbol_string, Terminal) or isinstance(symbol_string, Nonterminal):
            return self._first_cache[symbol_string]

        if symbol_string in self._first_cache:
            return self._first_cache[tuple(symbol_string)]

        first = set()

        for X_i in symbol_string:
            first.update(self._first_cache[X_i].difference({Terminal._epsilon}))
            if Terminal._epsilon not in self._first_cache[X_i]:
                # ε not in X_i so X_i+1 can't contribute to FIRST(symbol_string)
                break
        else:
            # We made it here which means ε was in all X_i
            first.add(Terminal._epsilon)

        self._first_cache[tuple(symbol_string)] = first
        return first

    def compute_all_first(self):
        self._first_cache = dict()

        # If X is a terminal, then FIRST(X) = {X}.
        for terminal in self.terminals:
            self._first_cache[terminal] = {terminal}

        # If X -> ε is a production, then add ε to FIRST(X).
        for nonterminal in self.nonterminals:
            for productions in self.productions[nonterminal]:
                if len(productions) == 1 and productions[0] == Terminal._epsilon:
                    self._first_cache[nonterminal] = {Terminal._epsilon}
                    break
            else:
                self._first_cache[nonterminal] = set()

        changed = True
        while changed:
            changed = False
            for X in self.nonterminals:
                for productions in self.productions[X]:
                    for Y_i in productions:
                        before = len(self._first_cache[X])
                        self._first_cache[X].update(self._first_cache[Y_i].difference({Terminal._epsilon}))
                        if len(self._first_cache[X]) != before:
                            changed = True

                        if Terminal._epsilon not in self._first_cache[Y_i]:
                            # ε not in Y_i so Y_i+1 can't contribute to FIRST(X)
                            break
                    else:
                        # We made it here which means ε was in all Y_i
                        if Terminal._epsilon not in self._first_cache[X]:
                            self._first_cache[X].add(Terminal._epsilon)
                            change = True

    def follow(self, X):
        assert isinstance(X, Nonterminal)
        if self._follow_cache == None:
            self.compute_all_follow()

        return self._follow_cache[X]

    def compute_all_follow(self):
        self._follow_cache = dict()
        for A in self.nonterminals:
            self._follow_cache[A] = set()
        self._follow_cache[self.start_symbol].add(Terminal(string='$'))


        changed = True
        while changed:
            changed = False
            for A in self.nonterminals:
                # If there is a production A -> α B β, then everything in FIRST(β) except ε
                # is in FOLLOW(B)
                for production in self.productions[A]:
                    for i in range(len(production)):
                        B = production[i]
                        if isinstance(B, Terminal):
                            continue
                        # alpha = production[:i] # not actually used
                        beta = production[(i+1):]
                        before = len(self._follow_cache[B])
                        self._follow_cache[B].update(self.first(beta).difference({Terminal._epsilon}))
                        if len(self._follow_cache[B]) != before:
                            changed = True

                # If there is a production A -> α B, or a production A -> α B β, where
                # FIRST(β) contains ε, then everything in FOLLOW(A) is in FOLLOW(B)
                for production in self.productions[A]:
                    for i in range(len(production)):
                        B = production[i]
                        if isinstance(B, Terminal):
                            continue
                        # alpha = production[:i] # not actually used
                        beta = production[(i+1):]
                        if Terminal._epsilon in self.first(beta):
                            before = len(self._follow_cache[B])
                            self._follow_cache[B].update(self._follow_cache[A])
                            if len(self._follow_cache[B]) != before:
                                changed = True

    def closure(self, I):
        if frozenset(I) in self._closure_cache:
            return self._closure_cache[frozenset(I)]

        assert isinstance(I, set)
        if len(I) == 0:
            self._closure_cache[frozenset(I)] = I
            return I

        # Initially, add every item in I to CLOSURE(I)
        closure = copy.copy(I)
        last_len = None

        # If A -> α . B β is in CLOSURE(I) and B -> γ is a production, then add the
        # item B -> . γ to CLOSURE(I), if it is not already there. Apply this rule
        # until no more new items can be added to CLOSURE(I).
        while last_len != len(closure):
            last_len = len(closure)

            for item in copy.copy(closure):
                assert isinstance(item, LR0Item)
                A = item.A
                production = item.production
                if item.dot_position >= len(production):
                    # This means the dot is to the right of the final symbol
                    continue

                alpha = production[:item.dot_position]
                B = production[item.dot_position]
                beta = production[(item.dot_position + 1):]
                if isinstance(B, Nonterminal):
                    for gamma in self.productions[B]:
                        closure.add(
                            LR0Item(
                            A=B,
                            production=gamma,
                            dot_position=0))

        self._closure_cache[frozenset(I)] = closure
        return closure

    def goto(self, I, X):
        # Returns the closure of the set of all items [A -> α X . β] such that [A -> α . X β] is in I.

        if (frozenset(I), X) in self._goto_cache:
            return self._goto_cache[(frozenset(I), X)]

        goto = set()
        last_len = None

        while last_len != len(goto):
            last_len = len(goto)

            for item in I:
                assert isinstance(item, LR0Item)
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
                        LR0Item(
                        A=A,
                        production=item.production,
                        dot_position=item.dot_position + 1))

        retval = self.closure(goto)
        self._goto_cache[(frozenset(I), X)] = retval
        return retval

    def items(self):
        if self._items_cache is not None:
            return self._items_cache

        self._items_cache = dict()

        self.augment()

        C = {frozenset(self.closure(
            {
                LR0Item(
                    A=self.start_symbol,
                    production=(self._prev_start_symbol, ),
                    dot_position=0)}))}


        last_len = None

        while last_len != len(C):
            last_len = len(C)

            for I in copy.copy(C):
                assert isinstance(I, frozenset)
                for X in self.terminals.union(self.nonterminals):
                    goto = self.goto(I, X)
                    if len(goto) > 0:
                        C.add(frozenset(goto))

        self._items_cache = C
        return C

    def augment(self):
        if self._prev_start_symbol is not None:
            return
        old_start = self.start_symbol
        new_start = old_start.derive_from(self._suffix_gen)
        assert isinstance(old_start, Nonterminal)
        self.productions[new_start] = [(old_start, )]
        self.nonterminals.add(new_start)
        self._is_augmented = True
        self._prev_start_symbol = old_start
        self.start_symbol = new_start


class LR1Grammar(Grammar):
    def closure(self, I):
        if frozenset(I) in self._closure_cache:
            return self._closure_cache[frozenset(I)]

        self.augment()

        assert isinstance(I, set)
        if len(I) == 0:
            self._closure_cache[frozenset(I)] = I
            return I

        # Initially, add every item in I to CLOSURE(I)
        closure = copy.copy(I)
        last_len = None

        # If A -> α . B β is in CLOSURE(I) and B -> γ is a production, then add the
        # item B -> . γ to CLOSURE(I), if it is not already there. Apply this rule
        # until no more new items can be added to CLOSURE(I).
        while last_len != len(closure):
            last_len = len(closure)

            for item in copy.copy(closure):
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

        self._closure_cache[frozenset(I)] = closure
        return closure

    def goto(self, I, X):
        # Returns the closure of the set of all items [A -> α X . β] such that [A -> α . X β] is in I.

        if (frozenset(I), X) in self._goto_cache:
            return self._goto_cache[(frozenset(I), X)]

        self.augment()

        goto = set()
        last_len = None

        while last_len != len(goto):
            last_len = len(goto)

            for item in I:
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
        self._goto_cache[(frozenset(I), X)] = retval
        return retval

    def items(self):
        if self._items_cache is not None:
            return self._items_cache

        self._items_cache = dict()

        self.augment()

        C = {frozenset(self.closure(
            {
                LR1Item(
                    A=self.start_symbol,
                    production=(self._prev_start_symbol, ),
                    dot_position=0,
                    lookahead=Terminal._end)}))}


        last_len = None

        while last_len != len(C):
            last_len = len(C)

            for I in copy.copy(C):
                assert isinstance(I, frozenset)
                for X in self.terminals.union(self.nonterminals):
                    goto = self.goto(I, X)
                    if len(goto) > 0:
                        C.add(frozenset(goto))

        self._items_cache = C
        return C

    def compute_all_first(self):
        super().compute_all_first()
        self._first_cache[Terminal._end] = {Terminal._end}


class TextbookGrammar(Grammar):
    _grammar_dict = dict()
    _grammar_str_dict = dict()

    def __init__(self, name):
        if len(self._grammar_dict) == 0:
            self._init_grammar_dict()
        self.name = name
        if name not in self._grammar_dict:
            raise Exception('Unknown textbook grammar')
        self.string_version = self._grammar_dict[name]
        grammar_copy = copy.copy(self.string_version)
        super().__init__(
            grammar_copy.terminals,
            grammar_copy.nonterminals,
            grammar_copy.productions,
            grammar_copy.start_symbol)

    @classmethod
    def string_version(cls, name):
        if len(cls._grammar_dict) == 0:
            cls._init_grammar_dict()
        if string_version := cls._grammar_str_dict.get(name):
            return string_version
        else:
            raise Exception('String version not available.')

    @classmethod
    def _init_grammar_str_dict(cls):
        cls._grammar_str_dict['4.18'] = \
            """
            S -> A 'a' | 'b'
            A -> A 'c' | S 'd' | 'ε'
            """
        cls._grammar_str_dict['4.3.4'] = \
            """
            stmt -> 'if' expr 'then' stmt 'else' stmt
                |  'if' expr 'then' stmt
            """
        cls._grammar_str_dict['4.22'] = \
            """
            S -> 'i' E 't' S Sp | 'a'
            Sp -> 'e' S | 'ε'
            E -> 'b'
            """
        cls._grammar_str_dict['4.23'] = \
            """
            S -> 'i' E 't' S | 'i' E 't' S 'e' S | 'a'
            E -> 'b'
            """
        cls._grammar_str_dict['4.28'] = \
            """
            E -> T Ep
            Ep -> '+' T Ep | 'ε'
            T -> F Tp
            Tp -> '*' F Tp | 'ε'
            F -> '(' E ')' | 'id'
            """
        cls._grammar_str_dict['4.29'] = \
            """
            S -> 'c' A 'd'
            A -> 'a' 'b' | 'a'
            """
        cls._grammar_str_dict['4.4.3'] = \
            """
            stmt -> 'if' '(' expr ')' stmt 'else' stmt
                | 'while' '(' expr ')' stmt
                | '{' stmt_list '}'
            expr -> 'expr'
            stmt_list -> stmt stmt_list | 'ε'
            """
        cls._grammar_str_dict['4.23_verbose'] = \
            """
            S -> 'if' '(' E ')' '{' S '}' ELSE_CLAUSE | 'id'
            ELSE_CLAUSE -> 'else' '{' S '}' | 'ε'
            E -> 'id'
            """
        cls._grammar_str_dict['4.40'] = \
            """
            Ep -> E
            E -> E '+' T | T
            T -> T '*' F | F
            F -> '(' E ')' | 'id'
            """
        cls._grammar_str_dict['4.40_2'] = \
            """
            E -> E '+' T | T
            T -> T '*' F | F
            F -> '(' E ')' | 'id'
            """
        cls._grammar_str_dict['4.55'] = \
            """
            S -> C C
            C -> 'id' C | 'num'
            """
        cls._grammar_str_dict['ANSI C'] = \
            """
            start ->
                translation_unit
                
            primary_expression ->
                  'id'
                | 'num'
                | 'str'
                | '(' expression ')'
            
            postfix_expression ->
                  primary_expression
                | postfix_expression '[' expression ']'
                | postfix_expression '(' ')'
                | postfix_expression '(' argument_expression_list ')'
                | postfix_expression '.' 'id'
                | postfix_expression '*' 'id'
                | postfix_expression '++'
                | postfix_expression '--'
            
            argument_expression_list ->
                  assignment_expression
                | argument_expression_list ',' assignment_expression
            
            unary_expression ->
                  postfix_expression
                | '++' unary_expression
                | '--' unary_expression
                | unary_operator cast_expression
                | 'sizeof' unary_expression
                | 'sizeof' '(' type_name ')'
            
            unary_operator ->
                  '&'
                | '*'
                | '+'
                | '-'
                | '~'
                | '!'
            
            cast_expression ->
                  unary_expression
                | '(' type_name ')' cast_expression
            
            multiplicative_expression ->
                  cast_expression
                | multiplicative_expression '*' cast_expression
                | multiplicative_expression '/' cast_expression
                | multiplicative_expression '%' cast_expression
            
            additive_expression ->
                  multiplicative_expression
                | additive_expression '+' multiplicative_expression
                | additive_expression '-' multiplicative_expression
            
            shift_expression ->
                  additive_expression
                | shift_expression '<<' additive_expression
                | shift_expression '>>' additive_expression
            
            relational_expression ->
                  shift_expression
                | relational_expression '<' shift_expression
                | relational_expression '>' shift_expression
                | relational_expression '<=' shift_expression
                | relational_expression '>=' shift_expression
            
            equality_expression ->
                  relational_expression
                | equality_expression '==' relational_expression
                | equality_expression '!=' relational_expression
            
            and_expression ->
                  equality_expression
                | and_expression '&' equality_expression
            
            exclusive_or_expression ->
                  and_expression
                | exclusive_or_expression '^' and_expression
            
            inclusive_or_expression ->
                  exclusive_or_expression
                | inclusive_or_expression '|' exclusive_or_expression
            
            logical_and_expression ->
                  inclusive_or_expression
                | logical_and_expression '&&' inclusive_or_expression
            
            logical_or_expression ->
                  logical_and_expression
                | logical_or_expression '||' logical_and_expression
            
            conditional_expression ->
                  logical_or_expression
                | logical_or_expression '?' expression ':' conditional_expression
            
            assignment_expression ->
                  conditional_expression
                | unary_expression assignment_operator assignment_expression
            
            assignment_operator ->
                  '='
                | '*='
                | '\='
                | '%='
                | '+='
                | '-='
                | '<<='
                | '>>='
                | '&='
                | '^='
                | '|='
            
            expression ->
                  assignment_expression
                | expression ',' assignment_expression
            
            constant_expression ->
                  conditional_expression
            
            declaration ->
                  declaration_specifiers ';'
                | declaration_specifiers init_declarator_list ';'
            
            declaration_specifiers ->
                  storage_class_specifier
                | storage_class_specifier declaration_specifiers
                | type_specifier
                | type_specifier declaration_specifiers
                | type_qualifier
                | type_qualifier declaration_specifiers
            
            init_declarator_list ->
                  init_declarator
                | init_declarator_list ',' init_declarator
            
            init_declarator ->
                  declarator
                | declarator '=' initializer
            
            storage_class_specifier ->
                  'typedef'
                | 'extern'
                | 'static'
                | 'auto'
                | 'register'
            
            type_specifier ->
                  'void'
                | 'char'
                | 'short'
                | 'int'
                | 'long'
                | 'float'
                | 'double'
                | 'signed'
                | 'unsigned'
                | struct_or_union_specifier
                | enum_specifier
                | 'id'
            
            struct_or_union_specifier ->
                  struct_or_union 'id' '{' struct_declaration_list '}'
                | struct_or_union '{' struct_declaration_list '}'
                | struct_or_union 'id'
            
            struct_or_union ->
                  'struct'
                | 'union'
            
            struct_declaration_list ->
                  struct_declaration
                | struct_declaration_list struct_declaration
            
            struct_declaration ->
                  specifier_qualifier_list struct_declarator_list ';'
            
            specifier_qualifier_list ->
                  type_specifier specifier_qualifier_list
                | type_specifier
                | type_qualifier specifier_qualifier_list
                | type_qualifier
            
            struct_declarator_list ->
                  struct_declarator
                | struct_declarator_list ',' struct_declarator
            
            struct_declarator ->
                  declarator
                | ':' constant_expression
                | declarator ':' constant_expression
            
            enum_specifier ->
                  'enum' '{' enumerator_list '}'
                | 'enum' 'id' '{' enumerator_list '}'
                | 'enum' 'id'
            
            enumerator_list ->
                  enumerator
                | enumerator_list ',' enumerator
            
            enumerator ->
                  'id'
                | 'id' '=' constant_expression
            
            type_qualifier ->
                  'const'
                | 'volatile'
            
            declarator ->
                  pointer direct_declarator
                | direct_declarator
            
            direct_declarator ->
                  'id'
                | '(' declarator ')'
                | direct_declarator '[' constant_expression ']'
                | direct_declarator '[' ']'
                | direct_declarator '(' parameter_type_list ')'
                | direct_declarator '(' identifier_list ')'
                | direct_declarator '(' ')'
            
            pointer ->
                  '*'
                | '*' type_qualifier_list
                | '*' pointer
                | '*' type_qualifier_list pointer
            
            type_qualifier_list ->
                  type_qualifier
                | type_qualifier_list type_qualifier
            
            
            parameter_type_list ->
                  parameter_list
                | parameter_list ',' 'ellipsis'
            
            parameter_list ->
                  parameter_declaration
                | parameter_list ',' parameter_declaration
            
            parameter_declaration ->
                  declaration_specifiers declarator
                | declaration_specifiers abstract_declarator
                | declaration_specifiers
            
            identifier_list ->
                  'id'
                | identifier_list ',' 'id'
            
            type_name ->
                  specifier_qualifier_list
                | specifier_qualifier_list abstract_declarator
            
            abstract_declarator ->
                  pointer
                | direct_abstract_declarator
                | pointer direct_abstract_declarator
            
            direct_abstract_declarator ->
                  '(' abstract_declarator ')'
                | '[' ']'
                | '[' constant_expression ']'
                | direct_abstract_declarator '[' ']'
                | direct_abstract_declarator '[' constant_expression ']'
                | '(' ')'
                | '(' parameter_type_list ')'
                | direct_abstract_declarator '(' ')'
                | direct_abstract_declarator '(' parameter_type_list ')'
            
            initializer ->
                  assignment_expression
                | '{' initializer_list '}'
                | '{' initializer_list ',' '}'
            
            initializer_list ->
                  initializer
                | initializer_list ',' initializer
            
            statement ->
                  labeled_statement
                | compound_statement
                | expression_statement
                | selection_statement
                | iteration_statement
                | jump_statement
            
            labeled_statement ->
                  'id' ':' statement
                | 'case' constant_expression ':' statement
                | 'default' ':' statement
            
            compound_statement ->
                  '{' '}'
                | '{' statement_list '}'
                | '{' declaration_list '}'
                | '{' declaration_list statement_list '}'
            
            declaration_list ->
                  declaration
                | declaration_list declaration
            
            statement_list ->
                  statement
                | statement_list statement
            
            expression_statement ->
                  ';'
                | expression ';'
            
            selection_statement ->
                  'if' '(' expression ')' statement
                | 'if' '(' expression ')' statement 'else' statement
                | 'switch' '(' expression ')' statement
            
            iteration_statement ->
                  'while' '(' expression ')' statement
                | 'do' statement 'while' '(' expression ')' ';'
                | 'for' '(' expression_statement expression_statement ')' statement
                | 'for' '(' expression_statement expression_statement expression ')' statement
            
            jump_statement ->
                  'goto' 'id' ';'
                | 'continue' ';'
                | 'break' ';'
                | 'return' ';'
                | 'return' expression ';'
            
            translation_unit ->
                  external_declaration
                | translation_unit external_declaration
            
            external_declaration ->
                  function_definition
                | declaration
            
            function_definition ->
                  declaration_specifiers declarator declaration_list compound_statement
                | declaration_specifiers declarator compound_statement
                | declarator declaration_list compound_statement
                | declarator compound_statement
            """


    @classmethod
    def _init_grammar_dict(cls):
        cls._init_grammar_str_dict()
        for name in cls._grammar_str_dict.keys():
            cls._grammar_dict[name] = Grammar.from_string(cls._grammar_str_dict[name])

        cls._grammar_dict['4.20'] = cls._grammar_dict['4.18'].without_left_recursion()
        cls._grammar_dict['4.24'] = cls._grammar_dict['4.23'].left_factored()
        cls._grammar_dict['ANSI C refactored'] = cls._grammar_dict['ANSI C']
        # cls._grammar_dict['ANSI C refactored'].start_symbol = Nonterminal('translation_unit')
        cls._grammar_dict['ANSI C refactored'] = cls._grammar_dict['ANSI C refactored'].without_left_recursion()
        cls._grammar_dict['ANSI C refactored2'] = cls._grammar_dict['ANSI C refactored'].left_factored()


def do_stuff():
    g = TextbookGrammar('ANSI C refactored2')
    print(g)

if __name__ == '__main__':
    do_stuff()