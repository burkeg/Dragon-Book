import Token
from Tokens.Tag import Tag


class IDToken(Token):
    def __init__(self, name):
        self.name = name
        super().__init__(Tag.ID)
