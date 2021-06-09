import copy
import math
import string

import Automata
import Enums


class RegExprParseTree:
    def __init__(self, left, operation, right=None):
        self.left = left
        self.operation = operation
        self.right = right
        if isinstance(left, Automata.Element) and self.operation != Enums.RegexOperation.IDENTITY:
            self.left = RegExprParseTree(left, Enums.RegexOperation.IDENTITY)
        if isinstance(right, Automata.Element) and \
                self.operation != Enums.RegexOperation.IDENTITY and \
                self.operation != Enums.RegexOperation.QUANTIFIER:
            self.right = RegExprParseTree(right, Enums.RegexOperation.IDENTITY)
        assert isinstance(operation, Enums.RegexOperation)
        if self.operation == Enums.RegexOperation.CONCAT:
            assert isinstance(self.left, RegExprParseTree)
            assert isinstance(self.right, RegExprParseTree)
        elif self.operation == Enums.RegexOperation.UNION:
            assert isinstance(self.left, RegExprParseTree)
            assert isinstance(self.right, RegExprParseTree)
        elif self.operation == Enums.RegexOperation.QUANTIFIER:
            assert isinstance(self.left, RegExprParseTree)
            assert isinstance(self.right, Automata.QuantifierElement)
        elif self.operation == Enums.RegexOperation.GROUP:
            assert isinstance(self.left, RegExprParseTree)
        elif self.operation == Enums.RegexOperation.IDENTITY:
            assert isinstance(self.left, Automata.Element)
        elif self.operation == Enums.RegexOperation.CHAR_CLASS:
            assert isinstance(self.left, RegExprParseTree)

    @staticmethod
    def build_from_expression(expression):
        expression = RegExprParseTree.handle_identity(expression)
        expression = RegExprParseTree.handle_char_class(expression)
        expression = RegExprParseTree.handle_escaped_special_chars(expression)
        expression = RegExprParseTree.handle_grouping(expression)
        expression = RegExprParseTree.handle_quantifiers(expression)
        expression = RegExprParseTree.handle_concat(expression)
        expression = RegExprParseTree.handle_union(expression)

        if len(expression) != 1:
            raise Exception('Something went wrong when generating the regex '
                            'parse tree')
        else:
            return expression[0]

    @staticmethod
    def handle_identity(expression):
        new_expression = []
        for term in expression:
            if isinstance(term, Automata.Element) and not isinstance(term, Automata.QuantifierElement):
                new_expression.append(RegExprParseTree(term, Enums.RegexOperation.IDENTITY))
            else:
                new_expression.append(term)
        return new_expression

    @staticmethod
    def range_over_chars(start, stop):
        # Either ranging over letters of numbers
        assert isinstance(start, str), len(start) == 1
        assert isinstance(stop, str), len(stop) == 1
        assert ord(start) <= ord(stop)
        if start.isdigit() and stop.isdigit() or \
            start.islower() and stop.islower() or \
            start.isupper() and stop.isupper():
            return set([chr(ASCII_num) for ASCII_num in range(ord(start), ord(stop) + 1)])
        else:
            raise Exception('Character class must be across letters of the same casing or digits.')

    @staticmethod
    def handle_char_class(expression):
        if len(expression) == 0:
            return []
        if len(expression) == 1:
            return expression

        if expression[0] == Enums.SpecialCharacter.LEFT_SQUARE_BRACKET:
            # Search for the matching close parenthesis and recursively build a tree
            paren_cnt = 1
            for i, term in enumerate(expression[1:]):
                if term == Enums.SpecialCharacter.LEFT_SQUARE_BRACKET:
                    paren_cnt += 1
                elif term == Enums.SpecialCharacter.RIGHT_SQUARE_BRACKET:
                    paren_cnt -= 1

                if paren_cnt == 0:
                    # We found the matching close square bracket
                    expressions_inside_parens = expression[1:(i+1)]
                    expressions_outside_parens = expression[i+2:]

                    if len(expressions_inside_parens) == 0:
                        return [Automata.UnmatchableElement()]

                    is_negative = False

                    char_list = []
                    for expression_inside_parens in expressions_inside_parens:
                        error_str = 'Character classes should only operate on single character ' \
                                    'strings or shorthand classes.'
                        if isinstance(expression_inside_parens, Enums.SpecialCharacter):
                            # Special characters have their meaning ignored inside character classes
                            char_list.append(str(expression_inside_parens))
                            continue
                        if isinstance(expression_inside_parens, Automata.QuantifierElement):
                            char_list.append(expression_inside_parens.value)
                            continue

                        assert isinstance(expression_inside_parens, RegExprParseTree), error_str
                        assert expression_inside_parens.operation == Enums.RegexOperation.IDENTITY, error_str
                        elem = expression_inside_parens.left
                        assert isinstance(elem, Automata.Element), error_str
                        assert isinstance(elem, Automata.EscapedCharElement) or \
                               isinstance(elem, Automata.CharClassElement) or \
                               (isinstance(elem.value, str) and len(elem.value) == 1), error_str
                        char_list.append(elem.value)

                    # look for a minus sign to indicate a range of characters
                    char_set = set()

                    if char_list[0] == '^':
                        char_list = char_list[1:]
                        is_negative = True

                    for idx, char in enumerate(char_list):
                        if isinstance(char, Enums.ShorthandCharacterClass):
                            char_set.update(char.to_char_set())
                            continue
                        elif isinstance(char, Enums.SpecialEscapedCharacter):
                            char_set.add(str(char))
                        if char == '-':
                            if idx == 0 or idx == len(char_list) - 1:
                                # If we see the range indicator at the start or end it's a literal '-'
                                char_set.add(char)
                            else:
                                range_of_chars = RegExprParseTree.range_over_chars(char_list[idx-1], char_list[idx+1])
                                char_set.update(range_of_chars)
                        else:
                            char_set.add(char)

                    # now we have all the characters in this character class
                    if is_negative:
                        char_set = set(string.printable).difference(char_set)

                    if len(char_set) == 0:
                        return [Automata.UnmatchableElement()]

                    expression_list = []
                    for idx, char in enumerate(char_set):
                        expression_list.append(Automata.Element(char))
                        if idx != len(char_set) - 1:
                            expression_list.append(Enums.SpecialCharacter.UNION)

                    tree_inside_brackets =  RegExprParseTree.build_from_expression(expression_list)

                    return RegExprParseTree.handle_char_class(
                        [tree_inside_brackets] + expressions_outside_parens)
        else:
            return [expression[0]] + \
                   RegExprParseTree.handle_char_class(expression[1:])

    @staticmethod
    def handle_escaped_special_chars(expression):
        new_expression = []
        for term in expression:
            if isinstance(term, RegExprParseTree) and term.operation == Enums.RegexOperation.IDENTITY:
                elem = term.left
                if isinstance(elem, Automata.EscapedCharElement):
                    if elem.value == Enums.SpecialEscapedCharacter.TAB:
                        new_expression.append(Automata.Element('\t'))
                    elif elem.value == Enums.SpecialEscapedCharacter.NEWLINE:
                        new_expression.append(Automata.Element('\n'))
                    else:
                        raise Exception('Unknown escaped special character')
                elif isinstance(elem, Automata.CharClassElement):
                    had_minus = False
                    had_caret = False
                    char_set = elem.value.to_char_set()
                    if '-' in char_set:
                        had_minus = True
                        char_set.remove('-')
                    if '^' in char_set:
                        had_caret = True
                        char_set.remove('^')
                    char_only = [Automata.Element(char) for char in char_set]
                    if had_caret:
                        char_only.append(Automata.Element('^'))
                    if had_minus:
                        char_only.append(Automata.Element('-'))
                    elements = [Enums.SpecialCharacter.LEFT_SQUARE_BRACKET] + \
                               char_only + \
                               [Enums.SpecialCharacter.RIGHT_SQUARE_BRACKET]
                    new_expression.append(RegExprParseTree.build_from_expression(elements))
                else:
                    new_expression.append(RegExprParseTree(elem, Enums.RegexOperation.IDENTITY))
            else:
                new_expression.append(term)
        return RegExprParseTree.handle_identity(new_expression)

    @staticmethod
    def handle_grouping(expression):
        if len(expression) == 0:
            return []
        if len(expression) == 1:
            return expression

        if expression[0] == Enums.SpecialCharacter.LEFT_PAREN:
            # Search for the matching close parenthesis and recursively build a tree
            paren_cnt = 1
            for i, term in enumerate(expression[1:]):
                if term == Enums.SpecialCharacter.LEFT_PAREN:
                    paren_cnt += 1
                elif term == Enums.SpecialCharacter.RIGHT_PAREN:
                    paren_cnt -= 1

                if paren_cnt == 0:
                    # We found the matching close parenthesis
                    expressions_inside_parens = expression[1:(i+1)]
                    expressions_outside_parens = expression[i+2:]
                    tree_inside_parens = RegExprParseTree(
                        RegExprParseTree.build_from_expression(expressions_inside_parens),
                        Enums.RegexOperation.GROUP)
                    return RegExprParseTree.handle_grouping(
                        [tree_inside_parens] + expressions_outside_parens)
        else:
            return [expression[0]] + \
                   RegExprParseTree.handle_grouping(expression[1:])

    @staticmethod
    def handle_quantifiers(expression):
        if len(expression) == 0:
            return []
        if len(expression) == 1:
            return expression

        if isinstance(expression[1], Automata.QuantifierElement):
            quant_target = RegExprParseTree(
                expression[0],
                Enums.RegexOperation.QUANTIFIER,
                expression[1])
            return RegExprParseTree.handle_quantifiers(
                [quant_target] + expression[2:])
        else:
            return [expression[0]] + \
                   RegExprParseTree.handle_quantifiers(expression[1:])

    @staticmethod
    def handle_union(expression):
        if len(expression) == 0:
            return []
        if len(expression) == 1:
            return expression

        if expression[1] == Enums.SpecialCharacter.UNION:
            union_target = RegExprParseTree(expression[0], Enums.RegexOperation.UNION, expression[2])
            return RegExprParseTree.handle_union(
                [union_target] + expression[3:])
        else:
            return [expression[0]] + \
                   RegExprParseTree.handle_union(expression[1:])

    @staticmethod
    def handle_concat(expression):
        if len(expression) == 0:
            return []
        if len(expression) == 1:
            return expression

        if expression[0] != Enums.SpecialCharacter.UNION and \
            expression[1] != Enums.SpecialCharacter.UNION:
            concat_target = RegExprParseTree(expression[0], Enums.RegexOperation.CONCAT, expression[1])
            return RegExprParseTree.handle_concat(
                [concat_target] + expression[2:])
        else:
            return [expression[0]] + \
                   RegExprParseTree.handle_concat(expression[1:])

        # concat_target = RegExprParseTree(expression[0], Enums.RegexOperation.CONCAT, expression[1])
        # return RegExprParseTree.handle_concat(
        #     [concat_target] + expression[2:])


class RegExpr:
    # An expression is a list of Element and SpecialCharacter
    def __init__(self, expression, alphabet, name=None):
        self.name = name
        assert isinstance(alphabet, Automata.Alphabet)
        for term in expression:
            assert isinstance(term, Automata.Element) or \
                   isinstance(term, Enums.SpecialCharacter) or \
                   isinstance(term, Enums.ShorthandCharacterClass)
        self.expression = expression
        self.alphabet = alphabet
        self.parse_tree = RegExprParseTree.build_from_expression(self.expression)

    def __str__(self):
        str_lst = []
        for elem in self.expression:
            if isinstance(elem.value, RegExpr):
                str_lst.append(f'({str(elem)})')
            else:
                str_lst.append(str(elem))
        return ''.join(str_lst)
    __repr__ = __str__

    @staticmethod
    def from_string(string):
        expression = []
        escape_char = '\\'
        escaped = False
        multicharacter_element = None
        for character in string:
            term_to_add = None
            if escaped:
                if multicharacter_element is not None:
                    multicharacter_element.append(character)
                    escaped = False
                    continue
                else:
                    if character == 'w':
                        term_to_add = Automata.CharClassElement(Enums.ShorthandCharacterClass.WORD)
                    elif character == 'd':
                        term_to_add = Automata.CharClassElement(Enums.ShorthandCharacterClass.DIGIT)
                    elif character == 's':
                        term_to_add = Automata.CharClassElement(Enums.ShorthandCharacterClass.WHITESPACE)
                    elif character == 'W':
                        term_to_add = Automata.CharClassElement(Enums.ShorthandCharacterClass.NEGATED_WORD)
                    elif character == 'D':
                        term_to_add = Automata.CharClassElement(Enums.ShorthandCharacterClass.NEGATED_DIGIT)
                    elif character == 'S':
                        term_to_add = Automata.CharClassElement(Enums.ShorthandCharacterClass.NEGATED_WHITESPACE)
                    elif character == 't':
                        term_to_add = Automata.EscapedCharElement(Enums.SpecialEscapedCharacter.TAB)
                    elif character == 'n':
                        term_to_add = Automata.EscapedCharElement(Enums.SpecialEscapedCharacter.NEWLINE)
                    else:
                        term_to_add = Automata.Element(character)
                    escaped = False
            elif character == escape_char:  # At this point we know we weren't preceded by an escape char
                escaped = True
                continue
            elif character == '{':
                multicharacter_element = []
                continue
            elif character == '}':
                # Check to see if this is a quantifier or a multicharacter element
                multichar_element_chars = ''.join(multicharacter_element)
                comma_separated = multichar_element_chars.split(',')
                is_quantifier = False
                if len(comma_separated) == 2:
                    is_first_num = all([c.isdigit() for c in comma_separated[0]])
                    is_second_num = all([c.isdigit() for c in comma_separated[1]])
                    if is_first_num and is_second_num and len(comma_separated[0]) > 0:
                        first_num = int(comma_separated[0])
                        if len(comma_separated[1]) == 0:
                            second_num = math.inf
                        else:
                            second_num = int(comma_separated[1])
                        assert first_num <= second_num, 'In a quantifier {a,b} a must be <= b'
                        is_quantifier = True
                        term_to_add = Automata.QuantifierElement(first_num, second_num)
                elif len(comma_separated) == 1:
                    is_first_num = all([c.isdigit() for c in comma_separated[0]])
                    if is_first_num and len(comma_separated[0]) > 0:
                        first_num = int(comma_separated[0])
                        is_quantifier = True
                        term_to_add = Automata.QuantifierElement(first_num, first_num)


                if not is_quantifier:
                    term_to_add = Automata.Element('{' + multichar_element_chars + '}')

                multicharacter_element = None
            elif multicharacter_element is not None:
                multicharacter_element.append(character)
                continue
            elif character == '(':
                term_to_add = Enums.SpecialCharacter.LEFT_PAREN
            elif character == ')':
                term_to_add = Enums.SpecialCharacter.RIGHT_PAREN
            elif character == '|':
                term_to_add = Enums.SpecialCharacter.UNION
            elif character == '*':
                term_to_add = Automata.QuantifierElement(0, math.inf)
            elif character == '+':
                term_to_add = Automata.QuantifierElement(1, math.inf)
            elif character == '?':
                term_to_add = Automata.QuantifierElement(0, 1)
            elif character == '[':
                term_to_add = Enums.SpecialCharacter.LEFT_SQUARE_BRACKET
            elif character == ']':
                term_to_add = Enums.SpecialCharacter.RIGHT_SQUARE_BRACKET
            elif character == '.':
                term_to_add = Automata.CharClassElement(Enums.ShorthandCharacterClass.DOT)
            else:
                term_to_add = Automata.Element(character)
            expression.append(term_to_add)
        elements = []
        for term in expression:
            if isinstance(term, Automata.Element):
                elements.append(term)
        return RegExpr(expression, Automata.Alphabet(elements))

    @staticmethod
    def recursive_parse_tree_to_NFA(parse_tree):
        # https://en.wikipedia.org/wiki/Thompson%27s_construction
        assert isinstance(parse_tree, RegExprParseTree)
        if parse_tree.operation == Enums.RegexOperation.IDENTITY:
            if isinstance(parse_tree.left, Automata.Element) and \
                    isinstance(parse_tree.left.value, RegExpr):
                return parse_tree.left.value.to_NFA()
            return Automata.NFAOneStartOneEnd.basis(parse_tree.left)

        # r = s|t
        if parse_tree.operation == Enums.RegexOperation.UNION:
            N_s = RegExpr.recursive_parse_tree_to_NFA(parse_tree.left)
            N_t = RegExpr.recursive_parse_tree_to_NFA(parse_tree.right)

            end_state = Automata.NFAState('f', accepting=True)
            end_transition = Automata.Transition(Automata.EmptyExpression(), end_state)
            N_s.stop.accepting = False
            N_t.stop.accepting = False
            N_s.stop.add_outgoing(end_transition)
            N_t.stop.add_outgoing(end_transition)

            N_s_start_transition = Automata.Transition(Automata.EmptyExpression(), N_s.start)
            N_t_start_transition = Automata.Transition(Automata.EmptyExpression(), N_t.start)
            start_state = Automata.NFAState('i')
            start_state.add_outgoing(N_s_start_transition)
            start_state.add_outgoing(N_t_start_transition)
            return Automata.NFAOneStartOneEnd(start_state, N_s.alphabet.union(N_t.alphabet), end_state)
        # r = st
        elif parse_tree.operation == Enums.RegexOperation.CONCAT:
            N_s = RegExpr.recursive_parse_tree_to_NFA(parse_tree.left)
            N_t = RegExpr.recursive_parse_tree_to_NFA(parse_tree.right)

            N_s.stop.accepting = False

            for transition_list in N_t.start.outgoing.values():
                for transition in transition_list:
                    N_s.stop.add_outgoing(transition)

            return Automata.NFAOneStartOneEnd(N_s.start, N_s.alphabet.union(N_t.alphabet), N_t.stop)
        elif parse_tree.operation == Enums.RegexOperation.QUANTIFIER:
            quantifier = parse_tree.right
            assert isinstance(quantifier, Automata.QuantifierElement)
            # r = s* AKA s{0,inf}
            if quantifier.start == 0 and quantifier.stop == math.inf:
                N_s = RegExpr.recursive_parse_tree_to_NFA(parse_tree.left)

                end_state = Automata.NFAState('f', accepting=True)
                end_transition = Automata.Transition(Automata.EmptyExpression(), end_state)
                N_s.stop.accepting = False
                N_s.stop.add_outgoing(end_transition)

                N_s_start_transition = Automata.Transition(Automata.EmptyExpression(), N_s.start)
                start_state = Automata.NFAState('i')
                start_state.add_outgoing(N_s_start_transition)

                skip_transition = Automata.Transition(Automata.EmptyExpression(), end_state)
                loop_transition = Automata.Transition(Automata.EmptyExpression(), N_s.start)
                start_state.add_outgoing(skip_transition)
                N_s.stop.add_outgoing(loop_transition)
                return Automata.NFAOneStartOneEnd(start_state, N_s.alphabet, end_state)
            # r = s+ AKA s{1,inf}
            elif quantifier.start == 1 and quantifier.stop == math.inf:
                N_s = RegExpr.recursive_parse_tree_to_NFA(parse_tree.left)

                end_state = Automata.NFAState('f', accepting=True)
                end_transition = Automata.Transition(Automata.EmptyExpression(), end_state)
                N_s.stop.accepting = False
                N_s.stop.add_outgoing(end_transition)

                N_s_start_transition = Automata.Transition(Automata.EmptyExpression(), N_s.start)
                start_state = Automata.NFAState('i')
                start_state.add_outgoing(N_s_start_transition)

                loop_transition = Automata.Transition(Automata.EmptyExpression(), N_s.start)
                N_s.stop.add_outgoing(loop_transition)
                return Automata.NFAOneStartOneEnd(start_state, N_s.alphabet, end_state)
            # r = s? AKA s{0,1}
            elif quantifier.start == 0 and quantifier.stop == 1:
                N_s = RegExpr.recursive_parse_tree_to_NFA(parse_tree.left)

                end_state = Automata.NFAState('f', accepting=True)
                end_transition = Automata.Transition(Automata.EmptyExpression(), end_state)
                N_s.stop.accepting = False
                N_s.stop.add_outgoing(end_transition)

                N_s_start_transition = Automata.Transition(Automata.EmptyExpression(), N_s.start)
                start_state = Automata.NFAState('i')
                start_state.add_outgoing(N_s_start_transition)

                skip_transition = Automata.Transition(Automata.EmptyExpression(), end_state)
                start_state.add_outgoing(skip_transition)
                return Automata.NFAOneStartOneEnd(start_state, N_s.alphabet, end_state)
            # r = s{1,1}
            elif quantifier.start == 1 and quantifier.stop == 1:
                return RegExpr.recursive_parse_tree_to_NFA(parse_tree.left)
            # r = s{0,m}
            elif quantifier.start == 0:
                N_s = RegExpr.recursive_parse_tree_to_NFA(parse_tree.left)
                N_s.stop.accepting = False

                N_s_0_m_minus_1 = RegExpr.recursive_parse_tree_to_NFA(
                    RegExprParseTree(
                        parse_tree.left,
                        Enums.RegexOperation.QUANTIFIER,
                        Automata.QuantifierElement(start=0, stop=quantifier.stop - 1)))
                N_s_0_m_minus_1.stop.accepting = False


                start_state = Automata.NFAState('i')
                end_state = Automata.NFAState('f', accepting=True)

                start_state.add_outgoing(Automata.Transition(Automata.EmptyExpression(), N_s_0_m_minus_1.start))
                start_state.add_outgoing(Automata.Transition(Automata.EmptyExpression(), N_s.start))
                start_state.add_outgoing(Automata.Transition(Automata.EmptyExpression(), end_state))

                N_s_0_m_minus_1.stop.add_outgoing(Automata.Transition(Automata.EmptyExpression(), N_s.start))

                N_s.stop.add_outgoing(Automata.Transition(Automata.EmptyExpression(), end_state))

                return Automata.NFAOneStartOneEnd(start_state, N_s.alphabet, end_state)
            # r = s{n,m}
            else:
                N_s = RegExpr.recursive_parse_tree_to_NFA(parse_tree.left)
                N_s.stop.accepting = False

                N_s_0_n_minus_1_m_minus_1 = RegExpr.recursive_parse_tree_to_NFA(
                    RegExprParseTree(
                        parse_tree.left,
                        Enums.RegexOperation.QUANTIFIER,
                        Automata.QuantifierElement(start=quantifier.start - 1, stop=quantifier.stop - 1)))
                N_s_0_n_minus_1_m_minus_1.stop.accepting = False


                start_state = Automata.NFAState('i')
                end_state = Automata.NFAState('f', accepting=True)

                start_state.add_outgoing(
                    Automata.Transition(Automata.EmptyExpression(), N_s_0_n_minus_1_m_minus_1.start))

                N_s_0_n_minus_1_m_minus_1.stop.add_outgoing(Automata.Transition(Automata.EmptyExpression(), N_s.start))

                N_s.stop.add_outgoing(Automata.Transition(Automata.EmptyExpression(), end_state))

                return Automata.NFAOneStartOneEnd(start_state, N_s.alphabet, end_state)
        # r = (s)
        elif parse_tree.operation == Enums.RegexOperation.GROUP:
            return RegExpr.recursive_parse_tree_to_NFA(parse_tree.left)
        else:
            raise Exception('Hey dummy you forgot to implement the graph operation for an operator')

    def to_NFA(self):
        return self.recursive_parse_tree_to_NFA(self.parse_tree)


class RegularDefinition:
    # Given an alphabet sigma of symbols d_1 to d_n, a regular definition is a sequence
    # of definitions of the form:
    #                       d_1 -> r_1
    #                       d_2 -> r_2
    #                         ...
    #                       d_n -> r_n
    # where:
    # 1. Each d_i is a new symbol now in the alphabet and not the same as any
    # other of the d's
    # 2. Each r_i is a regular expression over the alphabet sigma union {d_1, d_2, ..., d_i-1}
    # d_i is the reference to a RegExpr object
    # r_i is the regular expression represented by that d_i
    def __init__(self, regular_expressions):
        self.regular_expressions = regular_expressions
        self._verify()
        self.d_i_str_dict = dict()
        for regex in self.regular_expressions:
            if regex.name is not None:
                self.d_i_str_dict[regex.name] = regex


    def __getitem__(self, d_i_str):
        return self.d_i_str_dict.get(d_i_str)

    # Example input:
    # 'digit 0|1|2|3|4|5|6|7|8|9\n' +
    # 'digits {digit}{digit}*'
    @staticmethod
    def from_string(string):
        assert isinstance(string, str)
        regular_expressions = []
        d_i_str_to_d_i = dict()
        for line in string.strip().splitlines():
            split_on_spaces = line.strip().split(' ')
            d_i_str = f'{{{split_on_spaces[0]}}}'
            r_i_str = ' '.join(split_on_spaces[1:])
            d_i = RegExpr.from_string(r_i_str)
            d_i.name = split_on_spaces[0]
            regular_expressions.append(d_i)
            d_i_str_to_d_i[d_i_str] = d_i

        # Do another pass to replace all the regex elements with their actual representations
        for d_i in regular_expressions:
            for term in d_i.expression:
                if isinstance(term, Enums.SpecialCharacter):
                    continue
                assert isinstance(term, Automata.Element)
                d_i_str = term.value
                if d_i_sub := d_i_str_to_d_i.get(d_i_str):
                    # replace for example {digit} into the Regex that digit represents.
                    term.value = d_i_sub
                    # This parse tree should contain only single character elements because we
                    # are passing over d_i in order from least to greatest.

                    # I know the alphabet is now inaccurate but I need to update it later
                    # and I don't have enough information to do that here.

        # Let's fix up the alphabets so they fit the requirements of a RegularDefinition
        sigma = set()   # The base alphabet of all non-regex e
        for d_i in regular_expressions:
            for term in d_i.expression:
                if isinstance(term, Enums.SpecialCharacter):
                    continue
                assert isinstance(term, Automata.Element)
                if isinstance(term.value, str) and len(term.value) == 1:
                    sigma.add(term)
        sigma = Automata.Alphabet(sigma)

        d_0 = regular_expressions[0]
        d_0.alphabet = sigma
        last_alphabet = copy.deepcopy(sigma)
        assert isinstance(last_alphabet, Automata.Alphabet)
        for i in range(1, len(regular_expressions)):
            d_i = regular_expressions[i]
            d_i_minus_1 = regular_expressions[i-1]
            last_alphabet.elements.add(Automata.Element(d_i_minus_1))
            d_i.alphabet.elements = set([elem for elem in last_alphabet])

        return RegularDefinition(regular_expressions)

    def _verify(self):
        assert all([isinstance(d_i, RegExpr) for d_i in self.regular_expressions])

        # 1. Each d_i is a new symbol now in the alphabet and not the same as any
        for i in range(len(self.regular_expressions)):
            for j in range(i+1, len(self.regular_expressions)):
                assert self.regular_expressions[i] != self.regular_expressions[j]

        # 2. Each r_i is a regular expression over the alphabet sigma union {d_1, d_2, ..., d_i-1}
        sigma = self.regular_expressions[0].alphabet
        last_alphabet = copy.deepcopy(sigma)
        assert isinstance(last_alphabet, Automata.Alphabet)
        for i in range(1, len(self.regular_expressions)):
            d_i = self.regular_expressions[i]
            d_i_minus_1 = self.regular_expressions[i-1]
            assert isinstance(d_i, RegExpr)
            last_alphabet.elements.add(Automata.Element(d_i_minus_1))
            # Enforce alphabet for d_i = sigma union {d_1, d_2, ..., d_i-1}
            assert last_alphabet == d_i.alphabet

    def match(self, element_generator):
        pass


def do_stuff():
    reg_def_str = \
        r'delim [ \t\n]' + '\n' + \
        r'ws {delim}+' + '\n' + \
        r'letter a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z' + '\n' + \
        r'digit 0|1|2|3|4|5|6|7|8|9' + '\n' + \
        r'id {letter}({letter}|{digit})*' + '\n' + \
        r'number {digit}+(\.{digit}+)?(E[+-]?{digit}+)?'

    reg_def = RegularDefinition.from_string(reg_def_str)
    print(reg_def)


if __name__ == '__main__':
    do_stuff()