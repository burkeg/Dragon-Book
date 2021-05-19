from AutomataStructure import *
from RegExpr import *

def RegExpr_to_NFA(regexpr):
    # https://en.wikipedia.org/wiki/Thompson%27s_construction
    assert isinstance(regexpr, RegExpr)
