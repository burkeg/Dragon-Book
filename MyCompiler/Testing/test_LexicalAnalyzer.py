from unittest import TestCase

import RegExpr
import Automata
import SymbolTable
import Enums
import Tokens
import LexicalAnalyzer


class TestLexicalAnalyzer(TestCase):
    def test_process(self):
        with self.subTest(type='simple'):
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

        with self.subTest(type='ID'):
            reg_def = RegExpr.RegularDefinition.from_string('A a\nB {A}*a')
            symbol_table_manager = SymbolTable.SymbolTableManager()

            def num_action(symbol_table, lexeme):
                assert isinstance(symbol_table, SymbolTable.SymbolTable)
                assert isinstance(lexeme, str)
                new_token = Tokens.Token.Token(Enums.Tag.NUM, '', lexeme)
                symbol_table.create_symbol(new_token)
                return new_token

            def ID_action(symbol_table, lexeme):
                assert isinstance(symbol_table, SymbolTable.SymbolTable)
                assert isinstance(lexeme, str)
                new_token = Tokens.Token.Token(Enums.Tag.ID, '', lexeme)
                symbol_table.create_symbol(new_token)
                return new_token

            translation_rules = [(Automata.Element(reg_def['A']), num_action),
                                 (Automata.Element(reg_def['B']), ID_action)]
            lexer = LexicalAnalyzer.LexicalAnalyzer(symbol_table_manager, reg_def, translation_rules)
            tokens = []
            for token in lexer.process('aaa'):
                # print(token)
                tokens.append(token)

            print(tokens)
            assert len(tokens) == 1

    def test_ids_and_numbers(self):
        test_cases = [
            'aaa',
            '123',
            'abc',
            'abc aaa',
            'abc aaa aaasdf222    \t\n   a',
        ]
        reg_def = RegExpr.RegularDefinition.from_string(r'delim [ \t\n]' + '\n' + \
            r'ws {delim}+' + '\n' + \
            r'letter a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z' + '\n' + \
            r'letter_ {letter}|_' + '\n' + \
            r'digit 0|1|2|3|4|5|6|7|8|9' + '\n' + \
            r'id {letter_}({letter_}|{digit})*' + '\n' + \
            r'number {digit}+(\.{digit}+)?(E[+-]?{digit}+)?')
        symbol_table_manager = SymbolTable.SymbolTableManager()

        def num_action(symbol_table, lexeme):
            assert isinstance(symbol_table, SymbolTable.SymbolTable)
            assert isinstance(lexeme, str)
            new_token = Tokens.Token.Token(Enums.Tag.NUM, '', lexeme)
            symbol_table.create_symbol(new_token)
            return new_token

        def ID_action(symbol_table, lexeme):
            assert isinstance(symbol_table, SymbolTable.SymbolTable)
            assert isinstance(lexeme, str)
            new_token = Tokens.Token.Token(Enums.Tag.ID, '', lexeme)
            symbol_table.create_symbol(new_token)
            return new_token

        translation_rules = [
            (Automata.Element(reg_def['id']), ID_action),
            (Automata.Element(reg_def['num']), num_action)
        ]
        lexer = LexicalAnalyzer.LexicalAnalyzer(symbol_table_manager, reg_def, translation_rules)
        for case in test_cases:
            with self.subTest(case=case):
                tokens = []
                for token in lexer.process(case):
                    # print(token)
                    tokens.append(token)

                print(tokens)
                assert len(tokens) > 0
