from Terminal import Terminal
from Tokens import ActionToken


class ActionTerminal(Terminal):
    def __init__(self, action_name, action):
        super().__init__(action_name, ActionToken(action_name, action))

