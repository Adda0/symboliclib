"""
ST - Symbolic Transducer class
"""
from __future__ import print_function

from symbolic import Symbolic
import itertools


class ST(Symbolic):
    """
    Finite automaton class
    """
    def __init__(self):
        self.alphabet = set()
        self.states = set()
        self.start = set()
        self.final = set()
        self.transitions = {}
        # sign whether automaton is deterministic
        self.deterministic = None
        # reversed variant of the automaton
        self.reversed = None
        self.automaton_type = "INT"
        self.has_epsilon = None
        self.epsilon_Free = None

    def is_deterministic(self):
        """
        Checks if the automaton is deterministic
        sets the deterministic attribute
        :return: bool
        """
        if len(self.start) > 1:
            return False
        if self.deterministic is not None:
            # the deterministic attribute is already set, no need to check again
            return self.deterministic
        for trans_group in self.transitions:
            for trans_label in self.transitions[trans_group]:
                if len(self.transitions[trans_group][trans_label]) > 1:
                    # possible to pass through one label to multiple states
                    # automaton is non-deterministic
                    self.deterministic = False
                    return False
                if not trans_label.identity and len(trans_label.output.symbols):
                    self.deterministic = False
                    return False
                for trans_label2 in self.transitions[trans_group]:
                    if trans_label != trans_label2:
                        # test conjunction of each pair of labels
                        con = trans_label.input.conjunction(trans_label2.input)
                        if con.is_satisfiable():
                            # if the conjunction is satisfiable, automaton is non-deterministic
                            self.deterministic = False
                            return False

        # if no contradiction has been found, automaton is deterministic
        self.deterministic = True
        return True

    def composition(self, other):
        if self.automaton_type != other.automaton_type:
            return False

        comp = self.get_new()
        comp.alphabet = self.alphabet.intersection(other.alphabet)
        comp.reversed = None

        """start1 = self.start.copy().pop()
        start2 = other.start.copy().pop()
        first = str(start1) + "," + str(start2)
        comp.start = set()
        comp.start.add(first)
        queue = [first]"""

        queue = list(itertools.product(self.start, other.start))
        comp.start = set()
        for q in queue:
            comp.start.add("[" + q[0] + "_1|" + q[1] + "_2]")

        while len(queue) > 0:
            combined = queue.pop()
            state1 = combined[0]
            state2 = combined[1]
            combined_str = "[" + state1 + "_1|" + state2 + "_2]"

            if combined_str not in comp.transitions:
                comp.transitions[combined_str] = {}

            if state1 in self.final or state2 in other.final:
                comp.final.add(combined_str)

            if state1 in self.transitions and state2 in other.transitions:
                for label in self.transitions[state1]:
                    for label2 in other.transitions[state2]:
                        common = label.output.conjunction(label2.input)
                        if common and common.is_satisfiable():
                            new_label = label.combine(label2)
                            if new_label and new_label.is_satisfiable():
                                endstate = (self.transitions[state1][label][0], other.transitions[state2][label][0])
                                endstate_str = "[" + endstate[0] + "_1|" + endstate[1] + "_2]"

                                if new_label not in comp.transitions[combined]:
                                    comp.transitions[combined][new_label] = [endstate_str]
                                else:
                                    comp.transitions[combined][new_label].append(endstate_str)

                                if endstate not in queue and endstate_str not in comp.states:
                                    queue.append(endstate)

        comp.simple_reduce()
        #comp.remove_commas_from_states()

        return comp

    def check_translation(self, word, word2, state=None):
        # @TODO pre viac zaciatocnych stavov
        if len(word) == 0 and len(word2) == 0 and state in self.final:
            return True

        if len(word) != len(word2):
            return False

        if not state:
            state = self.start.copy().pop()

        if not state in self.transitions:
            return False
        for label in self.transitions[state]:
            if label.translates(word[0], word2[0]):
                for endstate in self.transitions[state][label]:
                    if self.check_translation(word[1:], word2[1:], endstate):
                        return True

        return False

    def translate_word(self, word, state=None):
        # @TODO pre viac zaciatocnych stavov
        if len(word) == 0:
            if state and state in self.final:
                return "a"
            else:
                return False

        first = False

        if not state:
            first = True
            state = self.start.copy().pop()

        if state not in self.transitions:
            return False
        for label in self.transitions[state]:
            if label.input.has_letter(word[0]):
                translation = label.translate(word[0], self.alphabet)
                for endstate in self.transitions[state][label]:
                    add = self.translate_word(word[1:], endstate)
                    if add:
                        if first:
                            return (translation + add)[:-1]
                        else:
                            return translation + add

        return False

    @staticmethod
    def get_new():
        return ST()
