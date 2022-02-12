from BaseAutomata import BaseAutomata


class BaseSimulator:
    def __init__(self, automata):
        assert isinstance(automata, BaseAutomata)
        self.automata = automata
