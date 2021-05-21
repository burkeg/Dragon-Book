from Automata import Element, Alphabet
from RegExpr import RegularDefinition, RegExpr
from SymbolTable import SymbolTable
from inspect import signature

from Tokens.Tag import Tag
from Tokens.Token import Token


class LexicalAnalyzer:
    def __init__(self, symbol_table, regular_definition, translation_rules):
        # symbol_table is an instance of the SymbolTable class
        # regular_definition is an instance of the RegularDefinition class
        # translation_rules is a list of 2-tuples with the following format:
        #   pattern: Any Element d_i from the regular_definition or list of Element
        #       where no element is any d_i.
        #   action: A function with 2 arguments:
        #           symbol_table, A reference to the symbol_table
        #           text, text corresponding with the current lexeme
        #       Any side effects should be written to the Symbol table.
        #       You can also optionally return a token.

        self.symbol_table = symbol_table
        self.regular_definition = regular_definition
        self.translation_rules = translation_rules
        assert isinstance(self.symbol_table, SymbolTable)
        assert isinstance(self.regular_definition, RegularDefinition)
        assert isinstance(self.translation_rules, list)
        self._verify()

    def _verify(self):
        for translation_rule in self.translation_rules:
            assert isinstance(translation_rule, tuple)
            assert len(translation_rule) == 2
            pattern = translation_rule[0]
            action = translation_rule[1]
            if isinstance(pattern, Element):
                # Any Element d_i from the regular_definition
                assert pattern.value in self.regular_definition.regular_expressions
            elif isinstance(pattern, list):
                for element in pattern:
                    assert isinstance(element, Element)
                    # List of Element where no element is any d_i.
                    assert element.value not in self.regular_definition.regular_expressions
            else:
                raise Exception('Translation Rule must have a list or Element as the translation trigger')

            assert len(signature(action).parameters) == 2



def do_stuff():
    # A -> a*b
    # B -> b a A
    A = RegExpr.from_string('a*b')
    before_add_B = RegExpr.from_string('ba')
    B = RegExpr(before_add_B.expression + [Element(A)], Alphabet(before_add_B.alphabet.elements + [Element(A)]))
    reg_def = RegularDefinition([A, B])
    print(reg_def)
    symbol_table = SymbolTable()

    def B_action(symbol_table, text):
        token
        return Token(Tag.ID)

    translation_rules = [(Element(B), B_action)]
    lexer = LexicalAnalyzer(symbol_table, reg_def, translation_rules)
    print(lexer)


if __name__ == '__main__':
    do_stuff()