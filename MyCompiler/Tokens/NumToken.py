import Token
from Tokens.Tag import Tag


class NumToken(Token):
    def __init__(self, value):
        self.value = value
        super().__init__(Tag.NUM)
