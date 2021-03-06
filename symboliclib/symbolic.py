"""
Symbolic class

used for implementation od method that are the same for automata and transducers

Copyright (c) 2017  Michaela Bielikova <xbieli06@stud.fit.vutbr.cz>
"""
from __future__ import print_function
import itertools
from copy import deepcopy


class Symbolic(object):
    """
    Symbolic class

    Attributes:
        -- classic automaton attributes:
        alphabet        set of symbols
        states          set of states
        start           set of initial states
        final           set of final states
        transitions     dictionary of transitions
        automaton_type  type of automaton - here SA (Symbolic Automaton)

        -- information about automaton:
        deterministic   flag whether automaton is deterministic
        is_epsilon_free flag whether automaton is epsilon free

        -- attributes used for optimisation:
        reversed        reversed version of automaton
        epsilon_free    epsilon free version of automaton

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
        self.automaton_type = "SA"
        self.is_epsilon_free = None
        self.epsilon_free = False

    def get_math_format(self):
        """
        Returns automaton in dictionary as in the definition:
        A = (alphabet, states, initial_states, final_states, transitions)
        :return: dictionary
        """
        math_format = {"alphabet": self.alphabet,
                       "states": self.states,
                       "initial_states": self.start,
                       "final_states": self.final,
                       "transitions": self.transitions}

        return math_format

    def reverse(self, force=False):
        """
        Reverses the automaton transitions:
        a(p)->q becomes a(q)->p
        stores the resulting automaton in attribute reversed
        :return: reversed version of the automaton
        """
        if self.reversed and not force:
            # automaton was reversed before
            return

        # copy all attributes but transitions and reversed
        self.reversed = self.get_new()
        self.reversed.alphabet = self.alphabet
        self.reversed.states = self.states
        self.reversed.start = self.start
        self.reversed.final = self.final
        self.reversed.transitions = {}
        self.reversed.deterministic = None

        # revert the direction of every transition
        for trans_group in self.transitions:
            for trans_label in self.transitions[trans_group]:
                for trans_end in self.transitions[trans_group][trans_label]:
                    if trans_end not in self.reversed.transitions:
                        # if doesn't exist, create new dictionary for the state
                        self.reversed.transitions[trans_end] = {}
                    if trans_label not in self.reversed.transitions[trans_end]:
                        # save new transition into new list
                        self.reversed.transitions[trans_end][trans_label] = [trans_group]
                    else:
                        # save new transition into existing list
                        self.reversed.transitions[trans_end][trans_label].append(trans_group)

        return deepcopy(self.reversed)

    def is_empty(self):
        """
        Checks whether language of the automaton is empty
        :return: bool
        """
        queue = self.start.copy()
        checked = set()

        while len(queue) > 0:
            # start from start state
            state = queue.pop()
            checked.add(state)

            if state in self.transitions:
                # check if state leads to a final state
                for label in self.transitions[state]:
                    for endstate in self.transitions[state][label]:
                        if endstate in self.final:
                            # one final state is reachable -> isEmpty = False
                            return False
                        if endstate not in checked:
                            queue.add(endstate)

        return True

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

    def remove_useless(self):
        """
        Reduces automaton by removing useless states
        :return: reduced automaton
        """
        result = deepcopy(self)
        result = result.remove_unused_states()

        for state in result.states:
            if result.is_useless(state):
                if state in result.start:
                    result.start.remove(state)
                if state in result.transitions:
                    del result.transitions[state]

        # then remove states which are not used in transitions
        result = result.remove_unused_states()

        return result

    def remove_unreachable(self):
        """
        Reduces automaton by removing unreachable states
        :return: reduced automaton
        """
        result = deepcopy(self)
        result = result.remove_unused_states()

        for state in result.states:
            if not result.is_reachable(state):
                if state in result.transitions:
                    del result.transitions[state]

        # then remove states which are not used in transitions
        result = result.remove_unused_states()
        return result

    def is_useless(self, state):
        """
        Checks whether a state is useless - doesnt lead to end state
        :return: bool
        """
        #if state in self.start:
        #    return False
        queue = [state]
        checked = set()

        while len(queue) > 0:
            # start from given state
            state = queue.pop()
            checked.add(state)
            if state in self.final:
                return False

            if state in self.transitions:
                # check if state leads to a final state
                for label in self.transitions[state]:
                    for endstate in self.transitions[state][label]:
                        if self.is_final(endstate):
                            return False
                        if endstate not in checked and endstate not in queue:
                            queue.append(endstate)

        return True

    def is_final(self,state):
        if state in self.final:
            return True
        else:
            return False

    def is_reachable(self, check):
        """
        Checks whether a state is reachable
        :return: bool
        """
        if check in self.start:
            return True

        queue = self.start.copy()
        checked = set()

        while len(queue) > 0:
            # start from start state
            state = queue.pop()
            checked.add(state)

            if state in self.transitions:
                # check if state leads to given state
                for label in self.transitions[state]:
                    for endstate in self.transitions[state][label]:
                        if endstate == check:
                            return True
                        if endstate not in checked:
                            queue.add(endstate)

        return False

    def remove_unused_states(self):
        """
        Reduces automaton by removing states that are not used in any transition
        :return: reduced automaton
        """
        # construct new states anf final states set according to transitions
        states_new = set()
        final_new = set()

        for starts in self.start:
            # add start states
            states_new.add(starts)
            if starts in self.final:
                # add start states to final
                final_new.add(starts)

        for state in self.transitions:
            # add beginning state of transition
            states_new.add(state)
            if state in self.final:
                final_new.add(state)
            for label in self.transitions[state]:
                for endstate in self.transitions[state][label]:
                    # add nd state of transition
                    states_new.add(endstate)
                    if endstate in self.final:
                        final_new.add(endstate)

        # replace states and final states by new sets
        result = deepcopy(self)
        result.states = states_new
        result.final = final_new

        return result

    def remove_empty_transitions(self):
        """
        Reduces automaton by removing transitions leading nowhere
        :return: reduced automaton
        """
        result = deepcopy(self)

        for state in deepcopy(result.transitions):
            for label in deepcopy(result.transitions[state]):
                if not result.transitions[state][label]:
                    del result.transitions[state][label]
                    if not result.transitions[state]:
                        del result.transitions[state]

        return result

    def print_automaton(self, filename=None):
        """
        Prints automaton in Timbuk format
        if a filename is given, prints automaton into file
        """
        # Alphabet
        export_str = "Ops "
        export_str += "x:0 "
        for letter in sorted(self.alphabet):
            export_str += letter + ":1 "
        # Automaton type
        export_str += "\n\nAutomaton A @" + self.automaton_type
        # States

        export_str += "\nStates "
        for state in sorted(self.states):
            export_str += state + " "
        # Final states
        export_str += "\nFinal States "
        if self.automaton_type == "GBA":
            for set in self.final:
                for state in set:
                    export_str += state + " "
                export_str += " ; "
        else:
            for state in sorted(self.final):
                export_str += state + " "
        # Transitions
        export_str += "\nTransitions\n"
        for state in self.start:
            # Start state transitions
            export_str += "x -> " + state + "\n"
        for trans_group in sorted(self.transitions):
            start_state = trans_group
            for trans_label in self.transitions[trans_group]:
            #for trans_label in sorted(self.transitions[trans_group]):
                for trans_end in self.transitions[trans_group][trans_label]:
                    end_state = trans_end
                    if self.automaton_type == "LFA":
                        export_str += str(trans_label) + "(" + start_state + ") -> " + end_state + "\n"
                    else:
                        export_str += "\"" + str(trans_label) + "\"(" + start_state + ") -> " + end_state + "\n"

        if filename is not None:
            with open(filename, 'w') as the_file:
                the_file.write(export_str)
        else:
            print(export_str)

    def intersection(self, automaton_2):
        """
        Performs intersection of two automata
        :param automaton_2: the second automaton
        :return: automaton created by intersection
        """
        intersect = self.get_new()
        intersect.alphabet = self.alphabet.intersection(automaton_2.alphabet)
        intersect.reversed = None

        queue = list(itertools.product(self.start, automaton_2.start))
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

            if state1 in self.final and state2 in automaton_2.final:
                intersect.final.add(combined_str)

            if state1 in self.transitions and state2 in automaton_2.transitions:
                for label in self.transitions[state1]:
                    for label2 in automaton_2.transitions[state2]:
                        common = label.conjunction(label2)
                        #print(common)
                        if common and common.is_satisfiable():
                            endstates = itertools.product(self.transitions[state1][label], automaton_2.transitions[state2][label2])
                            for endstate in endstates:
                                endstate_str = "[" + endstate[0] + "_1|" + endstate[1] + "_2]"
                                #endstate = self.transitions[state1][label][0] + "," + automaton_2.transitions[state2][label2][0]

                                if common not in intersect.transitions[combined_str]:
                                    intersect.transitions[combined_str][common] = [endstate_str]
                                else:
                                    intersect.transitions[combined_str][common].append(endstate_str)

                                if endstate not in queue and endstate_str not in intersect.states:
                                    queue.append(endstate)
                                #print(intersect.transitions)

        intersect = intersect.simple_reduce()
        #print(intersect.transitions)
        #intersect.remove_commas_from_states()

        return intersect

    def union(self, other):
        """
        Performss union of two automata
        :param other: the second automaton
        :return: automaton created by union
        """
        uni = self.get_new()
        uni.alphabet = self.alphabet.union(other.alphabet)
        uni.reversed = None

        uni.start = set()
        for q in self.start:
            uni.start.add(q + "_1")
        for q in other.start:
            uni.start.add(q + "_2")

        uni.states = set()
        for q in self.states:
            uni.states.add(q + "_1")
        for q in other.states:
            uni.states.add(q + "_2")

        self.get_final_union(other, uni)

        for state in self.transitions:
            state_str = state + "_1"
            uni.transitions[state_str] = {}
            for label in self.transitions[state]:
                uni.transitions[state_str][label] = []
                for endstate in self.transitions[state][label]:
                    uni.transitions[state_str][label].append(endstate + "_1")

        for state in other.transitions:
            state_str = state + "_2"
            uni.transitions[state_str] = {}
            for label in other.transitions[state]:
                uni.transitions[state_str][label] = []
                for endstate in other.transitions[state][label]:
                    uni.transitions[state_str][label].append(endstate + "_2")

        uni.simple_reduce()

        return uni

    def get_final_union(self, other, uni):
        uni.final = set()
        for q in self.final:
            uni.final.add(q + "_1")
        for q in other.final:
            uni.final.add(q + "_2")

    def check_automaton(self):
        """
        Checks whether automaton is valid:
            - has initial states
            - has states
            - has nonempty alphabet
            - final states are subset of all states
            - initial states are subset of all states
            - all states used in transitions are in automaton states
            - all transition labels are satisfiable
        :return: OK if automaton is valid, Error message if automaton is invalid
        """
        if not len(self.start):
            return "No initial states given."
        if not len(self.states):
            return "No states given."
        if not len(self.alphabet):
            return "Empty alphabet given."
        if self.automaton_type == "GBA":
            for set in self.final:
                if not set <= self.states:
                    return "F is not subset Q: Some of the final states are not in states."
        else:
            if not self.final <= self.states:
                return "F is not subset Q: Some of the final states are not in states."
        if not self.start <= self.states:
            return "I is not subset Q: Some of the start states are not in states."
        for state in self.transitions:
            if state not in self.states:
                return "State " + state + " not in states."
            for label in self.transitions[state]:
                if not label.is_epsilon:
                    if not label.is_satisfiable():
                        return "Unsatisfiable label " + str(label) + " from state " + state
                    for endstate in self.transitions[state][label]:
                        if endstate not in self.states:
                            return "State " + state + " not in states."
        return "OK"

    @staticmethod
    def get_new():
        """
        Creates and returns new empty object of class
        :return: empty object Symbolic
        """
        return Symbolic()

    @staticmethod
    def list_powerset(length):
        """
        Returns powerset of a list of given length
        :param length: length
        :return: list powerset
        """
        lst = []
        for i in range(0, length):
            lst.append(i)
        result = [[]]
        for x in lst:
            result.extend([subset + [x] for subset in result])
        return result

    def get_automaton_name(self):
        """
        Returns automaton name.
        :return: automaton name
        """

        return self.automaton_name

    def rename_automaton(self, new_name):
        """
        Rename automaton.
        :param new_name: Set automaton name to this name.
        """

        self.automaton_name = new_name

    def change_initial_states(self, new_initial_states):
        """
        Change automaton's initial states.
        :param new_initial_states: Set of the new initial states for the automaton.
        """

        self.start = new_initial_states

    def remove_useless_transitions(self):
        """
        Remove useless transitions leading to states not in self.states set.
        """

        copied_transitions = deepcopy(self.transitions)

        for state in copied_transitions:
            for symbol in copied_transitions[state]:
                for target_state in copied_transitions[state][symbol]:
                    if target_state not in self.states:
                        self.transitions[state][symbol].remove(target_state)
                        if not self.transitions[state][symbol]:
                            del self.transitions[state][symbol]

    def remove_abstract_final_state(self, abstract_final_symbol, abstract_final_state = ''):
        """
        Remove abstract final symbol, abstract final state and make the states leading to abstract final state throught abstract final symbol final states.
        :param abstract_final_symbol: Used abstract final symbol leading to abstract final state.
        :param abstract_final_state: Used abstract final state.
        """

        abstract_final_state_removed = False
        copied_transitions = deepcopy(self.transitions)

        if not abstract_final_state:
            abstract_final_state = self.final.pop()
            abstract_final_state_removed = True
        else:
            abstract_final_state += ',' + abstract_final_state
        if not abstract_final_state:
            return

        for state in copied_transitions:
            for symbol in copied_transitions[state]:
                if symbol == abstract_final_symbol:
                    self.final.add(state)
                    del self.transitions[state][symbol]

        # Remove abstract final state from final states set and states set.
        self.states.remove(abstract_final_state)
        if not abstract_final_state_removed:
            self.final.remove(abstract_final_state)
