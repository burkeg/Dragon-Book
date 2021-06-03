import copy
import re

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
            if type(self.token) == Tokens.Token:
                self.string = f"'{self.token.lexeme}'"
            else:
                self.string = string
        else:
            raise Exception('Not a valid terminal')
        super().__init__(self.string)


class ActionTerminal(Terminal):
    def __init__(self, action_name, action):
        super().__init__(action_name, Tokens.ActionToken(action_name, action))


class Nonterminal(GrammarSymbol):
    def derive_from(self):
        return GrammarSymbol(self.string + "'")


class Grammar:
    def __init__(self, terminals, nonterminals, productions, start_symbol):
        self.terminals = terminals          # A set of terminals
        self.nonterminals = nonterminals    # A set of nonterminals
        self.productions = productions      # A dictionary of nonterminals to lists of terminals/nonterminals
        self.start_symbol = start_symbol    # The starting point for all derivations from this grammar
        self.verify()

    def __str__(self):
        return '------------------------\n'\
               f'terminals: {self.terminals}\n'\
               f'nonterminals: {self.nonterminals}\n'\
               f'productions: {self.productions}\n'\
               f'start_symbol: {self.start_symbol}'
    __repr__ = __str__

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
                A_i_productions, A_ip_and_productions = self.remove_immediate_left_recursion(
                    A=A[i],
                    productions=replaced_productions)

                new_grammar.productions[A[i]] = A_i_productions
                if A_ip_and_productions:
                    A_ip, A_ip_productions = A_ip_and_productions
                    new_grammar.productions[A_ip] = A_ip_productions
                    new_grammar.nonterminals.add(A_ip)
                    new_grammar.terminals.add(Terminal(string='ε'))
        return new_grammar


    @staticmethod
    def remove_immediate_left_recursion(A, productions):
        assert isinstance(A, Nonterminal)
        # Immediate left recursion can be elminated by the following technique, which
        # works for any number of A-productions. First group the productions as
        # A -> A alpha_1 | A alpha_2 | ... A alpha_m | beta_1 | beta_2 | ... | beta_n
        # where no beta_i begins with an A. Then, replace the A-production by
        # A -> beta_1 A' | beta_2 A' | ... | beta_n A'
        # A' -> alpha_1 A' | alpha_2 A' | ... | alpha_m A' | ε
        including_A_i_prefix = [] # productions including alpha
        not_including_A_i_prefix = [] # productions including beta
        for production in productions:
            if production[0] == A:
                including_A_i_prefix.append(production)
            else:
                not_including_A_i_prefix.append(production)
        if len(including_A_i_prefix) == 0:
            return productions, None

        A_productions = []
        Ap_productions = []

        Ap = A.derive_from()
        for beta in not_including_A_i_prefix:
            A_productions.append(beta + [Ap])

        for alpha in including_A_i_prefix:
            Ap_productions.append(
                alpha[1:] +
                [Ap])
        Ap_productions.append([Terminal(string='ε')])
        return A_productions, (Ap, Ap_productions)


if __name__ == '__main__':
    g = Grammar.from_string(
        """
        S -> A 'a' | 'b'
        A -> A 'c' | S 'd' | 'ε'
        """
    )
    print(g)
    g2 = g.without_left_recursion()
    print(g2)
    g2.simplify()
    print(g2)
