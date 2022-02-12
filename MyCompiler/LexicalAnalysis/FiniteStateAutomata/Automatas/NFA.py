from AutomataOperationUtility import AutomataOperationUtility
from BaseAutomata import BaseAutomata
from DFA import DFA
from Elements import BaseElement
from States import DFAState
from Transition import Transition


class NFA(BaseAutomata):
    def to_DFA(self):
        Dtran = dict()
        # intially e-closure(s_0) is the only state in Dstates
        start_dstate = frozenset(AutomataOperationUtility.epsilon_closure(self.start))
        Dstates = {start_dstate}
        marked_states = set()
        while True:
            # while there is an unmarked state T in Dstates
            unmarked_states = Dstates.difference(marked_states)
            if len(unmarked_states) == 0:
                break
            T = unmarked_states.pop()
            # mark T
            marked_states.add(T)
            # for each input symbol a
            for a in self.alphabet:
                assert isinstance(a, BaseElement)
                U = frozenset(
                    AutomataOperationUtility.epsilon_closure(
                        AutomataOperationUtility.move(T, a)))
                if U not in Dstates:
                    Dstates.add(U)
                Dtran[(T, a)] = U

        count = 0
        DFA_states = dict()
        for dstate in Dstates:
            ID = count
            count += 1
            accepting = any([state.accepting for state in dstate])
            outgoing = None # We need to build all states before doing this
            DFA_states[dstate] = DFAState(accepting=accepting, outgoing=outgoing, ID=ID)

        # 2nd pass to add transitions based on Dtran
        for dstate in Dstates:
            DFA_state = DFA_states[dstate]
            for element in self.alphabet:
                target_dstate = Dtran[(dstate, element)]
                target_DFA_state = DFA_states[target_dstate]
                DFA_state.add_outgoing(Transition(element, target_DFA_state))

        start_DFA_state = DFA_states[start_dstate]
        return DFA(start_DFA_state, self.alphabet)
