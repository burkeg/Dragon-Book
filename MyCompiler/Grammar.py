class Terminal:
    def __init__(self, string):
        self.string = string

class Nonterminal:
    def __init__(self, name):
        self.name = name

class Grammar:
    def __init__(self, terminals, nonterminals, productions, start_symbol):
        self.terminals = terminals          # A list of terminals
        self.nonterminals = nonterminals    # A list of nonterminals
        self.productions = productions      # A dictionary of nonterminals to lists of terminals/nonterminals
        self.start_symbol = start_symbol    # The starting point for all derivations from this grammar

    def from_string(self, grammar_as_string):
        pass
