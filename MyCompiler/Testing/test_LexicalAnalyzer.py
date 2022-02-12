from unittest import TestCase

import RegExpr
import SymbolTable
import LexicalAnalyzer
from Tokens import IDToken, NumToken, RelationalOperatorToken, EqualsToken, NotEqualsToken, LTToken, LTEToken, \
    GTToken, GTEToken, ArithmeticOperatorToken, PlusToken, MinusToken, AsterixToken, DivideToken, LogicOperatorToken, \
    LogicAndToken, LogicOrToken, BitwiseOperatorToken, BitwiseAndToken, BitwiseOrToken, BitwiseXorToken, \
    AssignmentOperatorToken, AssignToken, PlusEqualsToken, MinusEqualsToken, TimesEqualsToken, DivideEqualsToken, \
    BracketToken, LParenToken, RParenToken, LBracketToken, RBracketToken, LCurlyToken, RCurlyToken, EndStatementToken, \
    KeywordToken, IfToken, ElseToken, WhileToken, ColonToken
from Elements import BaseElement


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
            (BaseElement(reg_def['id']), IDToken.lex_action),
            (BaseElement(reg_def['number']), NumToken.lex_action)
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
        ID = IDToken
        Num = NumToken
        Relop = RelationalOperatorToken
        Eq = EqualsToken
        NotEq = NotEqualsToken
        LT = LTToken
        LTE = LTEToken
        GT = GTToken
        GTE = GTEToken
        Arith = ArithmeticOperatorToken
        Plus = PlusToken
        Minus = MinusToken
        Mult = AsterixToken
        Div = DivideToken
        Logic = LogicOperatorToken
        LAnd = LogicAndToken
        LOr = LogicOrToken
        Bit = BitwiseOperatorToken
        BAnd = BitwiseAndToken
        BOr = BitwiseOrToken
        BXor = BitwiseXorToken
        Assignment = AssignmentOperatorToken
        Assign = AssignToken
        PlusEq = PlusEqualsToken
        MinusEq = MinusEqualsToken
        TimesEq = TimesEqualsToken
        DivEq = DivideEqualsToken
        Bracket = BracketToken
        LParen = LParenToken
        RParen = RParenToken
        LBracket = LBracketToken
        RBracket = RBracketToken
        LCurly = LCurlyToken
        RCurly = RCurlyToken
        EndStatement = EndStatementToken
        EndStmt = EndStatementToken
        Keyword = KeywordToken
        If = IfToken
        Else = ElseToken
        While = WhileToken
        Colon = ColonToken
        test_cases = {
            'aaa': [ID],
            'A': [ID],
            '123': [Num],
            '1+1;': [Num, Arith, Num, EndStatement],
            'a += b - 1': [ID, Assignment, ID, Arith, Num],
            '{a[1]=45.1E-3;}': [Bracket, ID, Bracket, Num, Bracket, Assignment, Num, EndStatement, Bracket],
            '{a[1]=45.1 E-3;}': [Bracket, ID, Bracket, Num, Bracket, Assignment, Num, ID, Arith, Num, EndStatement, Bracket],
            '+==+=+++==': [Assignment, Assignment, Assignment, Arith, Arith, Assignment, Assignment],
            'while_ while': [ID, While],
            'ififif ifif if': [ID, ID, Keyword],
            'else elseelse': [Keyword, ID],
            '{}{{[]}}': [Bracket, Bracket, Bracket, Bracket, Bracket, Bracket, Bracket],
            'a <\n \t\t\n 5': [ID, Relop, Num],
            '<>>=<<=>': [Relop, Relop, Relop, Relop, Relop, Relop],
            '&^|': [Bit, Bit, Bit, ],
            '&&||': [Logic, Logic, ],
            'a 1.3E+2 == != < <= > >= + - * / = += -= *= /= ( ) [ ] { } ; if else while && || & | ^ :':
                [ID, Num, Eq, NotEq, LT, LTE, GT, GTE, Plus, Minus, Mult, Div, Assign, PlusEq,
                 MinusEq, TimesEq, DivEq, LParen, RParen, LBracket, RBracket, LCurly, RCurly,
                 EndStmt, If, Else, While, LAnd, LOr, BAnd, BOr, BXor, Colon],
        }

        lexer = LexicalAnalyzer.LexicalAnalyzer.basic_expression_lexer()
        for string, expected_tokens in test_cases.items():
            with self.subTest(string=string):
                for token, expected_token in zip(lexer.process(string), expected_tokens):
                    assert isinstance(token, expected_token), f'{token} vs {expected_token}'

