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
    def lex_action(cls, symbol_table, lexeme):
        assert isinstance(symbol_table, SymbolTable.SymbolTable)
        assert isinstance(lexeme, str)
        new_token = cls.create(lexeme)
        symbol_table.create_symbol(new_token)
        return new_token

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'id':
            return IDToken('')
        elif lexeme == 'num':
            return NumToken('')
        for subclass in cls.__subclasses__():
            if subclass == IDToken or \
                    subclass == NumToken or \
                    subclass == ActionToken:
                continue
            if token := subclass.create(lexeme):
                return token
        # last resort, make a generic token with that lexeme
        return Token(lexeme)
        # raise Exception('Not a valid lexeme for this token')


class IDToken(Token):
    def __init__(self, lexeme):
        super().__init__(lexeme)

    @classmethod
    def create(cls, lexeme):
        return IDToken(lexeme)


class NumToken(Token):
    def __init__(self, lexeme):
        super().__init__(lexeme)

    @classmethod
    def create(cls, lexeme):
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

    @classmethod
    def create(cls, lexeme):
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
            return None


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
        assert isinstance(value, Enums.Operation), 'Unknown arithmetic operator'
        super().__init__(lexeme, value)

    @classmethod
    def create(cls, lexeme):
        if lexeme == '+':
            return PlusToken()
        elif lexeme == '-':
            return MinusToken()
        elif lexeme == '*':
            return MultiplyToken()
        elif lexeme == '/':
            return DivideToken()
        else:
            return None


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


class LogicOperatorToken(Token):
    def __init__(self, lexeme):
        value = None
        if lexeme == '&&':
            value = Enums.Operation.LOGIC_AND
        elif lexeme == '||':
            value = Enums.Operation.LOGIC_OR
        assert isinstance(value, Enums.Operation), 'Unknown logical operator'
        super().__init__(lexeme, value)

    @classmethod
    def create(cls, lexeme):
        if lexeme == '&&':
            return LogicAndToken()
        elif lexeme == '||':
            return LogicOrToken()
        else:
            return None


class LogicAndToken(LogicOperatorToken):
    def __init__(self):
        super().__init__('&&')


class LogicOrToken(LogicOperatorToken):
    def __init__(self):
        super().__init__('||')


class BitwiseOperatorToken(Token):
    def __init__(self, lexeme):
        value = None
        if lexeme == '&':
            value = Enums.Operation.BIT_AND
        elif lexeme == '|':
            value = Enums.Operation.BIT_OR
        elif lexeme == '^':
            value = Enums.Operation.BIT_XOR
        assert isinstance(value, Enums.Operation), 'Unknown bitwise operator'
        super().__init__(lexeme, value)

    @classmethod
    def create(cls, lexeme):
        if lexeme == '&':
            return BitwiseAndToken()
        elif lexeme == '|':
            return BitwiseOrToken()
        elif lexeme == '^':
            return BitwiseXorToken()
        else:
            return None


class BitwiseAndToken(BitwiseOperatorToken):
    def __init__(self):
        super().__init__('&')


class BitwiseOrToken(BitwiseOperatorToken):
    def __init__(self):
        super().__init__('|')


class BitwiseXorToken(BitwiseOperatorToken):
    def __init__(self):
        super().__init__('^')


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
        assert isinstance(value, Enums.Operation), 'Unknown assignment operator'
        super().__init__(lexeme, value)

    @classmethod
    def create(cls, lexeme):
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
            return None


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
        assert isinstance(value, Enums.Operation), 'Unknown bracket'
        super().__init__(lexeme)

    @classmethod
    def create(cls, lexeme):
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
            return None


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


class EndStatementToken(Token):
    def __init__(self):
        super().__init__(';')

    @classmethod
    def create(cls, lexeme):
        if lexeme == ';':
            return EndStatementToken()
        else:
            return None


class ColonToken(Token):
    def __init__(self):
        super().__init__(':')

    @classmethod
    def create(cls, lexeme):
        if lexeme == ':':
            return ColonToken()
        else:
            return None


class KeywordToken(Token):
    def __init__(self, lexeme):
        super().__init__(lexeme)

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'if':
            return IfToken()
        elif lexeme == 'if':
            return IfToken()
        elif lexeme == 'else':
            return ElseToken()
        elif lexeme == 'while':
            return WhileToken()
        else:
            return None


class IfToken(KeywordToken):
    def __init__(self):
        super().__init__(lexeme='if')


class ElseToken(KeywordToken):
    def __init__(self):
        super().__init__(lexeme='else')


class WhileToken(KeywordToken):
    def __init__(self):
        super().__init__(lexeme='while')


class QuoteToken(Token):
    def __init__(self, lexeme):
        value = None
        if lexeme == "'":
            value = Enums.Operation.SINGLE_QUOTE
        elif lexeme == '"':
            value = Enums.Operation.DOUBLE_QUOTE
        assert isinstance(value, Enums.Operation), 'Unknown quote'
        super().__init__(lexeme)

    @classmethod
    def create(cls, lexeme):
        if lexeme == "'":
            return SingleQuoteToken()
        elif lexeme == '"':
            return DoubleQuoteToken()
        else:
            return None


class SingleQuoteToken(QuoteToken):
    def __init__(self):
        super().__init__("'")


class DoubleQuoteToken(QuoteToken):
    def __init__(self):
        super().__init__('"')


class ActionToken(Token):
    def __init__(self, name, action=None):
        self.name = name
        super().__init__('', value=action)


class EmptyToken(Token):
    def __init__(self):
        super().__init__('')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '\u03B5':
            return EmptyToken()
        else:
            return None


def do_something():
    print(Token.create('+='))


if __name__ == '__main__':
    do_something()
