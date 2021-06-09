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
            return IDToken('id')
        elif lexeme == 'num':
            return NumToken('num')
        elif lexeme == 'str':
            return NumToken('str')
        for subclass in cls.__subclasses__():
            if subclass == IDToken or \
                    subclass == NumToken or \
                    subclass == StringLiteralToken or \
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


class StringLiteralToken(Token):
    def __init__(self, lexeme):
        super().__init__(lexeme)

    @classmethod
    def create(cls, lexeme):
        return StringLiteralToken(lexeme)


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
            return AsterixToken()
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
        super().__init__('ε')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'ε':
            return EmptyToken()
        else:
            return None


class AutoToken(Token):
    def __init__(self):
        super().__init__('auto')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'auto':
            return AutoToken()
        else:
            return None


class BreakToken(Token):
    def __init__(self):
        super().__init__('break')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'break':
            return BreakToken()
        else:
            return None


class CaseToken(Token):
    def __init__(self):
        super().__init__('case')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'case':
            return CaseToken()
        else:
            return None


class CharToken(Token):
    def __init__(self):
        super().__init__('char')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'char':
            return CharToken()
        else:
            return None


class ConstToken(Token):
    def __init__(self):
        super().__init__('const')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'const':
            return ConstToken()
        else:
            return None


class ContinueToken(Token):
    def __init__(self):
        super().__init__('continue')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'continue':
            return ContinueToken()
        else:
            return None


class DefaultToken(Token):
    def __init__(self):
        super().__init__('default')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'default':
            return DefaultToken()
        else:
            return None


class DoToken(Token):
    def __init__(self):
        super().__init__('do')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'do':
            return DoToken()
        else:
            return None


class DoubleToken(Token):
    def __init__(self):
        super().__init__('double')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'double':
            return DoubleToken()
        else:
            return None


class EnumToken(Token):
    def __init__(self):
        super().__init__('enum')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'enum':
            return EnumToken()
        else:
            return None


class ExternToken(Token):
    def __init__(self):
        super().__init__('extern')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'extern':
            return ExternToken()
        else:
            return None


class FloatToken(Token):
    def __init__(self):
        super().__init__('float')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'float':
            return FloatToken()
        else:
            return None


class ForToken(Token):
    def __init__(self):
        super().__init__('for')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'for':
            return ForToken()
        else:
            return None


class GotoToken(Token):
    def __init__(self):
        super().__init__('goto')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'goto':
            return GotoToken()
        else:
            return None


class IntToken(Token):
    def __init__(self):
        super().__init__('int')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'int':
            return IntToken()
        else:
            return None


class LongToken(Token):
    def __init__(self):
        super().__init__('long')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'long':
            return LongToken()
        else:
            return None


class RegisterToken(Token):
    def __init__(self):
        super().__init__('register')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'register':
            return RegisterToken()
        else:
            return None


class ReturnToken(Token):
    def __init__(self):
        super().__init__('return')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'return':
            return ReturnToken()
        else:
            return None


class ShortToken(Token):
    def __init__(self):
        super().__init__('short')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'short':
            return ShortToken()
        else:
            return None


class SignedToken(Token):
    def __init__(self):
        super().__init__('signed')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'signed':
            return SignedToken()
        else:
            return None


class SizeofToken(Token):
    def __init__(self):
        super().__init__('sizeof')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'sizeof':
            return SizeofToken()
        else:
            return None


class StaticToken(Token):
    def __init__(self):
        super().__init__('static')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'static':
            return StaticToken()
        else:
            return None


class StructToken(Token):
    def __init__(self):
        super().__init__('struct')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'struct':
            return StructToken()
        else:
            return None


class SwitchToken(Token):
    def __init__(self):
        super().__init__('switch')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'switch':
            return SwitchToken()
        else:
            return None


class TypedefToken(Token):
    def __init__(self):
        super().__init__('typedef')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'typedef':
            return TypedefToken()
        else:
            return None


class UnionToken(Token):
    def __init__(self):
        super().__init__('union')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'union':
            return UnionToken()
        else:
            return None


class UnsignedToken(Token):
    def __init__(self):
        super().__init__('unsigned')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'unsigned':
            return UnsignedToken()
        else:
            return None


class VoidToken(Token):
    def __init__(self):
        super().__init__('void')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'void':
            return VoidToken()
        else:
            return None


class VolatileToken(Token):
    def __init__(self):
        super().__init__('volatile')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'volatile':
            return VolatileToken()
        else:
            return None


class EllipsisToken(Token):
    def __init__(self):
        super().__init__('...')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '...':
            return EllipsisToken()
        else:
            return None


class RShiftEqualsToken(Token):
    def __init__(self):
        super().__init__('>>=')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '>>=':
            return RShiftEqualsToken()
        else:
            return None


class LShiftEqualsToken(Token):
    def __init__(self):
        super().__init__('<<=')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '<<=':
            return LShiftEqualsToken()
        else:
            return None


class ModEqualsToken(Token):
    def __init__(self):
        super().__init__('%=')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '%=':
            return ModEqualsToken()
        else:
            return None


class AndEqualsToken(Token):
    def __init__(self):
        super().__init__('&=')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '&=':
            return AndEqualsToken()
        else:
            return None


class XorEqualsToken(Token):
    def __init__(self):
        super().__init__('^=')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '^=':
            return XorEqualsToken()
        else:
            return None


class OrEqualsToken(Token):
    def __init__(self):
        super().__init__('|=')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '|=':
            return OrEqualsToken()
        else:
            return None


class RShiftToken(Token):
    def __init__(self):
        super().__init__('>>')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '>>':
            return RShiftToken()
        else:
            return None


class LShiftToken(Token):
    def __init__(self):
        super().__init__('<<')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '<<':
            return LShiftToken()
        else:
            return None


class IncrementToken(Token):
    def __init__(self):
        super().__init__('++')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '++':
            return IncrementToken()
        else:
            return None


class DecrementToken(Token):
    def __init__(self):
        super().__init__('--')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '--':
            return DecrementToken()
        else:
            return None


class ArrowToken(Token):
    def __init__(self):
        super().__init__('->')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '->':
            return ArrowToken()
        else:
            return None


class CommaToken(Token):
    def __init__(self):
        super().__init__(',')

    @classmethod
    def create(cls, lexeme):
        if lexeme == ',':
            return CommaToken()
        else:
            return None


class DotToken(Token):
    def __init__(self):
        super().__init__('.')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '.':
            return DotToken()
        else:
            return None


class NotToken(Token):
    def __init__(self):
        super().__init__('!')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '!':
            return NotToken()
        else:
            return None


class TildeToken(Token):
    def __init__(self):
        super().__init__('~')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '~':
            return TildeToken()
        else:
            return None


class AsterixToken(Token):
    def __init__(self):
        super().__init__('*')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '*':
            return AsterixToken()
        else:
            return None


class PercentToken(Token):
    def __init__(self):
        super().__init__('%')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '%':
            return PercentToken()
        else:
            return None


class LAngleToken(Token):
    def __init__(self):
        super().__init__('<')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '<':
            return LAngleToken()
        else:
            return None


class RAngleToken(Token):
    def __init__(self):
        super().__init__('>')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '>':
            return RAngleToken()
        else:
            return None


class QuestionToken(Token):
    def __init__(self):
        super().__init__('?')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '?':
            return QuestionToken()
        else:
            return None


def do_something():
    print(Token.create('+='))


if __name__ == '__main__':
    do_something()

