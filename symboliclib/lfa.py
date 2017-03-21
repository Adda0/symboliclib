"""
LFA - Letter Finite Automaton class
"""
from __future__ import print_function
from sa import SA
from copy import deepcopy
import itertools


class LFA(SA):
    """
    Finite automaton class
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

    @staticmethod
    def get_new():
        return LFA()

    def is_deterministic(self):
        """Checks if the automaton is deterministic
        sets the deterministic attribute
        Returns True or False
        """
        if self.deterministic is not None:
            # the deterministic attribute is already set, no need to check again
            return self.deterministic

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
        """Intersection
        Returns intersection
        """
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
                        endstate = (self.transitions[state1][label][0], a2.transitions[state2][label][0])
                        endstate_str = "[" + endstate[0] + "_1|" + endstate[1] + "_2]"

                        if label not in intersect.transitions[combined_str]:
                            intersect.transitions[combined_str][label] = [endstate_str]
                        else:
                            intersect.transitions[combined_str][label].append(endstate_str)

                        if endstate not in queue and endstate_str not in intersect.states:
                            queue.append(endstate)

        intersect.simple_reduce()

        return intersect

    def simulations(self):
        self.get_complete()
        self.print_automaton()

        self.reverse()
        rever_trans = self.reversed.transitions

        card = {}

        for state in self.states:
            for a in self.alphabet:
                if state in self.transitions and a in self.transitions[state]:
                    card[(state, a)] = len(self.transitions[state][a])
                else:
                    card[(state, a)] = 0

        result = set()
        c = []

        for final_state in self.final:
            for state in self.states - self.final:
                result.add((final_state, state))
                c.append((final_state, state))

        N = {}

        while len(c):
            item = c.pop()
            i = item[0]
            j = item[1]
            for a in self.alphabet:
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

        simulations = []
        q = self.states
        while len(q):
            state = q.pop()
            for state2 in q:
                if state != state2:
                    if (state, state2) not in result and (state2, state) not in result:
                        simulations.append((state, state2))

        print(simulations)

        return result

    def is_inclusion(self, other):
        self.determinize(True)
        self.determinized.get_complete()
        other.determinize(True)
        other.determinized.get_complete()

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
        Converts automaton to language equal complete automaton
        """
        # @TODO bleh. Nejako vytvárať nové lettery odtiaľto.
        label_prototype = list(self.transitions[list(self.transitions.keys())[0]].keys())[0]
        # create one nonterminating state
        self.states.add("qsink")
        # for transitions from each state
        for state in deepcopy(self.states):
            if state in self.transitions:
                labels = list(self.transitions[state].keys())
            else:
                labels = []
                self.transitions[state] = {}
            for a in self.alphabet:
                if a not in labels:
                    new_label = label_prototype.create(a)
                    self.transitions[state][new_label] = ["qsink"]

            for label in labels:
                # rename all nonterminating states to "qsink"
                endstates = self.transitions[state][label]
                for endstate in endstates:
                    if self.is_useless(endstate):
                        self.transitions[state][label].remove(endstate)
                        if "qsink" not in self.transitions[state][label]:
                            self.transitions[state][label].append("qsink")