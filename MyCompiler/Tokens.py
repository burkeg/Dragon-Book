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


class IDToken(Token):
    def __init__(self, lexeme, value):
        super().__init__(lexeme, value)

    @staticmethod
    def action(symbol_table, lexeme):
        assert isinstance(symbol_table, SymbolTable.SymbolTable)
        assert isinstance(lexeme, str)
        new_token = IDToken(lexeme, lexeme)
        symbol_table.create_symbol(new_token)
        return new_token

class NumToken(Token):
    def __init__(self, lexeme, value):
        super().__init__(lexeme, value)

    @staticmethod
    def action(symbol_table, lexeme):
        assert isinstance(symbol_table, SymbolTable.SymbolTable)
        assert isinstance(lexeme, str)
        new_token = NumToken(lexeme, lexeme)
        symbol_table.create_symbol(new_token)
        return new_token

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
    def action(symbol_table, lexeme):
        assert isinstance(symbol_table, SymbolTable.SymbolTable)
        assert isinstance(lexeme, str)
        new_token = RelationalOperatorToken(lexeme)
        symbol_table.create_symbol(new_token)
        return new_token

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
    def action(symbol_table, lexeme):
        assert isinstance(symbol_table, SymbolTable.SymbolTable)
        assert isinstance(lexeme, str)
        new_token = ArithmeticOperatorToken(lexeme)
        symbol_table.create_symbol(new_token)
        return new_token

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
    def action(symbol_table, lexeme):
        assert isinstance(symbol_table, SymbolTable.SymbolTable)
        assert isinstance(lexeme, str)
        new_token = AssignmentOperatorToken(lexeme)
        symbol_table.create_symbol(new_token)
        return new_token

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
    def action(symbol_table, lexeme):
        assert isinstance(symbol_table, SymbolTable.SymbolTable)
        assert isinstance(lexeme, str)
        new_token = BracketToken(lexeme)
        symbol_table.create_symbol(new_token)
        return new_token

class EndImperativeStatementToken(Token):
    def __init__(self, lexeme):
        value = None
        if lexeme == ';':
            value = Enums.Operation.END_IMPERATIVE
        assert isinstance(value, Enums.Operation), 'Unknown relational operator'
        super().__init__(lexeme, value)

    @staticmethod
    def action(symbol_table, lexeme):
        assert isinstance(symbol_table, SymbolTable.SymbolTable)
        assert isinstance(lexeme, str)
        new_token = EndImperativeStatementToken(lexeme)
        symbol_table.create_symbol(new_token)
        return new_token

class IfToken(Token):
    def __init__(self):
        super().__init__(lexeme='if')

    @staticmethod
    def action(symbol_table, lexeme):
        assert isinstance(symbol_table, SymbolTable.SymbolTable)
        assert isinstance(lexeme, str)
        new_token = IfToken()
        symbol_table.create_symbol(new_token)
        return new_token

class ElseToken(Token):
    def __init__(self):
        super().__init__(lexeme='else')

    @staticmethod
    def action(symbol_table, lexeme):
        assert isinstance(symbol_table, SymbolTable.SymbolTable)
        assert isinstance(lexeme, str)
        new_token = ElseToken()
        symbol_table.create_symbol(new_token)
        return new_token

class WhileToken(Token):
    def __init__(self):
        super().__init__(lexeme='while')

    @staticmethod
    def action(symbol_table, lexeme):
        assert isinstance(symbol_table, SymbolTable.SymbolTable)
        assert isinstance(lexeme, str)
        new_token = WhileToken()
        symbol_table.create_symbol(new_token)
        return new_token