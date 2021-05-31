import math
import pprint as pp
from inspect import signature

import Automata
import AutomataAlgorithms
import RegExpr
import SymbolTable
import Tokens


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
        self._d_i_to_priority = dict()
        for d_i in self.regular_definition.regular_expressions:
            self._d_i_to_priority[d_i] = math.inf

        priority = 0
        for d_i, action in self.translation_rules:
            self._d_i_to_action[d_i.value] = action
            self._d_i_to_priority[d_i.value] = priority
            priority += 1

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
                    accepted_states = list(accepting_states)
                    chars_consumed = len(match_history) - i
                    break

            accepted_states.sort(key=lambda state: self._d_i_to_priority[state.d_i])
            producing_state = accepted_states.pop(0)

            assert isinstance(producing_state, Automata.ProductionState)
            lexeme_elements = input_elements[:chars_consumed]
            lexeme = ''.join([element.value for element in lexeme_elements])
            assert isinstance(self.symbol_table_manager, SymbolTable.SymbolTableManager)
            if token := producing_state.action(self.symbol_table_manager.curr_table(), lexeme):
                yield token

            input_elements = input_elements[chars_consumed:]

    @staticmethod
    def default_lexer():
        reg_def = RegExpr.RegularDefinition.from_string(
            r'ws \s+' + '\n' +
            r'letter_ [a-zA-Z_]' + '\n' +
            r'if if' + '\n' +
            r'else else' + '\n' +
            r'while while' + '\n' +
            r'arithmetic_operator (\+|-|\*|/)' + '\n' +
            r'rel_operator (==|!=|<|<=|>|>=)' + '\n' +
            r'assignment_operator (=|\+=|-=|\*=|/=)' + '\n' +
            r'bracket_operator (\(|\)|\[|\]|\{|\})' + '\n' +
            r'end_imperitive_statement ;' + '\n' +
            r'id {letter_}({letter_}|\d)*' + '\n' +
            r'number \d+(\.\d+)?(E[+-]?\d+)?')
        symbol_table_manager = SymbolTable.SymbolTableManager()

        translation_rules = [
            (Automata.Element(reg_def['if']), Tokens.IfToken.action),
            (Automata.Element(reg_def['else']), Tokens.ElseToken.action),
            (Automata.Element(reg_def['while']), Tokens.WhileToken.action),
            (Automata.Element(reg_def['arithmetic_operator']), Tokens.ArithmeticOperatorToken.action),
            (Automata.Element(reg_def['rel_operator']), Tokens.RelationalOperatorToken.action),
            (Automata.Element(reg_def['assignment_operator']), Tokens.AssignmentOperatorToken.action),
            (Automata.Element(reg_def['bracket_operator']), Tokens.BracketToken.action),
            (Automata.Element(reg_def['end_imperitive_statement']), Tokens.EndImperativeStatementToken.action),
            (Automata.Element(reg_def['id']), Tokens.IDToken.action),
            (Automata.Element(reg_def['number']), Tokens.NumToken.action),
        ]
        return LexicalAnalyzer(symbol_table_manager, reg_def, translation_rules)


def do_stuff():
    lexer = LexicalAnalyzer.default_lexer()
    tokens = []
    for token in lexer.process('abc + 123; 1E9 += 1 - ab_3452;\n\nif (ten == 10) { a = 4; }'):
        # print(token)
        tokens.append(token)

    pp.pprint(tokens)


if __name__ == '__main__':
    do_stuff()