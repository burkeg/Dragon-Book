import copy
import re
import os
from Tokens import EmptyToken
from Nonterminal import Nonterminal
from Terminal import Terminal, epsilon_terminal
from ActionTerminal import ActionTerminal
from LRItemGroup import LRItemGroup
from LR0Item import LR0Item


class BaseGrammar:
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
                            isinstance(term.token, EmptyToken):
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
        return BaseGrammar(terminals, nonterminals, productions, start_symbol)

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
            first.update(self._first_cache[X_i].difference({epsilon_terminal}))
            if epsilon_terminal not in self._first_cache[X_i]:
                # ε not in X_i so X_i+1 can't contribute to FIRST(symbol_string)
                break
        else:
            # We made it here which means ε was in all X_i
            first.add(epsilon_terminal)

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
                if len(productions) == 1 and productions[0] == epsilon_terminal:
                    self._first_cache[nonterminal] = {epsilon_terminal}
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
                        self._first_cache[X].update(self._first_cache[Y_i].difference({epsilon_terminal}))
                        if len(self._first_cache[X]) != before:
                            changed = True

                        if epsilon_terminal not in self._first_cache[Y_i]:
                            # ε not in Y_i so Y_i+1 can't contribute to FIRST(X)
                            break
                    else:
                        # We made it here which means ε was in all Y_i
                        if epsilon_terminal not in self._first_cache[X]:
                            self._first_cache[X].add(epsilon_terminal)
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
                        self._follow_cache[B].update(self.first(beta).difference({epsilon_terminal}))
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
                        if epsilon_terminal in self.first(beta):
                            before = len(self._follow_cache[B])
                            self._follow_cache[B].update(self._follow_cache[A])
                            if len(self._follow_cache[B]) != before:
                                changed = True

    def closure(self, I):
        assert isinstance(I, LRItemGroup)
        if I in self._closure_cache:
            return self._closure_cache[I]

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

        self._closure_cache[I] = closure
        return closure

    def goto(self, I, X):
        # Returns the closure of the set of all items [A -> α X . β] such that [A -> α . X β] is in I.
        assert isinstance(I, LRItemGroup)
        if (I, X) in self._goto_cache:
            return self._goto_cache[(I, X)]

        goto = LRItemGroup(set())
        last_len = None

        while last_len != len(goto):
            last_len = len(goto)

            for item in I.get_items():
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
        self._goto_cache[(I, X)] = retval
        return retval

    def items(self):
        if self._items_cache is not None:
            return self._items_cache

        self._items_cache = dict()

        self.augment()

        C = {self.closure(LRItemGroup({LR0Item(
            A=self.start_symbol,
            production=(self._prev_start_symbol, ),
            dot_position=0)}))}


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
