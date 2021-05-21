import re

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
    pass


class Nonterminal(GrammarSymbol):
    pass

class Grammar:
    def __init__(self, terminals, nonterminals, productions, start_symbol):
        self.terminals = terminals          # A list of terminals
        self.nonterminals = nonterminals    # A list of nonterminals
        self.productions = productions      # A dictionary of nonterminals to lists of terminals/nonterminals
        self.start_symbol = start_symbol    # The starting point for all derivations from this grammar

    @staticmethod
    def from_string(grammar_as_string):
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
                elif m := re.match(r'^\"([^\"]+?)\"(.*)$', rest_of_line):
                    # Found terminal
                    current_rule.append(Terminal(m.group(1)))
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


if __name__ == '__main__':
    with open('Grammars/grammar4.1_augmented.txt', 'r') as file:
        g = Grammar.from_string(file.read())
    print('terminals: ', g.terminals)
    print('nonterminals: ', g.nonterminals)
    print('productions: ', g.productions)
    print('start_symbol: ', g.start_symbol)
