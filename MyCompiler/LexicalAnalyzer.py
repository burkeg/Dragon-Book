import Automata
import AutomataAlgorithms
import Enums
import RegExpr
import SymbolTable
from inspect import signature
import Tokens.Token
from collections.abc import Iterable


class LexicalAnalyzer:
    def __init__(self, symbol_table_manager, regular_definition, translation_rules):
        # symbol_table is an instance of the SymbolTableManager class
        # regular_definition is an instance of the RegularDefinition class
        # translation_rules is a list of 2-tuples with the following format:
        #   pattern: Any Element d_i from the regular_definition or list of Element
        #       where no element is any d_i.
        #   action: A function with 2 arguments:
        #           symbol_table, A reference to the symbol_table
        #           lexeme, string corresponding with the current lexeme
        #       Any side effects should be written to the Symbol table.
        #       You can also optionally return a token.

        self.symbol_table_manager = symbol_table_manager
        self.regular_definition = regular_definition
        self.translation_rules = translation_rules
        assert isinstance(self.symbol_table_manager, SymbolTable.SymbolTableManager)
        assert isinstance(self.regular_definition, RegExpr.RegularDefinition)
        assert isinstance(self.translation_rules, list)
        self._verify()
        self._d_i_to_action = dict()
        self._orig_NFAs = None
        self._NFA = None
        self._simulator = None
        self._prepare_automata()

    def _verify(self):
        for translation_rule in self.translation_rules:
            assert isinstance(translation_rule, tuple)
            assert len(translation_rule) == 2
            pattern = translation_rule[0]
            action = translation_rule[1]
            if isinstance(pattern, Automata.Element):
                if  pattern.value is not None:
                    # Any Element d_i from the regular_definition
                    assert pattern.value in self.regular_definition.regular_expressions
            elif isinstance(pattern, list):
                for element in pattern:
                    assert isinstance(element, Automata.Element)
                    # List of Element where no element is any d_i.
                    assert element.value not in self.regular_definition.regular_expressions
            else:
                raise Exception('Translation Rule must have a list or Element as the translation trigger')

            assert len(signature(action).parameters) == 2

    def _prepare_automata(self):
        self._d_i_to_action = dict()
        for d_i, action in self.translation_rules:
            self._d_i_to_action[d_i.value] = action

        # We need to combine all original NFAs into a single one
        root = Automata.NFAState('start')
        NFAs = []
        alphabet = Automata.Alphabet([])
        for regex in self.regular_definition.regular_expressions:
            assert isinstance(regex, RegExpr.RegExpr)
            curr_NFA = regex.to_NFA()
            root.add_outgoing(Automata.Transition(
                element=Automata.EmptyExpression(),
                target=curr_NFA.start))
            curr_NFA.stop.accepting = False

            # If we have a callback for this endpoint let's hook it up here.
            new_end_state = None
            if regex in self._d_i_to_action:
                new_end_state = Automata.ProductionState(
                    action=self._d_i_to_action[regex],
                    d_i=regex)
            else:
                new_end_state = Automata.ProductionState(
                    action=lambda a, b: None,
                    d_i=regex)
            curr_NFA.stop.add_outgoing(Automata.Transition(
                element=Automata.EmptyExpression(),
                target=new_end_state))
            NFAs.append(new_end_state)
            alphabet.union_update(regex.alphabet)

        self._orig_NFAs = NFAs
        # Ignore sub-regular expressions
        alphabet = Automata.Alphabet(
            [element for element in alphabet if not isinstance(element.value, RegExpr.RegExpr)])
        self._NFA = Automata.NFA(root, alphabet)
        self._simulator = AutomataAlgorithms.NFASimulator(self._NFA)


    def process(self, input_characters):
        assert isinstance(self._simulator, AutomataAlgorithms.NFASimulator)
        input_elements = Automata.Element.element_list_from_string(input_characters)
        while len(input_elements) > 0:
            match_history = []
            simulator_generator = self._simulator.simulate_gen(input_elements)
            while not isinstance((accepting_states := next(simulator_generator)), AutomataAlgorithms.EOF):
                match_history.append(accepting_states)

            if len(match_history) == 0:
                raise Exception('Cannot produce a token from this string.')

            accepted_states = None
            chars_consumed = 0
            for i, accepting_states in enumerate(reversed(match_history)):
                # assert isinstance(accepted_states, set)
                if len(accepting_states) > 0:
                    accepted_states = accepting_states
                    chars_consumed = len(match_history) - i
                    break

            producing_state = None
            if len(accepted_states) > 1:
                # We have to decide between multiple productions. The winner is the one declared first.
                for accepted_state in accepted_states:
                    if producing_state is not None:
                        break
                    for d_i in self.regular_definition.regular_expressions:
                        if producing_state is not None:
                            break
                        for d_i_priority in self.regular_definition.regular_expressions:
                            # Skip over expressions that don't have productions associated with them.
                            if d_i_priority not in self._d_i_to_action.keys():
                                continue
                            if d_i == d_i_priority:
                                producing_state = accepted_state
                                break
            else:
                # 1 and only state:
                producing_state = accepted_states.pop()

            assert isinstance(producing_state, Automata.ProductionState)
            lexeme_elements = input_elements[:chars_consumed]
            lexeme = ''.join([element.value for element in lexeme_elements])
            assert isinstance(self.symbol_table_manager, SymbolTable.SymbolTableManager)
            print(producing_state.action)
            produced_token = producing_state.action(self.symbol_table_manager.curr_table(), lexeme)
            for i in range(100):
                print(i)
                producing_state.action(self.symbol_table_manager.curr_table(), lexeme)
            print(produced_token)
            if produced_token:
                print('True')
            else:
                print('False')
            if produced_token is not None:
                yield produced_token

            input_elements = input_elements[chars_consumed:]








def num_action(symbol_table, lexeme):
    assert isinstance(symbol_table, SymbolTable.SymbolTable)
    assert isinstance(lexeme, str)
    new_token = Tokens.Token.Token(Enums.Tag.NUM, '', lexeme)
    symbol_table.create_symbol(new_token)
    return new_token

def ID_action(symbol_table, lexeme):
    print("entering ID action")
    assert isinstance(symbol_table, SymbolTable.SymbolTable)
    assert isinstance(lexeme, str)
    new_token = Tokens.Token.Token(Enums.Tag.ID, '', lexeme)
    symbol_table.create_symbol(new_token)
    print(f'Producing token: {new_token}')
    return new_token

def do_stuff():
    # A -> a*b
    # B -> b a A
    # A = RegExpr.from_string('a*b')
    # before_add_B = RegExpr.from_string('ba')
    # B = RegExpr(before_add_B.expression + [Element(A)], Alphabet(before_add_B.alphabet.elements + [Element(A)]))
    # reg_def = RegularDefinition([A, B])

    # reg_def = RegExpr.RegularDefinition.from_string('A baab\nB baab')
    # symbol_table_manager = SymbolTable.SymbolTableManager()
    #
    # def A_action(symbol_table, lexeme):
    #     assert isinstance(symbol_table, SymbolTable.SymbolTable)
    #     assert isinstance(lexeme, str)
    #     new_token = Tokens.Token.Token(Enums.Tag.NUM, '', lexeme)
    #     symbol_table.create_symbol(new_token)
    #     return new_token
    #
    # def B_action(symbol_table, lexeme):
    #     assert isinstance(symbol_table, SymbolTable.SymbolTable)
    #     assert isinstance(lexeme, str)
    #     new_token = Tokens.Token.Token(Enums.Tag.ID, '', lexeme)
    #     symbol_table.create_symbol(new_token)
    #     return new_token
    #
    # translation_rules = [(Automata.Element(reg_def['A']), A_action),
    #                      (Automata.Element(reg_def['B']), B_action)]
    # lexer = LexicalAnalyzer(symbol_table_manager, reg_def, translation_rules)
    # for token in lexer.process('baabbaab'):
    #     print(token)
    #
    # print()
    # reg_def = RegExpr.RegularDefinition.from_string(r'delim [ \t\n]' + '\n' + \
    #     r'ws {delim}+' + '\n' + \
    #     r'letter a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z' + '\n' + \
    #     r'letter_ {letter}|_' + '\n' + \
    #     r'digit 0|1|2|3|4|5|6|7|8|9' + '\n' + \
    #     r'id {letter_}({letter_}|{digit})*' + '\n' + \
    #     r'number {digit}+(\.{digit}+)?(E[+-]?{digit}+)?')
    reg_def = RegExpr.RegularDefinition.from_string(
        r'letter a|b' + '\n' + \
        r'digit 0|1' + '\n' + \
        r'id {letter}({letter}|{digit})*')
    symbol_table_manager = SymbolTable.SymbolTableManager()

    translation_rules = [
        (Automata.Element(reg_def['id']), ID_action),
        # (Automata.Element(reg_def['number']), num_action)
    ]
    lexer = LexicalAnalyzer(symbol_table_manager, reg_def, translation_rules)
    tokens = []
    for token in lexer.process('a'):
        # print(token)
        tokens.append(token)

    print(tokens)
    assert len(tokens) == 1


if __name__ == '__main__':
    do_stuff()