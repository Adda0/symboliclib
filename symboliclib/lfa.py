"""
LFA - Letter Finite Automaton class
"""
from __future__ import print_function
from sa import SA
from copy import deepcopy


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

        start1 = self.start.copy().pop()
        start2 = a2.start.copy().pop()
        first = str(start1) + "," + str(start2)
        intersect.start = set()
        intersect.start.add(first)
        queue = [first]

        while len(queue) > 0:
            combined = queue.pop()
            intersect.states.add(combined)
            if combined not in intersect.transitions:
                intersect.transitions[combined] = {}
            states = combined.split(",")
            state1 = states[0]
            state2 = states[1]

            if state1 in self.final and state2 in a2.final:
                intersect.final.add(combined)

            for label in self.transitions[state1]:
                if label in a2.transitions[state2]:
                    endstate = self.transitions[state1][label][0] + "," + a2.transitions[state2][label][0]

                    if label not in intersect.transitions[combined]:
                        intersect.transitions[combined][label] = [endstate]
                    else:
                        intersect.transitions[combined][label].append(endstate)

                    if endstate not in queue and endstate not in intersect.states:
                        queue.append(endstate)

        return intersect

    def simulations(self):
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

        """simulations = []
        q = self.states
        while len(q):
            state = q.pop()
            for state2 in q:
                if state != state2:
                    if (state, state2) not in result and (state2, state) not in result:
                        simulations.append((state, state2))"""

        return result

    def is_inclusion(self, other):
        self.determinize(True)
        self.determinized.get_complete()
        other.determinize(True)
        other.determinized.get_complete()
        self.determinized.print_automaton()
        other.determinized.print_automaton()

        queue = [(self.determinized.start.pop(), other.determinized.start.pop())]
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
        if not self.deterministic:
            self.determinize()
        # create one nonterminating state
        self.states.add("error")
        # for transitions from each state
        for state in deepcopy(self.transitions):
            labels = list(self.transitions[state].keys())
            for a in self.alphabet:
                if a not in labels:
                    new_label = labels[0].create(a)
                    self.transitions[state][new_label] = ["error"]

            for label in labels:
                # rename all error states to "error"
                endstates = self.transitions[state][label]
                for endstate in endstates:
                    if self.is_useless(endstate):
                        self.transitions[state][label].remove(endstate)
                        if "error" not in self.transitions[state][label]:
                            self.transitions[state][label].append("error")

            self.simple_reduce()
