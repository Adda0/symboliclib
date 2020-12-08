"""
LFA - Letter Finite Automaton class

represents classic finite automaton

Copyright (c) 2017  Michaela Bielikova <xbieli06@stud.fit.vutbr.cz>
"""
from __future__ import print_function
from sa import SA
from copy import deepcopy
import itertools


class LFA(SA):
    """
    Classic finite automaton class

    Attributes:
        -- classic automaton attributes:
        alphabet        set of symbols
        states          set of states
        start           set of initial states
        final           set of final states
        transitions     dictionary of transitions
        automaton_type  type of automaton - here LFA (Letter Finite Automaton)

        -- information about automaton:
        deterministic   flag whether automaton is deterministic
        is_epsilon_free flag whether automaton is epsilon free
        label           class instance of label used in automaton

        -- attributes used for optimisation:
        reversed        reversed version of automaton
        determinized    determinized version of automaton
        epsilon_free    epsilon free version of automaton

    """
    def __init__(self):
        self.alphabet = set()
        self.states = set()
        self.start = set()
        self.final = set()
        self.transitions = {}
        self.deterministic = None
        self.determinized = None
        self.reversed = None
        self.automaton_type = "LFA"
        self.label = None
        self.is_epsilon_free = None
        self.epsilon_free = None

    @staticmethod
    def get_new():
        """
        Creates and returns new empty object of class
        :return: empty object LFA
        """
        return LFA()

    def is_deterministic(self):
        """
        Checks if the automaton is deterministic
        sets the deterministic attribute
        :return: bool
        """
        # automaton with more than one start state is nondeterministic
        if len(self.start) > 1:
            self.deterministic = False
            return False

        for trans_group in self.transitions:
            for trans_label in self.transitions[trans_group]:
                if len(self.transitions[trans_group][trans_label]) > 1:
                    # possible to pass through one label in multiple states
                    # automaton is not deterministic
                    self.deterministic = False
                    return False

        # if no contradiction has been found, automaton is deterministic
        self.deterministic = True
        return True

    def intersection(self, a2):
        """
        Performs intersection of two automata
        :param a2: the second automaton
        :return: automaton created by intersection
        """
        #self.print_automaton()
        #a2.print_automaton()
        intersect = self.get_new()
        intersect.alphabet = self.alphabet.intersection(a2.alphabet)
        intersect.reversed = None

        queue = list(itertools.product(self.start, a2.start))
        intersect.start = set()
        for q in queue:
            intersect.start.add("[" + q[0] + "_1|" + q[1] + "_2]")

        while len(queue) > 0:
            combined = queue.pop()
            state1 = combined[0]
            state2 = combined[1]
            combined_str = "[" + state1 + "_1|" + state2 + "_2]"
            intersect.states.add(combined_str)
            if combined_str not in intersect.transitions:
                intersect.transitions[combined_str] = {}

            if state1 in self.final and state2 in a2.final:
                intersect.final.add(combined_str)

            if state1 in self.transitions and state2 in a2.transitions:
                for label in self.transitions[state1]:
                    if label in a2.transitions[state2]:
                        endstates = itertools.product(self.transitions[state1][label], a2.transitions[state2][label])
                        for endstate in endstates:
                            endstate_str = "[" + endstate[0] + "_1|" + endstate[1] + "_2]"

                            if label not in intersect.transitions[combined_str]:
                                intersect.transitions[combined_str][label] = [endstate_str]
                            else:
                                intersect.transitions[combined_str][label].append(endstate_str)

                            if endstate not in queue and endstate_str not in intersect.states:
                                queue.append(endstate)

        intersect = intersect.simple_reduce()
        return intersect

    def simple_reduce(self):
        """
        Reduces automaton by removing unreachable and useless states
        :return: reduced automaton
        """
        result = deepcopy(self)
        # first remove deadend transitions
        result = result.remove_useless()
        # then remove unreachable transitions
        result = result.remove_unreachable()

        return result

    def simulations_preorder(self):
        """
        Computes simulation_preorder relation
        :return: pairs of states that simulate each other
        """
        complete = self.get_complete()

        complete.reverse()
        rever_trans = complete.reversed.transitions

        card = {}

        for state in complete.states:
            for a in complete.alphabet:
                if state in complete.transitions and a in complete.transitions[state]:
                    card[(state, a)] = len(complete.transitions[state][a])
                else:
                    card[(state, a)] = 0

        result = set()
        c = []

        for final_state in complete.final:
            for state in complete.states - complete.final:
                result.add((final_state, state))
                c.append((final_state, state))

        N = {}

        while len(c):
            item = c.pop()
            i = item[0]
            j = item[1]
            for a in complete.alphabet:
                if j in rever_trans and a in rever_trans[j]:
                    for k in rever_trans[j][a]:
                        if a in N:
                            if (i, k) in N[a]:
                                N[a][(i, k)] += 1
                            else:
                                N[a][(i, k)] = 1
                        else:
                            N[a] = {}
                            N[a][(i, k)] = 1
                        if (k, a) in card:
                            if N[a][(i, k)] == card[(k, a)]:
                                if i in rever_trans and a in rever_trans[i]:
                                    for l in rever_trans[i][a]:
                                        if (l, k) not in result:
                                            result.add((l, k))
                                            c.append((l, k))

        # get pairs of states that simulate each other
        simulations = []
        q = complete.states.copy()
        while len(q):
            state = q.pop()
            for state2 in q:
                if state != state2:
                    if (state, state2) not in result:
                        simulations.append((state, state2))

        for state in complete.states:
            simulations.append((state, state))

        return simulations

    def is_included(self, other):
        """
        Checks whether automaton is included in the other one:
        self <= other ?
        :param other: other automaton
        :return: bool
        """
        self.determinize()
        self.determinized = self.determinized.get_complete()
        other.determinize()
        other.determinized = other.determinized.get_complete()

        queue = list(itertools.product(self.determinized.start, other.determinized.start))
        checked = []

        while len(queue) > 0:
            pair = queue.pop()
            q1 = pair[0]
            q2 = pair[1]
            checked.append(pair)
            if q1 in self.determinized.final and q2 not in other.determinized.final:
                return False
            for a in self.determinized.alphabet.union(other.determinized.alphabet):
                if q1 in self.determinized.transitions and a in self.determinized.transitions[q1]:
                    q1_new = self.determinized.transitions[q1][a][0]
                else:
                    q1_new = ""
                if q2 in other.determinized.transitions and a in other.determinized.transitions[q2]:
                    q2_new = other.determinized.transitions[q2][a][0]
                else:
                    q2_new = ""

                if q1_new != "" or q2_new != "":
                    if (q1_new, q2_new) not in checked and (q1_new, q2_new) not in queue:
                        queue.append((q1_new, q2_new))

        return True

    def get_complete(self):
        """
        Converts automaton into language equivalent complete automaton
        :return: complete automaton
        """
        complete = deepcopy(self)
        # create one nonterminating state
        complete.states.add("qsink")
        # for transitions from each state
        for state in deepcopy(complete.states):
            if state in complete.transitions:
                labels = list(complete.transitions[state].keys())
            else:
                labels = []
                complete.transitions[state] = {}
            for a in complete.alphabet:
                if a not in labels:
                    new_label = complete.label.create(a)
                    complete.transitions[state][new_label] = ["qsink"]

            for label in labels:
                # rename all nonterminating states to "qsink"
                endstates = complete.transitions[state][label]
                for endstate in endstates:
                    if complete.is_useless(endstate):
                        complete.transitions[state][label].remove(endstate)
                        if "qsink" not in complete.transitions[state][label]:
                            complete.transitions[state][label].append("qsink")

        return complete

    def get_deterministic_transitions(self, state_group):
        """
        Returns deterministic transitions from a given state
        :param state_group: comma separated set of states
        :return: deterministic transitions
        """
        new_transitions = {}

        for state in state_group.split(","):
            if state not in self.transitions:
                continue

            for a in self.transitions[state]:
                if a in new_transitions:
                    # if label already exists, unite endstates
                    existing_transitions = set(",".join(new_transitions[a]).split(","))
                    new_transitions[a] = [",".join(sorted(existing_transitions.union(set(self.transitions[state][a]))))]
                else:
                    new_transitions[a] = [",".join(sorted(self.transitions[state][a]))]

        return new_transitions

    def determinize_simulations(self):
        """
        Converts automaton into a deterministic one
        uses simulations optimisation
        :return: determinised automaton
        """
        # automaton is already deterministic
        if self.deterministic:
            self.determinized = deepcopy(self)
            return deepcopy(self)

        if self.determinized is not None and self.determinized.is_deterministic():
            return deepcopy(self.determinized)

        det = self.get_new()
        det.start = set()
        det.label = self.label
        det.start.add(",".join(self.start))

        det.alphabet = self.alphabet.copy()

        queue = set()
        queue.add(",".join(self.start))
        simulations = self.simulations_preorder()

        checked = []
        while len(queue) > 0:
            state = queue.pop()
            checked.append(state)
            det.states.add(state)
            # add final states
            for old_state in state.split(","):
                if old_state in self.final:
                    det.final.add(state)

            new_trans = self.get_deterministic_transitions_optim(state, simulations)
            det.transitions[state] = new_trans
            for label in new_trans:
                for endstate in new_trans[label]:
                    if endstate not in queue and endstate not in checked:
                        queue.add(endstate)

        det = det.simple_reduce()
        det.is_deterministic()

        self.determinized = det

        return det

    def get_deterministic_transitions_optim(self, state_group, simulations):
        """
        Returns deterministic transitions from a given state
        :param state_group: comma separated set of states
        :return: deterministic transitions
        """
        new_transitions = {}

        for state in state_group.split(","):
            if state not in self.transitions:
                continue

            for a in self.transitions[state]:
                if a in new_transitions:
                    # if label already exists, unite endstates
                    existing_transitions = set(",".join(new_transitions[a]).split(","))

                    minimal_states = self.minim_antichain(existing_transitions.union(set(self.transitions[state][a])), simulations)
                    new_transitions[a] = [",".join(sorted(minimal_states))]
                else:

                    new_transitions[a] = [",".join(sorted(self.minim_antichain(self.transitions[state][a], simulations)))]

        return new_transitions

    def post_antichain(self, other, pair):
        """
        Computes post relation for antichain algorithm
        :param other: other automaton
        :param pair: pair of states (p,Q), p is a state from self, Q is a superstate from other
        :return: post relation
        """
        result = []

        if pair[0] in self.transitions:
            for a in self.transitions[pair[0]]:
                new_qs = set()
                new_superstates = set()
                new_qs = new_qs.union(self.transitions[pair[0]][a])
                for superset_state in pair[1]:
                    if superset_state in other.transitions and a in other.transitions[superset_state]:
                        new_superstates = new_superstates.union(other.transitions[superset_state][a])
                if new_qs and new_superstates:
                    for q in new_qs:
                        result.append((q, new_superstates))

        return result

    def unify_transition_symbols(self):
        """
        Substitute every transition symbol with '*'.
        """

        new_transitions = {}

        for from_state, transition_set in self.transitions.items():
            for symbol, end_state in self.transitions[from_state].items():
                if from_state not in new_transitions:
                    new_transitions[from_state] = {'*': end_state}
                else:
                    new_transitions[from_state]['*'] += end_state

        self.transitions = new_transitions

    def count_formulas_for_lfa(self):
        """
        Computes formulas for the LFA for accepted strings.
        :return: dictionary of formulas for the LFA accept states
        """
        def get_next_state():
            nonlocal curr_state
            nonlocal length
            curr_state = {self.transitions.get(next(iter(curr_state))).get('*')[0]}
            length += 1


        curr_state = self.start
        length = 0
        formulas_for_states = {}
        last_state_to_stop = ''

        while True:
            if not curr_state.issubset(self.final):
                get_next_state()
                curr_state_iter = next(iter(curr_state))
            else:  # the current state is also an accept state
                try:
                    if not formulas_for_states[curr_state_iter][0]:
                        formulas_for_states[curr_state_iter][0] = True
                        formulas_for_states[curr_state_iter][1] += ' + ' + str(length - int(formulas_for_states[curr_state_iter][1])) + 'k'
                    if last_state_to_stop == curr_state_iter:
                        break
                except KeyError:
                    formulas_for_states[curr_state_iter] = [False, str(length)]
                    last_state_to_stop = curr_state_iter

                get_next_state()

        return formulas_for_states
