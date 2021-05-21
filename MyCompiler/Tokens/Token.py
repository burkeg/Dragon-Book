from Tokens import Tag


class Token:
    def __init__(self, tag):
        self.tag = tag
        assert isinstance(tag, Tag)