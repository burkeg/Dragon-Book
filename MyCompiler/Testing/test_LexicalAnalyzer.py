from unittest import TestCase

import RegExpr
import Automata
import SymbolTable
import Enums
import Tokens
import LexicalAnalyzer


class TestLexicalAnalyzer(TestCase):
    def test_process(self):
        reg_def = RegExpr.RegularDefinition.from_string('A baab\nB baab')
        symbol_table_manager = SymbolTable.SymbolTableManager()

        def A_action(symbol_table, lexeme):
            assert isinstance(symbol_table, SymbolTable.SymbolTable)
            assert isinstance(lexeme, str)
            new_token = Tokens.Token.Token(Enums.Tag.NUM, '', lexeme)
            symbol_table.create_symbol(new_token)
            return new_token

        def B_action(symbol_table, lexeme):
            assert isinstance(symbol_table, SymbolTable.SymbolTable)
            assert isinstance(lexeme, str)
            new_token = Tokens.Token.Token(Enums.Tag.ID, '', lexeme)
            symbol_table.create_symbol(new_token)
            return new_token

        translation_rules = [(Automata.Element(reg_def['A']), A_action),
                             (Automata.Element(reg_def['B']), B_action)]
        lexer = LexicalAnalyzer.LexicalAnalyzer(symbol_table_manager, reg_def, translation_rules)
        tokens = []
        for token in lexer.process('baabbaab'):
            # print(token)
            tokens.append(token)

        print(tokens)
        assert len(tokens) == 2
