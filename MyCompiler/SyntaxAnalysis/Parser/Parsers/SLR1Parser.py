from BaseGrammar import BaseGrammar
from BaseParser import BaseParser
from Enums import LRAction
from LR0Item import LR0Item
from LRState import LRState
from ParseTree import ParseTree
from SLRParsingTable import SLRParsingTable
from Terminal import Terminal, end_terminal


class SLR1Parser(BaseParser):
    def __init__(self, grammar):
        assert isinstance(grammar, BaseGrammar)
        super().__init__(grammar)
        self._parsing_table = None
        self._prepare_internals()
        self._verify()

    def _verify(self):
        pass

    def _prepare_internals(self):
        self._parsing_table = SLRParsingTable(self._grammar)

    def produce_derivation(self, w):
        assert isinstance(self._parsing_table, SLRParsingTable)
        def to_input_string(tokens):
            for token in tokens:
                yield Terminal(token=token)
            yield end_terminal

        # The input string is a
        input_string = to_input_string(w)
        stack = [self._parsing_table.start_state]
        a = next(input_string)
        while True:
            s = stack[-1]
            action, data = self._parsing_table.action(s, a)
            if action == LRAction.SHIFT:
                t = data
                assert isinstance(t, LRState)
                stack.append(t)
                yield a.token, None
                a = next(input_string)

            elif action == LRAction.REDUCE:
                item = data
                assert isinstance(item, LR0Item)
                for _ in item.production:
                    stack.pop(-1)
                t = stack[-1]
                stack.append(self._parsing_table.goto(t, item.A))
                yield item.A, item.production

            elif action == LRAction.ACCEPT:
                # Success!
                break
            elif action == LRAction.ERROR:
                # Handle error
                break
            else:
                raise Exception('Unknown action.')

    def to_parse_tree(self, derivation_iterator):
        children = []
        for data in derivation_iterator:
            if data[1] == None:
                child_token = data[0]
                # This is a terminal, we just shifted out a token
                children.append(ParseTree(child_token))
            else:
                parent = data[0]
                production = data[1]
                # assert len(production) == len(children)
                parent_tree = ParseTree(parent)
                parent_tree.children = children[-len(production):]
                children[-len(production):] = [parent_tree]
        assert len(children) == 1
        return children[0]
