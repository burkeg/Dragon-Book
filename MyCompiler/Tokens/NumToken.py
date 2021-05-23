import Token
from Enums import Tag


class NumToken(Token):
    def __init__(self, name, lexeme, value):
        super().__init__(Tag.NUM, name, lexeme, value)
