"""
SA - Symbolic Automaton class
"""
from __future__ import print_function

from copy import deepcopy
from symbolic import Symbolic
import itertools


class SA(Symbolic):
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
        self.determinized = None
        self.automaton_type = "INFA"
        self.has_epsilon = None
        self.epsilon_Free = None

    @staticmethod
    def get_new():
        return SA()

    def is_deterministic(self):
        """
        Checks if the automaton is deterministic
        sets the deterministic attribute
        :return: bool
        """
        if self.deterministic is not None:
            # the deterministic attribute is already set, no need to check again
            return self.deterministic

        if len(self.start) > 1:
            self.deterministic = False
            return False

        for trans_group in self.transitions:
            for trans_label in self.transitions[trans_group]:
                if len(self.transitions[trans_group][trans_label]) > 1:
                    # it is possible to pass through one label in multiple states
                    # automaton is non-deterministic
                    self.deterministic = False
                    return False
                for trans_label2 in self.transitions[trans_group]:
                    if not trans_label.is_equal(trans_label2):
                        # test conjunction of each pair of labels
                        con = trans_label.conjunction(trans_label2)
                        if con.is_satisfiable():
                            # if the conjunction is satisfiable, automaton is non-deterministic
                            self.deterministic = False
                            return False

        # if no contradiction has been found, automaton is deterministic
        self.deterministic = True
        return True

    def complement(self):
        """
        Converts automaton into complement
        :return: complement automaton
        """
        backup = None
        if self.deterministic is None:
            self.is_deterministic()

        if not self.deterministic:
            backup = deepcopy(self)
            self.determinize()

        complement = self.get_new()
        complement.alphabet = self.alphabet
        complement.states = self.states
        complement.start = self.start
        # changes final states for non-final
        complement.final = self.states - self.final
        complement.transitions = self.transitions
        complement.deterministic = complement.is_deterministic()
        complement.reversed = None

        if backup:
            self = deepcopy(backup)

        return complement

    def simple_reduce(self):
        """
        In place reduces automaton by deleting unreachable and deadend states
        """
        # first remove deadend transitions
        self.remove_useless()
        # then remove unreachable transitions
        self.remove_unreachable()
        # then reduce remaining transitions
        self.reduce_transitions()

    def reduce_transitions(self):
        """Simply reduces transitions by uniting them into one when possible"""
        # TODO premysli ci sa neda pouzit uplne rovnako pre transducer, ak ano, vytiahnut do Symbolic
        new_transitions = deepcopy(self.transitions)

        # first join transitions with the same start and end states into one

        # reduce for each state
        for state in deepcopy(self.transitions):
            # iterate through all labels
            queue = list(self.transitions[state].keys())

            while len(queue) > 0:
                # save label and endstate of transition
                label = queue.pop()
                endstates = set(new_transitions[state][label])
                # iterate through other transitions
                queue_to_check = queue.copy()

                while len(queue_to_check) > 0:
                    # save new label and new endstates
                    label_to_check = queue_to_check.pop()
                    endstates_to_check = set(new_transitions[state][label_to_check])
                    common = endstates_to_check.intersection(endstates)

                    if common:
                        merged_label = label.disjunction(label_to_check)
                        if merged_label and merged_label.is_satisfiable():
                            # safe delete common from both old transitions
                            for x in common:
                                if x in new_transitions[state][label_to_check]:
                                    new_transitions[state][label_to_check].remove(x)
                                if x in new_transitions[state][label]:
                                    new_transitions[state][label].remove(x)

                        if merged_label in new_transitions[state]:
                            # if merged label already exists, dont delete it
                            existing_states = set(new_transitions[state][merged_label])
                            merged_states = list(sorted(existing_states.union(common)))
                            new_transitions[state][merged_label] = merged_states
                        else:
                            new_transitions[state][merged_label] = list(sorted(common))

                            # prepare for next iteration
                        queue.remove(label_to_check)
                        if merged_label not in queue:
                            queue.append(merged_label)

        self.transitions = new_transitions
        self.remove_empty_transitions()
        new_transitions = deepcopy(self.transitions)

        # them remove redundant states

        # reduce for each state
        for state in deepcopy(self.transitions):
            # iterate through all labels
            queue = list(new_transitions[state].keys())

            while len(queue) > 0:
                # save label and endstate of transition
                label = queue.pop()
                endstates = set(new_transitions[state][label])
                # iterate through other transitions
                queue_to_check = queue.copy()

                while len(queue_to_check) > 0:
                    # save new label and new endstates
                    label_to_check = queue_to_check.pop()
                    endstates_to_check = set(new_transitions[state][label_to_check])
                    # get common endstates and them remove them from subset
                    common = endstates.intersection(endstates_to_check)

                    if common:
                        # if label_to_check is subset, remove common states from it
                        if label_to_check.is_subset(label):
                            if label_to_check in new_transitions[state]:
                                for x in common:
                                    if x in new_transitions[state][label_to_check]:
                                        # cascade remove - no need to store transitions with empty endstate list
                                        new_transitions[state][label_to_check].remove(x)
                                        if not new_transitions[state][label_to_check]:
                                            del new_transitions[state][label_to_check]
                                            if not new_transitions[state]:
                                                del new_transitions[state]
                                if label_to_check in queue:
                                    queue.remove(label_to_check)
                                    continue

                        # if label is subset, remove common states from it
                        if label.is_subset(label_to_check):
                            if label in new_transitions[state]:
                                for x in common:
                                    if x in new_transitions[state][label]:
                                        # cascade remove - no need to store transitions with empty endstate list
                                        new_transitions[state][label].remove(x)
                                        if not new_transitions[state][label]:
                                            del new_transitions[state][label]
                                            if not new_transitions[state]:
                                                del new_transitions[state]
                                break

        self.transitions = new_transitions
        self.remove_empty_transitions()

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
                if q1 in self.determinized.transitions:
                    for label in self.determinized.transitions[q1]:
                        if label.has_letter(a):
                            q1_new = self.determinized.transitions[q1][label][0]
                else:
                    q1_new = ""
                if q2 in other.determinized.transitions:
                    for label in other.determinized.transitions[q2]:
                        if label.has_letter(a):
                            q2_new = other.determinized.transitions[q2][label][0]
                else:
                    q2_new = ""

                if q1_new != "" or q2_new != "":
                    if (q1_new, q2_new) not in checked and (q1_new, q2_new) not in queue:
                        queue.append((q1_new, q2_new))

        return True

    def is_equivalent(self, other):
        if self.is_inclusion(other) and other.is_inclusion(self):
            return True

        return False

    def is_universal(self):
        self.minimize()
        for state in self.states:
            if state not in self.final:
                return False

        return True

    def get_complete(self):
        """
        Converts automaton to language equal complete automaton
        """
        # create one nonterminating state
        self.states.add("error")
        # for transitions from each state
        for state in deepcopy(self.transitions):
            # create an error label
            error_label = None
            labels = list(self.transitions[state].keys())
            for label in labels:
                if not error_label:
                    error_label = label.complement()
                else:
                    error_label = error_label.conjunction(label.complement())
                # rename all error states to "error"
                endstates = self.transitions[state][label]
                for endstate in endstates:
                    if self.is_useless(endstate):
                        self.transitions[state][label].remove(endstate)
                        if "error" not in self.transitions[state][label]:
                            self.transitions[state][label].append("error")
            if not error_label:
                error_label = label.get_universal()
            if error_label not in self.transitions[state]:
                self.transitions[state][error_label] = ["error"]

            self.simple_reduce()

    def to_classic(self):
        from lfa import LFA
        from letter import Letter
        classic = LFA.get_new()
        classic.alphabet = self.alphabet
        classic.states = self.states
        classic.start = self.start
        classic.final = self.final

        for state in self.transitions:
            classic.transitions[state] = {}
            for label in self.transitions[state]:
                for symbol in self.alphabet:
                    if label.has_letter(symbol):
                        new = Letter()
                        new.symbol = symbol
                        if new in classic.transitions[state]:
                            for endstate in self.transitions[state][label]:
                                if endstate not in classic.transitions[state][new]:
                                    classic.transitions[state][new].append(endstate)
                        else:
                            classic.transitions[state][new] = self.transitions[state][label]

        return classic

    def determinize(self, preserve=False):
        """
        Returns an language equivalent deterministic automaton
        """
        # self should not be changed, result is expected in .determinized
        if preserve:
            # determinized version was already stored
            if self.determinized:
                return
            # if automaton is deterministic, store and return
            if self.deterministic:
                self.determinized = self
                return
        # automaton is already deterministic
        if self.deterministic:
            return

        det = self.get_new()
        #det.start = self.start.copy()
        det.start = set()
        det.start.add(",".join(self.start))

        det.alphabet = self.alphabet.copy()

        #queue = self.start.copy()
        queue = set()
        queue.add(",".join(self.start))

        checked = []
        while len(queue) > 0:
            state = queue.pop()
            checked.append(state)
            det.states.add(state)
            # add final states
            for old_state in state.split(","):
                if old_state in self.final:
                    det.final.add(state)

            new_trans = self.get_deterministic_transitions(state)
            det.transitions[state] = new_trans
            for label in new_trans:
                for endstate in new_trans[label]:
                    if endstate not in queue and endstate not in checked:
                        queue.add(endstate)

        det.simple_reduce()
        det.remove_commas_from_states()
        det.is_deterministic()

        # store result in .determinized
        if preserve:
            self.determinized = det
        # store result in self
        else:
            self.alphabet = det.alphabet
            self.states = det.states
            self.start = det.start
            self.final = det.final
            self.transitions = det.transitions
            self.automaton_type = det.automaton_type
            self.deterministic = det.deterministic
            self.determinized = self

    def minimize(self):
        """
        Converts automaton to language equal minimal automaton
        """
        self.determinize()
        self.get_complete()
        self.print_automaton()

        min_states = set()
        min_states.add("|".join(sorted(self.final)))
        min_states.add("|".join(sorted(self.states - self.final)))
        print(min_states)
        while True:
            new_trans = {}
            # to check if queue was changed
            queue = min_states.copy()
            next_iteration = set()
            while len(queue) > 0:
                state_group = queue.pop()
                new_trans[state_group] = {}
                states = state_group.split("|")

                for state in states:
                    new_trans[state_group][state] = {}
                    if state in self.transitions:
                        for label in self.transitions[state]:
                            for endstate in self.transitions[state][label]:
                                for minstate in min_states:
                                    if endstate in minstate:
                                        new_trans[state_group][state][label] = [minstate]
                    else:
                        new_trans[state_group][state] = {}
                # get new transition sets
                new_transitions = list(new_trans[state_group].values())
                # collect states which have the same transitions into one set of states
                for item in new_transitions:
                    new_state_group = []
                    for old_state in self.states:
                        if old_state in new_trans[state_group]:
                            if new_trans[state_group][old_state] == item:
                                new_state_group.append(old_state)
                    next_iteration.add("|".join(sorted(new_state_group)))

            # if the subsets did not change between iterations, end
            if next_iteration == min_states:
                break
            else:
                min_states = next_iteration

        self.states = next_iteration
        self.transitions = {}
        new_final = set()
        new_start = set()
        for state_group in min_states:
            self.transitions[state_group] = list(new_trans[state_group].values())[0]
            for state_old in state_group.split("|"):
                if state_old in self.final:
                    new_final.add(state_group)
                if state_old in self.start:
                    new_start.add(state_group)

        self.start = new_start
        self.final = new_final

        self.simple_reduce()

    def get_deterministic_transitions(self, state_group):
        """Returns deterministi transitions from a given state"""
        new_transitions = {}

        for state in state_group.split(","):
            if state not in self.transitions:
                continue

            labels = list(self.transitions[state].keys())
            combinations = list_powerset(len(labels))
            for com in combinations:
                # get label combinations and endstates
                end = set()
                if 0 in com:
                    add = labels[0]
                    end = set(self.transitions[state][labels[0]])
                else:
                    add = labels[0].complement()
                for j in range(1, len(labels)):
                    if j in com:
                        add = add.conjunction(labels[j])
                        end = end.union(set(self.transitions[state][labels[j]]))
                    else:
                        add = add.conjunction(labels[j].complement())
                # add to created transitions
                if add.is_satisfiable() and len(end):
                    if add in new_transitions:
                        # if label already exists, unite endstates
                        existing_transitions = set(new_transitions[add][0].split(","))
                        new_transitions[add] = [",".join(sorted(existing_transitions.union(end)))]
                    else:
                        new_transitions = self.merge_transition(new_transitions, add, end)

        return new_transitions

    def merge_transition(self, new_transitions, add, end):
        """Merges a new transition to existing transitions without ruining determinism"""
        if not add.is_satisfiable():
            return new_transitions
        added = False
        queue = list(new_transitions.keys())
        checked = []

        while len(queue):
            original_label = queue.pop()
            checked.append(original_label)

            if add == original_label:
                added = True
                existing_states = new_transitions[original_label][0].split(",")
                merged_states = ",".join(sorted(set(existing_states).union(end)))
                new_transitions[original_label] = [merged_states]
                break

            if add.is_subset(original_label):
                added = True
                existing_states = set(new_transitions[original_label][0].split(","))
                merged_states = ",".join(sorted(existing_states.union(end)))
                new_transitions[add] = [merged_states]
                rest = original_label.conjunction(add.complement())
                del new_transitions[original_label]
                if rest and rest.is_satisfiable():
                    new_transitions = self.merge_transition(new_transitions, rest, existing_states)
                break

            if original_label.is_subset(add):
                added = True
                existing_states = set(new_transitions[original_label][0].split(","))
                merged_states = ",".join(sorted(existing_states.union(end)))
                new_transitions[original_label] = [merged_states]
                rest = add.conjunction(original_label.complement())
                if rest and rest.is_satisfiable():
                    new_transitions = self.merge_transition(new_transitions, rest, end)
                break

            conjunction = original_label.conjunction(add)
            if conjunction and conjunction.is_satisfiable():
                added = True
                conend = end.union(new_transitions[original_label][0].split(","))
                original_end = new_transitions[original_label][0].split(",")

                new_transitions = self.merge_transition(new_transitions, conjunction, conend)

                left_label = original_label.conjunction(add.complement())
                if left_label and left_label.is_satisfiable():
                    new_transitions = self.merge_transition(new_transitions, left_label, original_end)

                add_left = add.conjunction(conjunction.complement())
                if add_left and add_left.is_satisfiable():
                    new_transitions = self.merge_transition(new_transitions, add_left, end)

                break

        if not added:
            new_transitions[add] = [",".join(sorted(end))]

        return new_transitions

def list_powerset(length):
    """Returns powerset of a list of given length"""
    lst = []
    for i in range(0, length):
        lst.append(i)
    result = [[]]
    for x in lst:
        result.extend([subset + [x] for subset in result])
    return result
