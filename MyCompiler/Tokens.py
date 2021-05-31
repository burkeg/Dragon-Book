import Enums
import SymbolTable


class Token:
    def __init__(self, lexeme, value=None, symbol_table_entry=None):
        self.lexeme = lexeme
        assert isinstance(lexeme, str)
        self.value = value
        self.symbol_table_entry = symbol_table_entry

    def __str__(self):
        return f"{self.__class__.__name__}(lexeme: '{self.lexeme}')"
    __repr__ = __str__

    @classmethod
    def action(cls, symbol_table, lexeme):
        assert isinstance(symbol_table, SymbolTable.SymbolTable)
        assert isinstance(lexeme, str)
        new_token = cls.create(lexeme)
        symbol_table.create_symbol(new_token)
        return new_token

    @staticmethod
    def create(lexeme):
        raise NotImplementedError()


class IDToken(Token):
    def __init__(self, lexeme):
        super().__init__(lexeme)

    @staticmethod
    def create(lexeme):
        return IDToken(lexeme)


class NumToken(Token):
    def __init__(self, lexeme):
        super().__init__(lexeme)

    @staticmethod
    def create(lexeme):
        return NumToken(lexeme)


class RelationalOperatorToken(Token):
    def __init__(self, lexeme):
        value = None
        if lexeme == '==':
            value = Enums.Operation.EQUALS
        elif lexeme == '!=':
            value = Enums.Operation.NOT_EQUALS
        elif lexeme == '<':
            value = Enums.Operation.LT
        elif lexeme == '<=':
            value = Enums.Operation.LTE
        elif lexeme == '>':
            value = Enums.Operation.GT
        elif lexeme == '>=':
            value = Enums.Operation.GTE
        assert isinstance(value, Enums.Operation), 'Unknown relational operator'
        super().__init__(lexeme, value)

    @staticmethod
    def create(lexeme):
        if lexeme == '==':
            return EqualsToken()
        elif lexeme == '!=':
            return NotEqualsToken()
        elif lexeme == '<':
            return LTToken()
        elif lexeme == '<=':
            return LTEToken()
        elif lexeme == '>':
            return GTToken()
        elif lexeme == '>=':
            return GTEToken()
        else:
            raise Exception('Not a valid lexeme for this token')


class EqualsToken(RelationalOperatorToken):
    def __init__(self):
        super().__init__('==')


class NotEqualsToken(RelationalOperatorToken):
    def __init__(self):
        super().__init__('!=')


class LTToken(RelationalOperatorToken):
    def __init__(self):
        super().__init__('<')


class LTEToken(RelationalOperatorToken):
    def __init__(self):
        super().__init__('<=')


class GTToken(RelationalOperatorToken):
    def __init__(self):
        super().__init__('>')


class GTEToken(RelationalOperatorToken):
    def __init__(self):
        super().__init__('>=')


class ArithmeticOperatorToken(Token):
    def __init__(self, lexeme):
        value = None
        if lexeme == '+':
            value = Enums.Operation.PLUS
        elif lexeme == '-':
            value = Enums.Operation.MINUS
        elif lexeme == '*':
            value = Enums.Operation.MULTIPLY
        elif lexeme == '/':
            value = Enums.Operation.DIVIDE
        assert isinstance(value, Enums.Operation), 'Unknown relational operator'
        super().__init__(lexeme, value)

    @staticmethod
    def create(lexeme):
        if lexeme == '+':
            return PlusToken()
        elif lexeme == '-':
            return MinusToken()
        elif lexeme == '*':
            return MultiplyToken()
        elif lexeme == '/':
            return DivideToken()
        else:
            raise Exception('Not a valid lexeme for this token')


class PlusToken(ArithmeticOperatorToken):
    def __init__(self):
        super().__init__('+')


class MinusToken(ArithmeticOperatorToken):
    def __init__(self):
        super().__init__('-')


class MultiplyToken(ArithmeticOperatorToken):
    def __init__(self):
        super().__init__('*')


class DivideToken(ArithmeticOperatorToken):
    def __init__(self):
        super().__init__('/')


class AssignmentOperatorToken(Token):
    def __init__(self, lexeme):
        value = None
        if lexeme == '=':
            value = Enums.Operation.ASSIGN
        elif lexeme == '+=':
            value = Enums.Operation.PLUS_EQUAL
        elif lexeme == '-=':
            value = Enums.Operation.MINUS_EQUAL
        elif lexeme == '*=':
            value = Enums.Operation.TIMES_EQUAL
        elif lexeme == '/=':
            value = Enums.Operation.DIVIDE_EQUAL
        assert isinstance(value, Enums.Operation), 'Unknown relational operator'
        super().__init__(lexeme, value)

    @staticmethod
    def create(lexeme):
        if lexeme == '=':
            return AssignToken()
        elif lexeme == '+=':
            return PlusEqualsToken()
        elif lexeme == '-=':
            return MinusEqualsToken()
        elif lexeme == '*=':
            return TimesEqualsToken()
        elif lexeme == '/=':
            return DivideEqualsToken()
        else:
            raise Exception('Not a valid lexeme for this token')


class AssignToken(AssignmentOperatorToken):
    def __init__(self):
        super().__init__('=')


class PlusEqualsToken(AssignmentOperatorToken):
    def __init__(self):
        super().__init__('+=')


class MinusEqualsToken(AssignmentOperatorToken):
    def __init__(self):
        super().__init__('-=')


class TimesEqualsToken(AssignmentOperatorToken):
    def __init__(self):
        super().__init__('*=')


class DivideEqualsToken(AssignmentOperatorToken):
    def __init__(self):
        super().__init__('/=')


class BracketToken(Token):
    def __init__(self, lexeme):
        value = None
        if lexeme == '(':
            value = Enums.Operation.LEFT_PAREN
        elif lexeme == ')':
            value = Enums.Operation.RIGHT_PAREN
        elif lexeme == '[':
            value = Enums.Operation.LEFT_BRACKET
        elif lexeme == ']':
            value = Enums.Operation.RIGHT_BRACKET
        elif lexeme == '{':
            value = Enums.Operation.LEFT_CURLY
        elif lexeme == '}':
            value = Enums.Operation.RIGHT_CURLY
        assert isinstance(value, Enums.Operation), 'Unknown relational operator'
        super().__init__(lexeme)

    @staticmethod
    def create(lexeme):
        if lexeme == '(':
            return LParenToken()
        elif lexeme == ')':
            return RParenToken()
        elif lexeme == '[':
            return LBracketToken()
        elif lexeme == ']':
            return RBracketToken()
        elif lexeme == '{':
            return LCurlyToken()
        elif lexeme == '}':
            return RCurlyToken()
        else:
            raise Exception('Not a valid lexeme for this token')


class LParenToken(BracketToken):
    def __init__(self):
        super().__init__('(')


class RParenToken(BracketToken):
    def __init__(self):
        super().__init__(')')


class LBracketToken(BracketToken):
    def __init__(self):
        super().__init__('[')


class RBracketToken(BracketToken):
    def __init__(self):
        super().__init__(']')


class LCurlyToken(BracketToken):
    def __init__(self):
        super().__init__('{')


class RCurlyToken(BracketToken):
    def __init__(self):
        super().__init__('}')


class EndImperativeStatementToken(Token):
    def __init__(self, lexeme):
        value = None
        if lexeme == ';':
            value = Enums.Operation.END_IMPERATIVE
        assert isinstance(value, Enums.Operation), 'Unknown relational operator'
        super().__init__(';', value)

    @staticmethod
    def create(lexeme):
        if lexeme == ';':
            return EndStatementToken()
        else:
            raise Exception('Not a valid lexeme for this token')


class EndStatementToken(EndImperativeStatementToken):
    def __init__(self):
        super().__init__(';')


class KeywordToken(Token):
    def __init__(self, lexeme):
        super().__init__(lexeme)

    @staticmethod
    def create(lexeme):
        if lexeme == 'if':
            return IfToken()
        elif lexeme == 'if':
            return IfToken()
        elif lexeme == 'else':
            return ElseToken()
        elif lexeme == 'while':
            return WhileToken()
        else:
            raise Exception('Not a valid lexeme for this token')


class IfToken(KeywordToken):
    def __init__(self):
        super().__init__(lexeme='if')


class ElseToken(KeywordToken):
    def __init__(self):
        super().__init__(lexeme='else')


class WhileToken(KeywordToken):
    def __init__(self):
        super().__init__(lexeme='while')