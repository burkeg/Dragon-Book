from unittest import TestCase

import RegExpr
import Automata
import SymbolTable
import Enums
import LexicalAnalyzer
import Tokens


class TestLexicalAnalyzer(TestCase):
    def test_ids_and_numbers(self):
        test_cases = {
            'aaa',
            '123',
            'abc aaa',
            'abc aaa aaasdf222    \t\n   a123',
            'a',
            '1',
            '',
        }
        reg_def = RegExpr.RegularDefinition.from_string(r'delim [ \t\n]' + '\n' + \
            r'ws {delim}+' + '\n' + \
            r'letter a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z' + '\n' + \
            r'letter_ {letter}|_' + '\n' + \
            r'digit 0|1|2|3|4|5|6|7|8|9' + '\n' + \
            r'id {letter_}({letter_}|{digit})*' + '\n' + \
            r'number {digit}+(\.{digit}+)?(E[+-]?{digit}+)?')
        symbol_table_manager = SymbolTable.SymbolTableManager()

        translation_rules = [
            (Automata.Element(reg_def['id']), Tokens.IDToken.action),
            (Automata.Element(reg_def['number']), Tokens.NumToken.action)
        ]
        lexer = LexicalAnalyzer.LexicalAnalyzer(symbol_table_manager, reg_def, translation_rules)
        for case in test_cases:
            with self.subTest(case=case):
                tokens = []
                for token in lexer.process(case):
                    # print(token)
                    tokens.append(token)

                print(tokens)
                assert len(tokens) == len(case.split())

    def test_ids_and_numbers_and_operators(self):
        test_cases = {
            'a a',
        }
        reg_def = RegExpr.RegularDefinition.from_string(r'delim [ \t\n]' + '\n' + \
            r'ws {delim}+' + '\n' + \
            r'letter a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z' + '\n' + \
            r'letter_ {letter}|_' + '\n' + \
            r'type (int|bool)' + '\n' + \
            r'operator (\+|-|\*|/)' + '\n' + \
            r'digit 0|1|2|3|4|5|6|7|8|9' + '\n' + \
            r'id {letter_}({letter_}|{digit})*' + '\n' + \
            r'number {digit}+(\.{digit}+)?(E[+-]?{digit}+)?')
        symbol_table_manager = SymbolTable.SymbolTableManager()

        translation_rules = [
            (Automata.Element(reg_def['id']), Tokens.IDToken.action),
            (Automata.Element(reg_def['number']), Tokens.NumToken.action)
        ]
        lexer = LexicalAnalyzer.LexicalAnalyzer(symbol_table_manager, reg_def, translation_rules)
        for case in test_cases:
            with self.subTest(case=case):
                tokens = []
                for token in lexer.process(case):
                    # print(token)
                    tokens.append(token)

                print(tokens)

