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

    def test_default_lexer(self):
        ID = Tokens.IDToken
        Num = Tokens.NumToken
        Relop = Tokens.RelationalOperatorToken
        Arith = Tokens.ArithmeticOperatorToken
        Assign = Tokens.AssignmentOperatorToken
        Bracket = Tokens.BracketToken
        EndStmt = Tokens.EndImperativeStatementToken
        If = Tokens.IfToken
        Else = Tokens.ElseToken
        While = Tokens.WhileToken
        test_cases = {
            'aaa': [ID],
            'A': [ID],
            '123': [Num],
            '1+1;': [Num, Arith, Num, EndStmt],
            'a += b - 1': [ID, Assign, ID, Arith, Num],
            '{a[1]=45.1E-3;}': [Bracket, ID, Bracket, Num, Bracket, Assign, Num, EndStmt, Bracket],
            '{a[1]=45.1 E-3;}': [Bracket, ID, Bracket, Num, Bracket, Assign, Num, ID, Arith, Num, EndStmt, Bracket],
            '+==+=+++==': [Assign, Assign, Assign, Arith, Arith, Assign, Assign],
            'while_ while': [ID, While],
            'ififif ifif if': [ID, ID, If],
            'else elseelse': [Else, ID],
            '{}{{[]}}': [Bracket, Bracket, Bracket, Bracket, Bracket, Bracket, Bracket],
            'a <\n \t\t\n 5': [ID, Relop, Num],
            '<>>=<<=>': [Relop, Relop, Relop, Relop, Relop, Relop],
        }

        lexer = LexicalAnalyzer.LexicalAnalyzer.default_lexer()
        for string, expected_tokens in test_cases.items():
            with self.subTest(string=string):
                for token, expected_token in zip(lexer.process(string), expected_tokens):
                    assert isinstance(token, expected_token)

