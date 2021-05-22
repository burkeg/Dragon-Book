import Token
from Tokens.Tag import Tag


class IDToken(Token):
    def __init__(self, name, lexeme, value):
        super().__init__(Tag.ID, name, lexeme, value)
