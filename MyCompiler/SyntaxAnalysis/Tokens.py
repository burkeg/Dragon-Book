from Enums import Operation


class BaseToken:
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
        # assert isinstance(symbol_table, SymbolTable)
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
        return BaseToken(lexeme)
        # raise Exception('Not a valid lexeme for this token')


class IDToken(BaseToken):
    def __init__(self, lexeme):
        super().__init__(lexeme)

    @classmethod
    def create(cls, lexeme):
        return IDToken(lexeme)


class StringLiteralToken(BaseToken):
    def __init__(self, lexeme):
        super().__init__(lexeme)

    @classmethod
    def create(cls, lexeme):
        return StringLiteralToken(lexeme)


class NumToken(BaseToken):
    def __init__(self, lexeme):
        super().__init__(lexeme)

    @classmethod
    def create(cls, lexeme):
        return NumToken(lexeme)


class RelationalOperatorToken(BaseToken):
    def __init__(self, lexeme):
        value = None
        if lexeme == '==':
            value = Operation.EQUALS
        elif lexeme == '!=':
            value = Operation.NOT_EQUALS
        elif lexeme == '<':
            value = Operation.LT
        elif lexeme == '<=':
            value = Operation.LTE
        elif lexeme == '>':
            value = Operation.GT
        elif lexeme == '>=':
            value = Operation.GTE
        assert isinstance(value, Operation), 'Unknown relational operator'
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


class ArithmeticOperatorToken(BaseToken):
    def __init__(self, lexeme):
        value = None
        if lexeme == '+':
            value = Operation.PLUS
        elif lexeme == '-':
            value = Operation.MINUS
        elif lexeme == '*':
            value = Operation.MULTIPLY
        elif lexeme == '/':
            value = Operation.DIVIDE
        assert isinstance(value, Operation), 'Unknown arithmetic operator'
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


class LogicOperatorToken(BaseToken):
    def __init__(self, lexeme):
        value = None
        if lexeme == '&&':
            value = Operation.LOGIC_AND
        elif lexeme == '||':
            value = Operation.LOGIC_OR
        assert isinstance(value, Operation), 'Unknown logical operator'
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


class BitwiseOperatorToken(BaseToken):
    def __init__(self, lexeme):
        value = None
        if lexeme == '&':
            value = Operation.BIT_AND
        elif lexeme == '|':
            value = Operation.BIT_OR
        elif lexeme == '^':
            value = Operation.BIT_XOR
        assert isinstance(value, Operation), 'Unknown bitwise operator'
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


class AssignmentOperatorToken(BaseToken):
    def __init__(self, lexeme):
        value = None
        if lexeme == '=':
            value = Operation.ASSIGN
        elif lexeme == '+=':
            value = Operation.PLUS_EQUAL
        elif lexeme == '-=':
            value = Operation.MINUS_EQUAL
        elif lexeme == '*=':
            value = Operation.TIMES_EQUAL
        elif lexeme == '/=':
            value = Operation.DIVIDE_EQUAL
        assert isinstance(value, Operation), 'Unknown assignment operator'
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


class BracketToken(BaseToken):
    def __init__(self, lexeme):
        value = None
        if lexeme == '(':
            value = Operation.LEFT_PAREN
        elif lexeme == ')':
            value = Operation.RIGHT_PAREN
        elif lexeme == '[':
            value = Operation.LEFT_BRACKET
        elif lexeme == ']':
            value = Operation.RIGHT_BRACKET
        elif lexeme == '{':
            value = Operation.LEFT_CURLY
        elif lexeme == '}':
            value = Operation.RIGHT_CURLY
        assert isinstance(value, Operation), 'Unknown bracket'
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


class EndStatementToken(BaseToken):
    def __init__(self):
        super().__init__(';')

    @classmethod
    def create(cls, lexeme):
        if lexeme == ';':
            return EndStatementToken()
        else:
            return None


class ColonToken(BaseToken):
    def __init__(self):
        super().__init__(':')

    @classmethod
    def create(cls, lexeme):
        if lexeme == ':':
            return ColonToken()
        else:
            return None


class KeywordToken(BaseToken):
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


class QuoteToken(BaseToken):
    def __init__(self, lexeme):
        value = None
        if lexeme == "'":
            value = Operation.SINGLE_QUOTE
        elif lexeme == '"':
            value = Operation.DOUBLE_QUOTE
        assert isinstance(value, Operation), 'Unknown quote'
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


class ActionToken(BaseToken):
    def __init__(self, name, action=None):
        self.name = name
        super().__init__('', value=action)


class EmptyToken(BaseToken):
    def __init__(self):
        super().__init__('ε')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'ε':
            return EmptyToken()
        else:
            return None


class EndToken(BaseToken):
    def __init__(self):
        super().__init__('$')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '$':
            return EndToken()
        else:
            return None


class AutoToken(BaseToken):
    def __init__(self):
        super().__init__('auto')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'auto':
            return AutoToken()
        else:
            return None


class BreakToken(BaseToken):
    def __init__(self):
        super().__init__('break')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'break':
            return BreakToken()
        else:
            return None


class CaseToken(BaseToken):
    def __init__(self):
        super().__init__('case')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'case':
            return CaseToken()
        else:
            return None


class CharToken(BaseToken):
    def __init__(self):
        super().__init__('char')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'char':
            return CharToken()
        else:
            return None


class ConstToken(BaseToken):
    def __init__(self):
        super().__init__('const')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'const':
            return ConstToken()
        else:
            return None


class ContinueToken(BaseToken):
    def __init__(self):
        super().__init__('continue')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'continue':
            return ContinueToken()
        else:
            return None


class DefaultToken(BaseToken):
    def __init__(self):
        super().__init__('default')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'default':
            return DefaultToken()
        else:
            return None


class DoToken(BaseToken):
    def __init__(self):
        super().__init__('do')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'do':
            return DoToken()
        else:
            return None


class DoubleToken(BaseToken):
    def __init__(self):
        super().__init__('double')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'double':
            return DoubleToken()
        else:
            return None


class EnumToken(BaseToken):
    def __init__(self):
        super().__init__('enum')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'enum':
            return EnumToken()
        else:
            return None


class ExternToken(BaseToken):
    def __init__(self):
        super().__init__('extern')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'extern':
            return ExternToken()
        else:
            return None


class FloatToken(BaseToken):
    def __init__(self):
        super().__init__('float')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'float':
            return FloatToken()
        else:
            return None


class ForToken(BaseToken):
    def __init__(self):
        super().__init__('for')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'for':
            return ForToken()
        else:
            return None


class GotoToken(BaseToken):
    def __init__(self):
        super().__init__('goto')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'goto':
            return GotoToken()
        else:
            return None


class IntToken(BaseToken):
    def __init__(self):
        super().__init__('int')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'int':
            return IntToken()
        else:
            return None


class LongToken(BaseToken):
    def __init__(self):
        super().__init__('long')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'long':
            return LongToken()
        else:
            return None


class RegisterToken(BaseToken):
    def __init__(self):
        super().__init__('register')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'register':
            return RegisterToken()
        else:
            return None


class ReturnToken(BaseToken):
    def __init__(self):
        super().__init__('return')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'return':
            return ReturnToken()
        else:
            return None


class ShortToken(BaseToken):
    def __init__(self):
        super().__init__('short')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'short':
            return ShortToken()
        else:
            return None


class SignedToken(BaseToken):
    def __init__(self):
        super().__init__('signed')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'signed':
            return SignedToken()
        else:
            return None


class SizeofToken(BaseToken):
    def __init__(self):
        super().__init__('sizeof')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'sizeof':
            return SizeofToken()
        else:
            return None


class StaticToken(BaseToken):
    def __init__(self):
        super().__init__('static')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'static':
            return StaticToken()
        else:
            return None


class StructToken(BaseToken):
    def __init__(self):
        super().__init__('struct')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'struct':
            return StructToken()
        else:
            return None


class SwitchToken(BaseToken):
    def __init__(self):
        super().__init__('switch')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'switch':
            return SwitchToken()
        else:
            return None


class TypedefToken(BaseToken):
    def __init__(self):
        super().__init__('typedef')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'typedef':
            return TypedefToken()
        else:
            return None


class UnionToken(BaseToken):
    def __init__(self):
        super().__init__('union')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'union':
            return UnionToken()
        else:
            return None


class UnsignedToken(BaseToken):
    def __init__(self):
        super().__init__('unsigned')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'unsigned':
            return UnsignedToken()
        else:
            return None


class VoidToken(BaseToken):
    def __init__(self):
        super().__init__('void')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'void':
            return VoidToken()
        else:
            return None


class VolatileToken(BaseToken):
    def __init__(self):
        super().__init__('volatile')

    @classmethod
    def create(cls, lexeme):
        if lexeme == 'volatile':
            return VolatileToken()
        else:
            return None


class EllipsisToken(BaseToken):
    def __init__(self):
        super().__init__('...')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '...':
            return EllipsisToken()
        else:
            return None


class RShiftEqualsToken(BaseToken):
    def __init__(self):
        super().__init__('>>=')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '>>=':
            return RShiftEqualsToken()
        else:
            return None


class LShiftEqualsToken(BaseToken):
    def __init__(self):
        super().__init__('<<=')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '<<=':
            return LShiftEqualsToken()
        else:
            return None


class ModEqualsToken(BaseToken):
    def __init__(self):
        super().__init__('%=')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '%=':
            return ModEqualsToken()
        else:
            return None


class AndEqualsToken(BaseToken):
    def __init__(self):
        super().__init__('&=')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '&=':
            return AndEqualsToken()
        else:
            return None


class XorEqualsToken(BaseToken):
    def __init__(self):
        super().__init__('^=')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '^=':
            return XorEqualsToken()
        else:
            return None


class OrEqualsToken(BaseToken):
    def __init__(self):
        super().__init__('|=')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '|=':
            return OrEqualsToken()
        else:
            return None


class RShiftToken(BaseToken):
    def __init__(self):
        super().__init__('>>')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '>>':
            return RShiftToken()
        else:
            return None


class LShiftToken(BaseToken):
    def __init__(self):
        super().__init__('<<')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '<<':
            return LShiftToken()
        else:
            return None


class IncrementToken(BaseToken):
    def __init__(self):
        super().__init__('++')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '++':
            return IncrementToken()
        else:
            return None


class DecrementToken(BaseToken):
    def __init__(self):
        super().__init__('--')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '--':
            return DecrementToken()
        else:
            return None


class ArrowToken(BaseToken):
    def __init__(self):
        super().__init__('->')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '->':
            return ArrowToken()
        else:
            return None


class CommaToken(BaseToken):
    def __init__(self):
        super().__init__(',')

    @classmethod
    def create(cls, lexeme):
        if lexeme == ',':
            return CommaToken()
        else:
            return None


class DotToken(BaseToken):
    def __init__(self):
        super().__init__('.')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '.':
            return DotToken()
        else:
            return None


class NotToken(BaseToken):
    def __init__(self):
        super().__init__('!')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '!':
            return NotToken()
        else:
            return None


class TildeToken(BaseToken):
    def __init__(self):
        super().__init__('~')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '~':
            return TildeToken()
        else:
            return None


class AsterixToken(BaseToken):
    def __init__(self):
        super().__init__('*')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '*':
            return AsterixToken()
        else:
            return None


class PercentToken(BaseToken):
    def __init__(self):
        super().__init__('%')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '%':
            return PercentToken()
        else:
            return None


class LAngleToken(BaseToken):
    def __init__(self):
        super().__init__('<')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '<':
            return LAngleToken()
        else:
            return None


class RAngleToken(BaseToken):
    def __init__(self):
        super().__init__('>')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '>':
            return RAngleToken()
        else:
            return None


class QuestionToken(BaseToken):
    def __init__(self):
        super().__init__('?')

    @classmethod
    def create(cls, lexeme):
        if lexeme == '?':
            return QuestionToken()
        else:
            return None


def do_something():
    print(BaseToken.create('+='))


if __name__ == '__main__':
    do_something()

