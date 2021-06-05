import copy
import re
import os

import Tokens


class GrammarSymbol:
    def __init__(self, string):
        self.string = string

    def __hash__(self):
        return hash(self.string)

    def __eq__(self, other):
        if not isinstance(other, GrammarSymbol):
            return False
        return hash(self) == hash(other)

    def __str__(self):
        return self.string

    __repr__ = __str__

    def __lt__(self, other):
        return self.string < other.string


class Terminal(GrammarSymbol):
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
        else:
            raise Exception('Not a valid terminal')
        super().__init__(self.string)


class ActionTerminal(Terminal):
    def __init__(self, action_name, action):
        super().__init__(action_name, Tokens.ActionToken(action_name, action))


class Nonterminal(GrammarSymbol):
    def derive_from(self, suffix_gen):
        return Nonterminal(f'{self.string}_{str(next(suffix_gen))}')


class Grammar:
    def __init__(self, terminals, nonterminals, productions, start_symbol):
        self.terminals = terminals  # A set of terminals
        self.nonterminals = nonterminals  # A set of nonterminals
        self.productions = productions  # A dictionary of nonterminals to lists of terminals/nonterminals
        self.start_symbol = start_symbol  # The starting point for all derivations from this grammar
        self.verify()
        self._first_cache = dict()
        self._follow_cache = dict()
        self._suffix_gen = self._suffix_gen_func()

    def __str__(self):
        return '------------------------\n' \
               f'terminals: {self.terminals}\n' \
               f'nonterminals: {self.nonterminals}\n' \
               f'productions: {self.productions}\n' \
               f'start_symbol: {self.start_symbol}'

    __repr__ = __str__

    def _suffix_gen_func(self):
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
                    new_productions.append([Terminal(string='ε')])
                else:
                    new_productions.append(new_production)
            self.productions[A] = new_productions

    def verify(self):
        assert isinstance(self.terminals, set)
        assert isinstance(self.nonterminals, set)
        assert isinstance(self.productions, dict)
        for nonterminal, production_list in self.productions.items():
            assert isinstance(nonterminal, Nonterminal)
            for production in production_list:
                assert isinstance(production, list)
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
        return Grammar(
            terminals=new_terminals,
            nonterminals=new_nonterminals,
            productions=new_productions,
            start_symbol=new_start_symbol)

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
            if m := re.match(r'^(\w+) -> (.*)$', rest_of_line):
                # This is a definition of a nonterminal, let's figure out its name
                current_nonterminal = Nonterminal(m.group(1))
                rest_of_line = m.group(2).strip()
                if start_symbol is None:
                    start_symbol = current_nonterminal
            elif m := re.match(r'^\|(.*)$', rest_of_line):
                # we are on a new line doing a shorthand production
                rest_of_line = m.group(1).strip()

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
                    productions.setdefault(current_nonterminal, []).append(current_rule)
                    current_rule = []
                    rest_of_line = m.group(1).strip()
                else:
                    raise Exception('Expected a nonterminal, terminal or | before "' + rest_of_line + '"')

            productions.setdefault(current_nonterminal, []).append(current_rule)
        nonterminals = set(productions.keys())
        all_rhs_symbols = set([symbol
                               for productions_for_rule in productions.values()
                               for production in productions_for_rule
                               for symbol in production])
        terminals = all_rhs_symbols.difference(nonterminals)
        return Grammar(terminals, nonterminals, productions, start_symbol)

    def without_left_recursion(self):
        new_grammar = copy.copy(self)
        A = list(new_grammar.nonterminals)
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

                # eliminate the immediate left recursion among the A_i-productions
                A_i_productions, A_ip_and_productions = self.without_immediate_left_recursion(
                    A=A[i],
                    productions=replaced_productions)

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
        # A -> A alpha_1 | A alpha_2 | ... A alpha_m | beta_1 | beta_2 | ... | beta_n
        # where no beta_i begins with an A. Then, replace the A-production by
        # A -> beta_1 A' | beta_2 A' | ... | beta_n A'
        # A' -> alpha_1 A' | alpha_2 A' | ... | alpha_m A' | ε
        including_A_i_prefix = []  # productions including alpha
        not_including_A_i_prefix = []  # productions including beta
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
            A_productions.append(beta + [Ap])

        for alpha in including_A_i_prefix:
            Ap_productions.append(
                alpha[1:] +
                [Ap])
        Ap_productions.append([Terminal(string='ε')])
        return A_productions, (Ap, Ap_productions)

    def left_factored(self):
        new_grammar = copy.copy(self)
        new_productions = dict()
        for A, productions in new_grammar.productions.items():
            # Find the longest prefix alpha common to two or more of its alternatives
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

            # Replace all of the A-productions A -> alpha beta_1 | alpha beta_2 | ... | alpha beta_n | gamma
            # where gamma represents all alternatives that do not begin with alpha, by
            # A -> alpha A' | gamma
            # A' -> beta_1 | beta_2 | ... | beta_n
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

    def _first_symbol(self, X):
        # If we already cached this then return right away
        if X in self._first_cache:
            return self._first_cache[X]

        assert X in self.terminals or X in self.nonterminals

        if isinstance(X, Terminal):
            self._first_cache[X] = {X}
            return self._first_cache[X]

        first_set = set()
        epsilon = Terminal(string='ε')
        for production in self.productions[X]:
            if len(production) >= 1:
                for Y_i in production:
                    first_set.update(self._first_symbol(Y_i))
                    if epsilon not in self._first_symbol(Y_i):
                        break
                else:
                    if epsilon in production[-1]:
                        first_set.add(epsilon)
            else:
                raise Exception('Tried processing an empty production. Was this supposed to be ε?')

        return first_set

    def first(self, string):
        if isinstance(string, Terminal) or isinstance(string, Nonterminal):
            return self._first_symbol(string)
        for X in string:
            assert isinstance(X, Terminal) or isinstance(X, Nonterminal)

        first_set = set()
        epsilon = Terminal(string='ε')

        for i, X_i in string:
            first_set.update(self._first_symbol(X_i).difference({epsilon}))
            if epsilon not in self._first_symbol(X_i):
                break
        else:
            if epsilon in string[-1]:
                first_set.add(epsilon)

        return first_set


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

    @classmethod
    def _init_grammar_dict(cls):
        cls._init_grammar_str_dict()
        for name in cls._grammar_str_dict.keys():
            cls._grammar_dict[name] = Grammar.from_string(cls._grammar_str_dict[name])

        cls._grammar_dict['4.20'] = cls._grammar_dict['4.18'].without_left_recursion()
        cls._grammar_dict['4.24'] = cls._grammar_dict['4.23'].left_factored()


if __name__ == '__main__':
    print(TextbookGrammar('4.29')._first_symbol(Terminal(string='c')))
    print(TextbookGrammar('4.20')._first_symbol(Terminal(string='c')))
