from enum import Enum

from Automata.Automata import Element, Alphabet


class Operation(Enum):
    CONCAT = 1
    UNION = 2
    KLEENE = 3
    GROUP = 4
    IDENTITY = 5


class SpecialCharacter(Enum):
    LEFT_PAREN = 1
    RIGHT_PAREN = 2
    UNION = 3
    KLEENE = 4
    EMPTY = 5

    def __str__(self):
        if self == SpecialCharacter.LEFT_PAREN:
            return '('
        elif self == SpecialCharacter.RIGHT_PAREN:
            return ')'
        elif self == SpecialCharacter.UNION:
            return '|'
        elif self == SpecialCharacter.KLEENE:
            return '*'
        elif self == SpecialCharacter.EMPTY:
            return 'epsilon'
        raise Exception('Hey dummy you forgot to add a string representation')
    __repr__ = __str__


class RegExprParseTree:
    def __init__(self, left, operation, right=None):
        self.left = left
        self.operation = operation
        self.right = right
        if isinstance(left, Element) and self.operation != Operation.IDENTITY:
            self.left = RegExprParseTree(left, Operation.IDENTITY)
        if isinstance(right, Element) and self.operation != Operation.IDENTITY:
            self.right = RegExprParseTree(right, Operation.IDENTITY)
        assert isinstance(operation, Operation)
        if self.operation == Operation.CONCAT:
            assert isinstance(self.left, RegExprParseTree)
            assert isinstance(self.right, RegExprParseTree)
        elif self.operation == Operation.UNION:
            assert isinstance(self.left, RegExprParseTree)
            assert isinstance(self.right, RegExprParseTree)
        elif self.operation == Operation.KLEENE:
            assert isinstance(self.left, RegExprParseTree)
        elif self.operation == Operation.GROUP:
            assert isinstance(self.left, RegExprParseTree)
        elif self.operation == Operation.IDENTITY:
            assert isinstance(self.left, Element)

    @staticmethod
    def build_from_expression(expression):
        expression = RegExprParseTree.handle_identity(expression)
        expression = RegExprParseTree.handle_grouping(expression)
        expression = RegExprParseTree.handle_kleene(expression)
        expression = RegExprParseTree.handle_union(expression)
        expression = RegExprParseTree.handle_concat(expression)

        if len(expression) != 1:
            raise Exception('Something went wrong when generating the regex '
                            'parse tree')
        else:
            return expression[0]

    @staticmethod
    def handle_identity(expression):
        new_expression = []
        for term in expression:
            if isinstance(term, Element):
                new_expression.append(RegExprParseTree(term, Operation.IDENTITY))
            else:
                new_expression.append(term)
        return new_expression

    @staticmethod
    def handle_grouping(expression):
        if len(expression) == 0:
            return []
        if len(expression) == 1:
            return expression

        if expression[0] == SpecialCharacter.LEFT_PAREN:
            # Search for the matching close parenthesis and recursively build a tree
            paren_cnt = 1
            for i, term in enumerate(expression[1:]):
                if term == SpecialCharacter.LEFT_PAREN:
                    paren_cnt += 1
                elif term == SpecialCharacter.RIGHT_PAREN:
                    paren_cnt -= 1

                if paren_cnt == 0:
                    # We found the matching close parenthesis
                    expr_inside_parens = expression[1:(i+1)]
                    expr_outside_parens = expression[i+2:]
                    tree_inside_parens = RegExprParseTree(
                        RegExprParseTree.build_from_expression(expr_inside_parens),
                        Operation.GROUP)
                    return RegExprParseTree.handle_grouping(
                        [tree_inside_parens] + expr_outside_parens)
        else:
            return [expression[0]] + \
                   RegExprParseTree.handle_grouping(expression[1:])

    @staticmethod
    def handle_kleene(expression):
        if len(expression) == 0:
            return []
        if len(expression) == 1:
            return expression

        if expression[1] == SpecialCharacter.KLEENE:
            kleene_target = RegExprParseTree(
                expression[0],
                Operation.KLEENE)
            return RegExprParseTree.handle_kleene(
                [kleene_target] + expression[2:])
        else:
            return [expression[0]] + \
                   RegExprParseTree.handle_kleene(expression[1:])

    @staticmethod
    def handle_union(expression):
        if len(expression) == 0:
            return []
        if len(expression) == 1:
            return expression

        if expression[1] == SpecialCharacter.UNION:
            union_target = RegExprParseTree(expression[0], Operation.UNION, expression[2])
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

        concat_target = RegExprParseTree(expression[0], Operation.CONCAT, expression[1])
        return RegExprParseTree.handle_concat(
            [concat_target] + expression[2:])




class RegExpr:
    # An expression is a list of Element and SpecialCharacter
    def __init__(self, expression, alphabet):
        assert isinstance(alphabet, Alphabet)
        for term in expression:
            assert isinstance(term, Element) or isinstance(term, SpecialCharacter)
        self.expression = expression
        self.alphabet = alphabet
        self.parse_tree = RegExprParseTree.build_from_expression(self.expression)

    @staticmethod
    def from_string(string):
        expression = []
        for character in string:
            term_to_add = None
            if character == '(':
                term_to_add = SpecialCharacter.LEFT_PAREN
            elif character == ')':
                term_to_add = SpecialCharacter.RIGHT_PAREN
            elif character == '|':
                term_to_add = SpecialCharacter.UNION
            elif character == '*':
                term_to_add = SpecialCharacter.KLEENE
            else:
                term_to_add = Element(character)
            expression.append(term_to_add)
        elements = []
        for term in expression:
            if isinstance(term, Element):
                elements.append(term)
        return RegExpr(expression, Alphabet(elements))


def do_stuff():
    expr = RegExpr.from_string('(a|b)*abb')
    print(expr.parse_tree)


if __name__ == '__main__':
    do_stuff()