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
            r"""
                ws \s+
                letter_ [a-zA-Z_]
                if if
                else else
                while while
                arithmetic_operator [-+*/]
                logical_operator (&&|\|\|)
                bitwise_operator [&|^]
                rel_operator (==|!=|<|<=|>|>=)
                assignment_operator (=|\+=|-=|\*=|/=)
                bracket_operator (\(|\)|\[|\]|\{|\})
                end_statement ;
                colon :
                id {letter_}({letter_}|\d)*
                number \d+(\.\d+)?(E[+-]?\d+)?
            """
        )
        symbol_table_manager = SymbolTable.SymbolTableManager()

        translation_rules = [
            (Automata.Element(reg_def['if']), Tokens.IfToken.lex_action),
            (Automata.Element(reg_def['else']), Tokens.ElseToken.lex_action),
            (Automata.Element(reg_def['while']), Tokens.WhileToken.lex_action),
            (Automata.Element(reg_def['arithmetic_operator']), Tokens.ArithmeticOperatorToken.lex_action),
            (Automata.Element(reg_def['logical_operator']), Tokens.LogicOperatorToken.lex_action),
            (Automata.Element(reg_def['bitwise_operator']), Tokens.BitwiseOperatorToken.lex_action),
            (Automata.Element(reg_def['rel_operator']), Tokens.RelationalOperatorToken.lex_action),
            (Automata.Element(reg_def['assignment_operator']), Tokens.AssignmentOperatorToken.lex_action),
            (Automata.Element(reg_def['bracket_operator']), Tokens.BracketToken.lex_action),
            (Automata.Element(reg_def['end_statement']), Tokens.EndStatementToken.lex_action),
            (Automata.Element(reg_def['colon']), Tokens.ColonToken.lex_action),
            (Automata.Element(reg_def['id']), Tokens.IDToken.lex_action),
            (Automata.Element(reg_def['number']), Tokens.NumToken.lex_action),
        ]
        return LexicalAnalyzer(symbol_table_manager, reg_def, translation_rules)

    @staticmethod
    def ANSI_C_lexer():
        reg_def = RegExpr.RegularDefinition.from_string(
            r"""
                D [0-9]
                L [a-zA-Z_]
                H [a-fA-F0-9]
                E [Ee][+-]?{D}+
                FS (f|F|l|L)
                IS (u|U|l|L)*
                AUTO auto
                BREAK break
                CASE case
                CHAR char
                CONST const
                CONTINUE continue
                DEFAULT default
                DO do
                DOUBLE double
                ELSE else
                ENUM enum
                EXTERN extern
                FLOAT float
                FOR for
                GOTO goto
                IF if
                INT int
                LONG long
                REGISTER register
                RETURN return
                SHORT short
                SIGNED signed
                SIZEOF sizeof
                STATIC static
                STRUCT struct
                SWITCH switch
                TYPEDEF typedef
                UNION union
                UNSIGNED unsigned
                VOID void
                VOLATILE volatile
                WHILE while
                IDENTIFIER {L}({L}|{D})*
                CONSTANT (0[xX]{H}+{IS}?)|(0{D}+{IS}?)|({D}+{IS}?)|(L?'(\\.|[^\\'])+')|({D}+{E}{FS}?)|({D}*"."{D}+({E})?{FS}?)|({D}+"."{D}*({E})?{FS}?)
                STRING_LITERAL L?\"(\\.|[^\\"])*\"
                ELLIPSIS ...
                RIGHT_ASSIGN >>=
                LEFT_ASSIGN <<=
                ADD_ASSIGN +=
                SUB_ASSIGN -=
                MUL_ASSIGN *=
                DIV_ASSIGN /=
                MOD_ASSIGN %=
                AND_ASSIGN &=
                XOR_ASSIGN ^=
                OR_ASSIGN |=
                RIGHT_OP >>
                LEFT_OP <<
                INC_OP ++
                DEC_OP --
                PTR_OP ->
                AND_OP &&
                OR_OP ||
                LE_OP <=
                GE_OP >=
                EQ_OP ==
                NE_OP !=
                SEMICOLON \;
                LCURLY \{
                RCURLY \}
                COMMA \,
                COLON \:
                EQUAL \=
                LPAREN \(
                RPAREN \)
                LSQUARE \[
                RSQUARE \]
                DOT \.
                AND \&
                NOT \!
                TILDE \~
                MINUS \-
                PLUS \+
                ASTERIX \*
                FWD_SLASH \/
                PERCENT \%
                LANGLE \<
                RANGLE \>
                CARET \^
                PIPE \|
                QUESTION \?
                WHITESPACE [ \t\v\n\f]
            """
        )
        symbol_table_manager = SymbolTable.SymbolTableManager()

        translation_rules = [
            (Automata.Element(reg_def['AUTO']), Tokens.AutoToken.lex_action),
            (Automata.Element(reg_def['BREAK']), Tokens.BreakToken.lex_action),
            (Automata.Element(reg_def['CASE']), Tokens.CaseToken.lex_action),
            (Automata.Element(reg_def['CHAR']), Tokens.CharToken.lex_action),
            (Automata.Element(reg_def['CONST']), Tokens.ConstToken.lex_action),
            (Automata.Element(reg_def['CONTINUE']), Tokens.ContinueToken.lex_action),
            (Automata.Element(reg_def['DEFAULT']), Tokens.DefaultToken.lex_action),
            (Automata.Element(reg_def['DO']), Tokens.DoToken.lex_action),
            (Automata.Element(reg_def['DOUBLE']), Tokens.DoubleToken.lex_action),
            (Automata.Element(reg_def['ELSE']), Tokens.ElseToken.lex_action),
            (Automata.Element(reg_def['ENUM']), Tokens.EnumToken.lex_action),
            (Automata.Element(reg_def['EXTERN']), Tokens.ExternToken.lex_action),
            (Automata.Element(reg_def['FLOAT']), Tokens.FloatToken.lex_action),
            (Automata.Element(reg_def['FOR']), Tokens.ForToken.lex_action),
            (Automata.Element(reg_def['GOTO']), Tokens.GotoToken.lex_action),
            (Automata.Element(reg_def['IF']), Tokens.IfToken.lex_action),
            (Automata.Element(reg_def['INT']), Tokens.IntToken.lex_action),
            (Automata.Element(reg_def['LONG']), Tokens.LongToken.lex_action),
            (Automata.Element(reg_def['REGISTER']), Tokens.RegisterToken.lex_action),
            (Automata.Element(reg_def['RETURN']), Tokens.ReturnToken.lex_action),
            (Automata.Element(reg_def['SHORT']), Tokens.ShortToken.lex_action),
            (Automata.Element(reg_def['SIGNED']), Tokens.SignedToken.lex_action),
            (Automata.Element(reg_def['SIZEOF']), Tokens.SizeofToken.lex_action),
            (Automata.Element(reg_def['STATIC']), Tokens.StaticToken.lex_action),
            (Automata.Element(reg_def['STRUCT']), Tokens.StructToken.lex_action),
            (Automata.Element(reg_def['SWITCH']), Tokens.SwitchToken.lex_action),
            (Automata.Element(reg_def['TYPEDEF']), Tokens.TypedefToken.lex_action),
            (Automata.Element(reg_def['UNION']), Tokens.UnionToken.lex_action),
            (Automata.Element(reg_def['UNSIGNED']), Tokens.UnsignedToken.lex_action),
            (Automata.Element(reg_def['VOID']), Tokens.VoidToken.lex_action),
            (Automata.Element(reg_def['VOLATILE']), Tokens.VolatileToken.lex_action),
            (Automata.Element(reg_def['WHILE']), Tokens.WhileToken.lex_action),
            (Automata.Element(reg_def['IDENTIFIER']), Tokens.IDToken.lex_action),
            (Automata.Element(reg_def['CONSTANT']), Tokens.NumToken.lex_action),
            (Automata.Element(reg_def['STRING_LITERAL']), Tokens.StringLiteralToken.lex_action),
            (Automata.Element(reg_def['ELLIPSIS']), Tokens.EllipsisToken.lex_action),
            (Automata.Element(reg_def['RIGHT_ASSIGN']), Tokens.RShiftEqualsToken.lex_action),
            (Automata.Element(reg_def['LEFT_ASSIGN']), Tokens.LShiftEqualsToken.lex_action),
            (Automata.Element(reg_def['ADD_ASSIGN']), Tokens.PlusEqualsToken.lex_action),
            (Automata.Element(reg_def['SUB_ASSIGN']), Tokens.MinusEqualsToken.lex_action),
            (Automata.Element(reg_def['MUL_ASSIGN']), Tokens.TimesEqualsToken.lex_action),
            (Automata.Element(reg_def['DIV_ASSIGN']), Tokens.DivideEqualsToken.lex_action),
            (Automata.Element(reg_def['MOD_ASSIGN']), Tokens.ModEqualsToken.lex_action),
            (Automata.Element(reg_def['AND_ASSIGN']), Tokens.AndEqualsToken.lex_action),
            (Automata.Element(reg_def['XOR_ASSIGN']), Tokens.XorEqualsToken.lex_action),
            (Automata.Element(reg_def['OR_ASSIGN']), Tokens.OrEqualsToken.lex_action),
            (Automata.Element(reg_def['RIGHT_OP']), Tokens.RShiftToken.lex_action),
            (Automata.Element(reg_def['LEFT_OP']), Tokens.LShiftToken.lex_action),
            (Automata.Element(reg_def['INC_OP']), Tokens.IncrementToken.lex_action),
            (Automata.Element(reg_def['DEC_OP']), Tokens.DecrementToken.lex_action),
            (Automata.Element(reg_def['PTR_OP']), Tokens.ArrowToken.lex_action),
            (Automata.Element(reg_def['AND_OP']), Tokens.LogicAndToken.lex_action),
            (Automata.Element(reg_def['OR_OP']), Tokens.LogicOrToken.lex_action),
            (Automata.Element(reg_def['LE_OP']), Tokens.LTEToken.lex_action),
            (Automata.Element(reg_def['GE_OP']), Tokens.GTEToken.lex_action),
            (Automata.Element(reg_def['EQ_OP']), Tokens.EqualsToken.lex_action),
            (Automata.Element(reg_def['NE_OP']), Tokens.NotEqualsToken.lex_action),
            (Automata.Element(reg_def['SEMICOLON']), Tokens.EndStatementToken.lex_action),
            (Automata.Element(reg_def['LCURLY']), Tokens.LCurlyToken.lex_action),
            (Automata.Element(reg_def['RCURLY']), Tokens.RCurlyToken.lex_action),
            (Automata.Element(reg_def['COMMA']), Tokens.CommaToken.lex_action),
            (Automata.Element(reg_def['COLON']), Tokens.ColonToken.lex_action),
            (Automata.Element(reg_def['EQUAL']), Tokens.AssignToken.lex_action),
            (Automata.Element(reg_def['LPAREN']), Tokens.LParenToken.lex_action),
            (Automata.Element(reg_def['RPAREN']), Tokens.RParenToken.lex_action),
            (Automata.Element(reg_def['LSQUARE']), Tokens.LBracketToken.lex_action),
            (Automata.Element(reg_def['RSQUARE']), Tokens.RBracketToken.lex_action),
            (Automata.Element(reg_def['DOT']), Tokens.DotToken.lex_action),
            (Automata.Element(reg_def['AND']), Tokens.BitwiseAndToken.lex_action),
            (Automata.Element(reg_def['NOT']), Tokens.NotToken.lex_action),
            (Automata.Element(reg_def['TILDE']), Tokens.TildeToken.lex_action),
            (Automata.Element(reg_def['MINUS']), Tokens.MinusToken.lex_action),
            (Automata.Element(reg_def['PLUS']), Tokens.PlusToken.lex_action),
            (Automata.Element(reg_def['ASTERIX']), Tokens.AsterixToken.lex_action),
            (Automata.Element(reg_def['FWD_SLASH']), Tokens.DivideToken.lex_action),
            (Automata.Element(reg_def['PERCENT']), Tokens.PercentToken.lex_action),
            (Automata.Element(reg_def['LANGLE']), Tokens.LAngleToken.lex_action),
            (Automata.Element(reg_def['RANGLE']), Tokens.RAngleToken.lex_action),
            (Automata.Element(reg_def['CARET']), Tokens.BitwiseXorToken.lex_action),
            (Automata.Element(reg_def['PIPE']), Tokens.BitwiseOrToken.lex_action),
            (Automata.Element(reg_def['QUESTION']), Tokens.QuestionToken.lex_action),
        ]
        return LexicalAnalyzer(symbol_table_manager, reg_def, translation_rules)


def do_stuff():
    lexer = LexicalAnalyzer.default_lexer()
    tokens = []
    for token in lexer.process('abc + 123; 1E9 += 1 - ab_3452;\n\nif (ten == 10) { a = 4; } ^'):
        tokens.append(token)

    pp.pprint(tokens)


if __name__ == '__main__':
    do_stuff()