import math
from inspect import signature

from Tokens import IfToken, ElseToken, ArithmeticOperatorToken, WhileToken, BitwiseOperatorToken, LogicOperatorToken, \
    RelationalOperatorToken, AssignmentOperatorToken, BracketToken, EndStatementToken, ColonToken, IDToken, NumToken, \
    AutoToken, BreakToken, CaseToken, CharToken, ConstToken, ContinueToken, DefaultToken, DoToken, DoubleToken, \
    EnumToken, ExternToken, FloatToken, ForToken, GotoToken, IntToken, LongToken, RegisterToken, ReturnToken, \
    ShortToken, SignedToken, SizeofToken, StaticToken, StructToken, SwitchToken, TypedefToken, UnionToken, \
    UnsignedToken, VoidToken, VolatileToken, StringLiteralToken, EllipsisToken, RShiftEqualsToken, LShiftEqualsToken, \
    PlusEqualsToken, MinusEqualsToken, TimesEqualsToken, DivideEqualsToken, ModEqualsToken, AndEqualsToken, \
    XorEqualsToken, OrEqualsToken, RShiftToken, LShiftToken, IncrementToken, DecrementToken, ArrowToken, LogicAndToken, \
    LogicOrToken, LTEToken, GTEToken, EqualsToken, NotEqualsToken, LCurlyToken, RCurlyToken, CommaToken, AssignToken, \
    LParenToken, RParenToken, LBracketToken, RBracketToken, DotToken, BitwiseAndToken, NotToken, TildeToken, MinusToken, \
    PlusToken, AsterixToken, DivideToken, PercentToken, LAngleToken, RAngleToken, BitwiseXorToken, BitwiseOrToken, \
    QuestionToken
from Alphabet import Alphabet
from Elements import BaseElement, EmptyExpression, EOF
from NFA import NFA
from NFASimulator import NFASimulator
from RegExpr import RegularDefinition, RegExpr
from States import NFAState, ProductionState
from SymbolTable import SymbolTableManager
from Transition import Transition


class LexicalAnalyzer:
    def __init__(self, symbol_table_manager, regular_definition, translation_rules):
        # symbol_table is an instance of the SymbolTableManager class
        # regular_definition is an instance of the RegularDefinition class
        # translation_rules is a list of 2-tuples with the following format:
        #   pattern: Any BaseElement d_i from the regular_definition or list of BaseElement
        #       where no element is any d_i.
        #   action: A function with 2 arguments:
        #           symbol_table, A reference to the symbol_table
        #           lexeme, string corresponding with the current lexeme
        #       Any side effects should be written to the Symbol table.
        #       You can also optionally return a token.

        self.symbol_table_manager = symbol_table_manager
        self.regular_definition = regular_definition
        self.translation_rules = translation_rules
        assert isinstance(self.symbol_table_manager, SymbolTableManager)
        assert isinstance(self.regular_definition, RegularDefinition)
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
            if isinstance(pattern, BaseElement):
                if  pattern.value is not None:
                    # Any BaseElement d_i from the regular_definition
                    assert pattern.value in self.regular_definition.regular_expressions
            elif isinstance(pattern, list):
                for element in pattern:
                    assert isinstance(element, BaseElement)
                    # List of BaseElement where no element is any d_i.
                    assert element.value not in self.regular_definition.regular_expressions
            else:
                raise Exception('Translation Rule must have a list or BaseElement as the translation trigger')

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
        root = NFAState('start')
        NFAs = []
        alphabet = Alphabet([])
        for regex in self.regular_definition.regular_expressions:
            assert isinstance(regex, RegExpr)
            curr_NFA = regex.to_NFA()
            root.add_outgoing(Transition(
                element=EmptyExpression(),
                target=curr_NFA.start))
            curr_NFA.stop.accepting = False

            # If we have a callback for this endpoint let's hook it up here.
            new_end_state = None
            if regex in self._d_i_to_action:
                new_end_state = ProductionState(
                    action=self._d_i_to_action[regex],
                    d_i=regex)
            else:
                new_end_state = ProductionState(
                    action=lambda a, b: None,
                    d_i=regex)
            curr_NFA.stop.add_outgoing(Transition(
                element=EmptyExpression(),
                target=new_end_state))
            NFAs.append(new_end_state)
            alphabet.union_update(regex.alphabet)

        self._orig_NFAs = NFAs
        # Ignore sub-regular expressions
        alphabet = Alphabet(
            [element for element in alphabet if not isinstance(element.value, RegExpr)])
        self._NFA = NFA(root, alphabet)
        self._simulator = NFASimulator(self._NFA)

    def process(self, input_characters):
        assert isinstance(self._simulator, NFASimulator)
        input_elements = BaseElement.element_list_from_string(input_characters)
        while len(input_elements) > 0:
            match_history = []
            simulator_generator = self._simulator.simulate_gen(input_elements)
            while not isinstance((accepting_states := next(simulator_generator)), EOF):
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

            assert isinstance(producing_state, ProductionState)
            lexeme_elements = input_elements[:chars_consumed]
            lexeme = ''.join([element.value for element in lexeme_elements])
            assert isinstance(self.symbol_table_manager, SymbolTableManager)
            if token := producing_state.action(self.symbol_table_manager.curr_table(), lexeme):
                yield token

            input_elements = input_elements[chars_consumed:]

    @staticmethod
    def basic_expression_lexer():
        reg_def = RegularDefinition.from_string(
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
        symbol_table_manager = SymbolTableManager()

        translation_rules = [
            (BaseElement(reg_def['if']), IfToken.lex_action),
            (BaseElement(reg_def['else']), ElseToken.lex_action),
            (BaseElement(reg_def['while']), WhileToken.lex_action),
            (BaseElement(reg_def['arithmetic_operator']), ArithmeticOperatorToken.lex_action),
            (BaseElement(reg_def['logical_operator']), LogicOperatorToken.lex_action),
            (BaseElement(reg_def['bitwise_operator']), BitwiseOperatorToken.lex_action),
            (BaseElement(reg_def['rel_operator']), RelationalOperatorToken.lex_action),
            (BaseElement(reg_def['assignment_operator']), AssignmentOperatorToken.lex_action),
            (BaseElement(reg_def['bracket_operator']), BracketToken.lex_action),
            (BaseElement(reg_def['end_statement']), EndStatementToken.lex_action),
            (BaseElement(reg_def['colon']), ColonToken.lex_action),
            (BaseElement(reg_def['id']), IDToken.lex_action),
            (BaseElement(reg_def['number']), NumToken.lex_action),
        ]
        return LexicalAnalyzer(symbol_table_manager, reg_def, translation_rules)

    @staticmethod
    def ANSI_C_lexer():
        reg_def = RegularDefinition.from_string(
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
                CONSTANT (0[xX]{H}+{IS}?)|(0{D}+{IS}?)|({D}+{IS}?)|('(\\.|[^\\'])')|({D}+{E}{FS}?)|({D}*\.{D}+({E})?{FS}?)|({D}+\.{D}*({E})?{FS}?)
                STRING_LITERAL \"(\\.|[^\\"])*\"
                ELLIPSIS \.\.\.
                RIGHT_ASSIGN >>=
                LEFT_ASSIGN <<=
                ADD_ASSIGN \+=
                SUB_ASSIGN -=
                MUL_ASSIGN \*=
                DIV_ASSIGN /=
                MOD_ASSIGN %=
                AND_ASSIGN &=
                XOR_ASSIGN ^=
                OR_ASSIGN \|=
                RIGHT_OP >>
                LEFT_OP <<
                INC_OP \+\+
                DEC_OP --
                PTR_OP ->
                AND_OP &&
                OR_OP \|\|
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
        symbol_table_manager = SymbolTableManager()

        translation_rules_short = [            ('AUTO', AutoToken),
            ('BREAK', BreakToken),
            ('CASE', CaseToken),
            ('CHAR', CharToken),
            ('CONST', ConstToken),
            ('CONTINUE', ContinueToken),
            ('DEFAULT', DefaultToken),
            ('DO', DoToken),
            ('DOUBLE', DoubleToken),
            ('ELSE', ElseToken),
            ('ENUM', EnumToken),
            ('EXTERN', ExternToken),
            ('FLOAT', FloatToken),
            ('FOR', ForToken),
            ('GOTO', GotoToken),
            ('IF', IfToken),
            ('INT', IntToken),
            ('LONG', LongToken),
            ('REGISTER', RegisterToken),
            ('RETURN', ReturnToken),
            ('SHORT', ShortToken),
            ('SIGNED', SignedToken),
            ('SIZEOF', SizeofToken),
            ('STATIC', StaticToken),
            ('STRUCT', StructToken),
            ('SWITCH', SwitchToken),
            ('TYPEDEF', TypedefToken),
            ('UNION', UnionToken),
            ('UNSIGNED', UnsignedToken),
            ('VOID', VoidToken),
            ('VOLATILE', VolatileToken),
            ('WHILE', WhileToken),
            ('IDENTIFIER', IDToken),
            ('CONSTANT', NumToken),
            ('STRING_LITERAL', StringLiteralToken),
            ('ELLIPSIS', EllipsisToken),
            ('RIGHT_ASSIGN', RShiftEqualsToken),
            ('LEFT_ASSIGN', LShiftEqualsToken),
            ('ADD_ASSIGN', PlusEqualsToken),
            ('SUB_ASSIGN', MinusEqualsToken),
            ('MUL_ASSIGN', TimesEqualsToken),
            ('DIV_ASSIGN', DivideEqualsToken),
            ('MOD_ASSIGN', ModEqualsToken),
            ('AND_ASSIGN', AndEqualsToken),
            ('XOR_ASSIGN', XorEqualsToken),
            ('OR_ASSIGN', OrEqualsToken),
            ('RIGHT_OP', RShiftToken),
            ('LEFT_OP', LShiftToken),
            ('INC_OP', IncrementToken),
            ('DEC_OP', DecrementToken),
            ('PTR_OP', ArrowToken),
            ('AND_OP', LogicAndToken),
            ('OR_OP', LogicOrToken),
            ('LE_OP', LTEToken),
            ('GE_OP', GTEToken),
            ('EQ_OP', EqualsToken),
            ('NE_OP', NotEqualsToken),
            ('SEMICOLON', EndStatementToken),
            ('LCURLY', LCurlyToken),
            ('RCURLY', RCurlyToken),
            ('COMMA', CommaToken),
            ('COLON', ColonToken),
            ('EQUAL', AssignToken),
            ('LPAREN', LParenToken),
            ('RPAREN', RParenToken),
            ('LSQUARE', LBracketToken),
            ('RSQUARE', RBracketToken),
            ('DOT', DotToken),
            ('AND', BitwiseAndToken),
            ('NOT', NotToken),
            ('TILDE', TildeToken),
            ('MINUS', MinusToken),
            ('PLUS', PlusToken),
            ('ASTERIX', AsterixToken),
            ('FWD_SLASH', DivideToken),
            ('PERCENT', PercentToken),
            ('LANGLE', LAngleToken),
            ('RANGLE', RAngleToken),
            ('CARET', BitwiseXorToken),
            ('PIPE', BitwiseOrToken),
            ('QUESTION', QuestionToken),
        ]
        translation_rules = []
        for name, cls in translation_rules_short:
            translation_rules.append((BaseElement(reg_def[name]), getattr(cls, 'lex_action')))

        return LexicalAnalyzer(symbol_table_manager, reg_def, translation_rules)
