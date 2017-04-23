"""
ST - Symbolic Transducer class

represents symbolic transducer
"""
from __future__ import print_function

from symbolic import Symbolic
import itertools


class ST(Symbolic):
    """
    Symbolic transducer class

    Attributes:
        -- classic transducer attributes:
        alphabet        set of symbols
        states          set of states
        start           set of initial states
        final           set of final states
        transitions     dictionary of transitions
        automaton_type  type of transducer - here INT (In/Not_in Transducer)

        -- information about transducer:
        deterministic   flag whether transducer is deterministic
        is_epsilon_free flag whether transducer is epsilon free
        label           class instance of label used in transducer

        -- attributes used for optimisation:
        reversed        reversed version of transducer
        epsilon_free    epsilon free version of transducer

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
        self.is_epsilon_free = None
        self.epsilon_free = None
        self.label = None

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
        """
        Performs composition of two transducers
        :param other: the second automaton
        :return: transducer created by composition
        """
        if self.automaton_type != other.automaton_type:
            return False

        comp = self.get_new()
        comp.alphabet = self.alphabet.intersection(other.alphabet)
        comp.reversed = None

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

            if combined_str not in comp.states:
                comp.states.add(combined_str)

            if state1 in self.final or state2 in other.final:
                comp.final.add(combined_str)

            if state1 in self.transitions and state2 in other.transitions:
                for label in self.transitions[state1]:
                    for label2 in other.transitions[state2]:
                        common = label.output.conjunction(label2.input)
                        if common and common.is_satisfiable():
                            new_label = label.combine(label2)
                            if new_label and new_label.is_satisfiable():
                                for end in self.transitions[state1][label]:
                                    for end2 in other.transitions[state2][label2]:
                                        endstate = (end, end2)
                                        endstate_str = "[" + endstate[0] + "_1|" + endstate[1] + "_2]"

                                        if new_label not in comp.transitions[combined_str]:
                                            comp.transitions[combined_str][new_label] = [endstate_str]
                                        else:
                                            comp.transitions[combined_str][new_label].append(endstate_str)

                                        if endstate not in queue and endstate_str not in comp.states:
                                            queue.append(endstate)

        comp = comp.simple_reduce()

        return comp

    def run_on_nfa(self, nfa):
        """
        Applies transducer on given automaton
        :param nfa: finite automaton
        :return: finite automaton created by application of trnasucer
        """
        if not self.alphabet.intersection(nfa.alphabet):
            return False

        new_nfa = nfa.get_new()
        new_nfa.alphabet = self.alphabet
        new_nfa.reversed = None

        queue = list(itertools.product(self.start, nfa.start))
        new_nfa.start = set()
        for q in queue:
            new_nfa.start.add("[" + q[0] + "_1|" + q[1] + "_2]")

        while len(queue) > 0:
            combined = queue.pop()
            state1 = combined[0]
            state2 = combined[1]
            combined_str = "[" + state1 + "_1|" + state2 + "_2]"

            if combined_str not in new_nfa.transitions:
                new_nfa.transitions[combined_str] = {}

            if combined_str not in new_nfa.states:
                new_nfa.states.add(combined_str)

            if state1 in self.final and state2 in nfa.final:
                new_nfa.final.add(combined_str)
            if state1 in self.transitions and state2 in nfa.transitions:
                for label in self.transitions[state1]:
                    for label2 in nfa.transitions[state2]:
                        common = label.input.conjunction(label2)
                        if common and common.is_satisfiable():
                            new_label = label.output
                            if label.identity:
                                new_label = label.output.conjunction(label2)
                            if new_label and new_label.is_satisfiable():
                                for end in self.transitions[state1][label]:
                                    for end2 in nfa.transitions[state2][label2]:
                                        endstate = (end, end2)
                                        endstate_str = "[" + endstate[0] + "_1|" + endstate[1] + "_2]"

                                        if new_label not in new_nfa.transitions[combined_str]:
                                            new_nfa.transitions[combined_str][new_label] = [endstate_str]
                                        else:
                                            new_nfa.transitions[combined_str][new_label].append(endstate_str)

                                        if endstate not in queue and endstate_str not in new_nfa.states:
                                            queue.append(endstate)

        new_nfa = new_nfa.simple_reduce()

        return new_nfa

    def check_translation(self, word, word2, state=None):
        """
        Checks if word translates to word2 in the transducer
        !! does not work with multiple initial states
        :param word: the input word
        :param word2: the output word
        :param state: initial state of checking
        :return: bool
        """
        if len(word) == 0 and len(word2) == 0 and state in self.final:
            return True

        if len(word) != len(word2):
            return False

        if not state:
            state = self.start.copy().pop()

        if state not in self.transitions:
            return False
        for label in self.transitions[state]:
            if label.translates(word[0], word2[0]):
                for endstate in self.transitions[state][label]:
                    if self.check_translation(word[1:], word2[1:], endstate):
                        return True

        return False

    def translate_word(self, word, state=None):
        """
        Generates random translation of given word if possible
        !! does not work with multiple initial states
        :param word: the input word
        :param state: initial state of translation
        :return: output word or False if translation not possible
        """
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
        """
        Creates and returns new empty object of class
        :return: empty object ST
        """
        return ST()
