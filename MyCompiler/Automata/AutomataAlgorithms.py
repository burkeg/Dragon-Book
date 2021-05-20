from Automata import *
from RegExpr import *

def RegExpr_to_NFA(regexpr):
    # https://en.wikipedia.org/wiki/Thompson%27s_construction
    assert isinstance(regexpr, RegExpr)

    def recursive_parse_tree_to_NFA(parse_tree):
        assert isinstance(parse_tree, RegExprParseTree)
        if parse_tree.operation == Operation.IDENTITY:
            return NFAOneStartOneEnd.basis(parse_tree.left)

        # r = s|t
        if parse_tree.operation == Operation.UNION:
            N_s = recursive_parse_tree_to_NFA(parse_tree.left)
            N_t = recursive_parse_tree_to_NFA(parse_tree.right)

            end_state = NFAState('f', accepting=True)
            end_transition = Transition(EmptyExpression, end_state)
            N_s.stop.accepting = False
            N_t.stop.accepting = False
            N_s.stop.add_outgoing(end_transition)
            N_t.stop.add_outgoing(end_transition)

            N_s_start_transition = Transition(EmptyExpression, N_s.start)
            N_t_start_transition = Transition(EmptyExpression, N_t.start)
            start_state = NFAState('i')
            start_state.add_outgoing(N_s_start_transition)
            start_state.add_outgoing(N_t_start_transition)
            return NFAOneStartOneEnd(start_state, N_s.alphabet.union(N_t.alphabet), end_state)
        # r = st
        elif parse_tree.operation == Operation.CONCAT:
            N_s = recursive_parse_tree_to_NFA(parse_tree.left)
            N_t = recursive_parse_tree_to_NFA(parse_tree.right)

            N_s.stop.accepting = False

            for transition_list in N_t.start.outgoing.values():
                for transition in transition_list:
                    N_s.stop.add_outgoing(transition)

            return NFAOneStartOneEnd(N_s.start, N_s.alphabet.union(N_t.alphabet), N_t.stop)
        # r = s*
        elif parse_tree.operation == Operation.KLEENE:
            N_s = recursive_parse_tree_to_NFA(parse_tree.left)

            end_state = NFAState('f', accepting=True)
            end_transition = Transition(EmptyExpression, end_state)
            N_s.stop.accepting = False
            N_s.stop.add_outgoing(end_transition)

            N_s_start_transition = Transition(EmptyExpression, N_s.start)
            start_state = NFAState('i')
            start_state.add_outgoing(N_s_start_transition)

            skip_transition = Transition(EmptyExpression, end_state)
            loop_transition = Transition(EmptyExpression, N_s.start)
            start_state.add_outgoing(skip_transition)
            N_s.stop.add_outgoing(loop_transition)
            return NFAOneStartOneEnd(start_state, N_s.alphabet, end_state)
        # r = (s)
        elif parse_tree.operation == Operation.GROUP:
            return recursive_parse_tree_to_NFA(parse_tree.left)

    return recursive_parse_tree_to_NFA(regexpr.parse_tree)

def do_stuff():
    expr = RegExpr.from_string('(a|b)*a')
    nfa = RegExpr_to_NFA(expr)
    nfa.relabel()
    print(nfa)


if __name__ == '__main__':
    do_stuff()
