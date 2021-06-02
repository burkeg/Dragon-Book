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
    pass

class Grammar:
    def __init__(self, terminals, nonterminals, productions, start_symbol):
        self.terminals = terminals          # A set of terminals
        self.nonterminals = nonterminals    # A set of nonterminals
        self.productions = productions      # A dictionary of nonterminals to lists of terminals/nonterminals
        self.start_symbol = start_symbol    # The starting point for all derivations from this grammar
        self.verify()

    def verify(self):
        assert isinstance(self.terminals, set)
        assert isinstance(self.terminals, set)
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
                if new_grammar.nonterminals[A[i]][0] == A[j]:
                    print(A[j])




if __name__ == '__main__':
    g = Grammar.from_string(
        """
        A -> A 'c' | A 'a' 'd' | 'b' 'd' | \u03B5
        """
    )
    print(g)
    print('terminals: ', g.terminals)
    print('nonterminals: ', g.nonterminals)
    print('productions: ', g.productions)
    print('start_symbol: ', g.start_symbol)
    g2 = g.without_left_recursion()
