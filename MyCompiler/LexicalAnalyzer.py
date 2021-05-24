import Automata
import Enums
import RegExpr
import SymbolTable
from inspect import signature
import Tokens.Token
from collections import Iterable


class LexicalAnalyzer:
    def __init__(self, symbol_table_manager, regular_definition, translation_rules):
        # symbol_table is an instance of the SymbolTableManager class
        # regular_definition is an instance of the RegularDefinition class
        # translation_rules is a list of 2-tuples with the following format:
        #   pattern: Any Element d_i from the regular_definition or list of Element
        #       where no element is any d_i.
        #   action: A function with 2 arguments:
        #           symbol_table, A reference to the symbol_table
        #           text, text corresponding with the current lexeme
        #       Any side effects should be written to the Symbol table.
        #       You can also optionally return a token.

        self.symbol_table_manager = symbol_table_manager
        self.regular_definition = regular_definition
        self.translation_rules = translation_rules
        assert isinstance(self.symbol_table_manager, SymbolTable.SymbolTableManager)
        assert isinstance(self.regular_definition, RegExpr.RegularDefinition)
        assert isinstance(self.translation_rules, list)
        self._verify()

    def _verify(self):
        for translation_rule in self.translation_rules:
            assert isinstance(translation_rule, tuple)
            assert len(translation_rule) == 2
            pattern = translation_rule[0]
            action = translation_rule[1]
            if isinstance(pattern, Automata.Element):
                # Any Element d_i from the regular_definition
                assert pattern.value in self.regular_definition.regular_expressions
            elif isinstance(pattern, list):
                for element in pattern:
                    assert isinstance(element, Automata.Element)
                    # List of Element where no element is any d_i.
                    assert element.value not in self.regular_definition.regular_expressions
            else:
                raise Exception('Translation Rule must have a list or Element as the translation trigger')

            assert len(signature(action).parameters) == 2

    def process(self, character_iter):
        assert isinstance(character_iter, Iterable)



def do_stuff():
    # A -> a*b
    # B -> b a A
    # A = RegExpr.from_string('a*b')
    # before_add_B = RegExpr.from_string('ba')
    # B = RegExpr(before_add_B.expression + [Element(A)], Alphabet(before_add_B.alphabet.elements + [Element(A)]))
    # reg_def = RegularDefinition([A, B])
    reg_def = RegExpr.RegularDefinition.from_string('A a*b\nB ba{A}')
    print(reg_def)
    symbol_table_manager = SymbolTable.SymbolTableManager()

    def B_action(symbol_table, text):
        return Tokens.Token.Token(Enums.Tag.ID)

    translation_rules = [(Automata.Element(reg_def), B_action)]
    lexer = LexicalAnalyzer(symbol_table_manager, reg_def, translation_rules)
    print(lexer)


if __name__ == '__main__':
    do_stuff()