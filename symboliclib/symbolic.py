"""
Symbolic automaton class
all methods common for FA and FT
"""
from __future__ import print_function

from copy import deepcopy


class Symbolic(object):
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
        self.automaton_type = "SA"

    def reverse(self):
        """
        Reverses the automaton transitions
        stores the resulting automaton in attribute reversed
        """
        if self.reversed:
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
        In place reduces automaton by deleting unreachable and deadend states
        """
        # first remove deadend transitions
        self.remove_useless()

        # then remove unreachable transitions
        self.remove_unreachable()

    def remove_useless(self):
        """
        Removes useless states
        """
        self.remove_unused_states()

        for state in self.states:
            if self.is_useless(state):
                if state in self.transitions:
                    del self.transitions[state]

        # then remove states which are not used in transitions
        self.remove_unused_states()

    def remove_unreachable(self):
        """
        Removes unreachable states
        """
        self.remove_unused_states()

        for state in self.states:
            if not self.is_reachable(state):
                if state in self.transitions:
                    del self.transitions[state]

        # then remove states which are not used in transitions
        self.remove_unused_states()

    def is_useless(self, state):
        """
        Checks whether a state is deadend - doesnt lead to end state
        :return: bool
        """
        if state in self.start:
            return False
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
                        if endstate in self.final:
                            return False
                        if endstate not in checked:
                            queue.append(endstate)

        return True

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
        Removes in place useless states - the ones that are not used in any transition
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
        self.states = states_new
        self.final = final_new

    def remove_empty_transitions(self):
        """
        Clears useless transition structures
        """
        for state in deepcopy(self.transitions):
            for label in deepcopy(self.transitions[state]):
                if not self.transitions[state][label]:
                    del self.transitions[state][label]
                    if not self.transitions[state]:
                        del self.transitions[state]

    def remove_commas_from_states(self):
        """
        Removes commas in state names
        """
        new_transitions = {}
        for state in self.transitions:
            new_state = state.replace(",", "")
            new_transitions[new_state] = {}
            for label in self.transitions[state]:
                new_transitions[new_state][label] = []
                for endstate in self.transitions[state][label]:
                    new_endstate = endstate.replace(",", "")
                    new_transitions[new_state][label].append(new_endstate)

        self.transitions = new_transitions

        new_states = set()
        for state in self.states:
            new_states.add(state.replace(",", ""))
        self.states = new_states

        new_states = set()
        for state in self.start:
            new_states.add(state.replace(",", ""))
        self.start = new_states

        new_states = set()
        for state in self.final:
            new_states.add(state.replace(",", ""))
        self.final = new_states

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
        """Intersection
        Returns intersection
        """
        intersect = self.get_new()
        intersect.alphabet = self.alphabet.intersection(automaton_2.alphabet)
        intersect.reversed = None

        start1 = self.start.copy().pop()
        start2 = automaton_2.start.copy().pop()
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

            if state1 in self.final and state2 in automaton_2.final:
                intersect.final.add(combined)

            if state1 in self.transitions and state2 in automaton_2.transitions:
                for label in self.transitions[state1]:
                    for label2 in automaton_2.transitions[state2]:
                        common = label.conjunction(label2)
                        print(common)
                        if common and common.is_satisfiable():
                            endstate = self.transitions[state1][label][0] + "," + automaton_2.transitions[state2][label2][0]

                            if common not in intersect.transitions[combined]:
                                intersect.transitions[combined][common] = [endstate]
                            else:
                                intersect.transitions[combined][common].append(endstate)

                            if endstate not in queue and endstate not in intersect.states:
                                queue.append(endstate)
                            print(intersect.transitions)

        intersect.simple_reduce()
        print(intersect.transitions)
        intersect.remove_commas_from_states()

        return intersect

    def union(self, automaton_2):
        """Union
        Returns union
        """
        uni = self.get_new()
        uni.alphabet = self.alphabet.intersection(automaton_2.alphabet)
        uni.reversed = None

        start1 = self.start.copy().pop()
        start2 = automaton_2.start.copy().pop()
        first = str(start1) + "," + str(start2)
        uni.start = set()
        uni.start.add(first)
        queue = [first]

        while len(queue) > 0:
            combined = queue.pop()
            uni.states.add(combined)
            if combined not in uni.transitions:
                uni.transitions[combined] = {}
            states = combined.split(",")
            state1 = states[0]
            state2 = states[1]

            if state1 in self.final or state2 in automaton_2.final:
                uni.final.add(combined)

            if state1 in self.transitions and state2 in automaton_2.transitions:
                for label in self.transitions[state1]:
                    for label2 in automaton_2.transitions[state2]:
                        common = label.disjunction(label2)
                        if common and common.is_satisfiable():
                            endstate = self.transitions[state1][label][0] + "," + automaton_2.transitions[state2][label2][0]

                            if common not in uni.transitions[combined]:
                                uni.transitions[combined][common] = [endstate]
                            else:
                                uni.transitions[combined][common].append(endstate)

                            if endstate not in queue and endstate not in uni.states:
                                queue.append(endstate)

        uni.simple_reduce()
        uni.remove_commas_from_states()

        return uni

    def check_automaton(self):
        if not len(self.start):
            return "No initial states given."
        if not len(self.states):
            return "No states given."
        if not len(self.alphabet):
            return "Empty alphabet given."
        if not self.final <= self.states:
            return "F is not subset Q: Some of the final states are not in states."
        if not self.start <= self.states:
            return "I is not subset Q: Some of the start states are not in states."
        for state in self.transitions:
            if state not in self.states:
                return "State " + state + " not in states."
            for label in self.transitions[state]:
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
