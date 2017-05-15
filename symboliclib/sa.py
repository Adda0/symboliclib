"""
SA - Symbolic Automaton class

represents symbolic finite automaton

Copyright (c) 2017  Michaela Bielikova <xbieli06@stud.fit.vutbr.cz>
"""
from __future__ import print_function

from copy import deepcopy
from symbolic import Symbolic
import itertools


class SA(Symbolic):
    """
    Symbolic finite automaton class

    Attributes:
        -- classic automaton attributes:
        alphabet        set of symbols
        states          set of states
        start           set of initial states
        final           set of final states
        transitions     dictionary of transitions
        automaton_type  type of automaton - here INFA (In/Not_in Finite Automaton)

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
        # sign whether automaton is deterministic
        self.deterministic = None
        # reversed variant of the automaton
        self.reversed = None
        self.determinized = None
        self.automaton_type = "INFA"
        self.is_epsilon_free = None
        self.epsilon_free = None
        self.label = None

    @staticmethod
    def get_new():
        """
        Creates and returns new empty object of class
        :return: empty object SA
        """
        return SA()

    def remove_epsilon(self):
        """
        Creates epsilon_free version of the automaton
        stores result in attribute epsilon_free
        :return: epsilon_free automaton
        """
        if self.epsilon_free is not None:
            return self.epsilon_free
        if self.is_epsilon_free:
            return self

        eps_free = deepcopy(self)
        for state in self.transitions:
            closure = self.get_epsilon_closure(state)
            # every start state that has a final state in eps closure must be final
            if state in self.start:
                if len(self.final.intersection(closure)):
                    self.final.add(state)
            # add transitions that will replace epsilon transitions
            for closure_state in closure:
                if closure_state in self.transitions:
                    for label in self.transitions[closure_state]:
                        if label.is_epsilon:
                            continue
                        for endstate in self.transitions[closure_state][label]:
                            if label in eps_free.transitions[state]:
                                if endstate not in eps_free.transitions[state][label]:
                                    eps_free.transitions[state][label].append(endstate)
                            else:
                                eps_free.transitions[state][label] = [endstate]
        # delete epsilon transitions
        for state in self.transitions:
            for label in self.transitions[state]:
                if label.is_epsilon:
                    del eps_free.transitions[state][label]

        self.epsilon_free = eps_free

        return eps_free

    def get_epsilon_closure(self, state, checked=set()):
        """
        Finds epsilon closure of a state
        :param state: state to check
        :param checked: already checked states
        :return: epsilon closure of state
        """
        result = set()

        if state in self.transitions:
            for label in self.transitions[state]:
                if label.is_epsilon:
                    for endstate in self.transitions[state][label]:
                        if endstate not in checked:
                            result.add(endstate)
                            checked.add(endstate)
                            result = result.union(self.get_epsilon_closure(endstate, checked))

        return result

    def is_deterministic(self):
        """
        Checks if the automaton is deterministic
        sets the deterministic attribute
        :return: bool
        """
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
        det = self.determinize()

        complement = deepcopy(det)
        # changes final states for non-final
        complement.final = det.states - det.final

        return complement

    def is_included_simple(self, other):
        """
        Checks whether automaton is included in the other one:
        self <= other ?
        Algorithm checks whether L(self) ^ !L(other) == {}
        :param other: other automaton
        :return: bool
        """
        # algorithm works for complete automata only
        alphabet = self.alphabet.union(other.alphabet)
        det_other = other.determinize()
        det_other.alphabet = alphabet
        complete_other = det_other.get_complete()
        alpha_self = deepcopy(self)
        alpha_self.alphabet = alphabet
        complete_self = alpha_self.get_complete()
        # compute !L(other)
        det_com = complete_other.complement()

        # compute L(self) ^ !L(other)
        con = complete_self.intersection(det_com)
        if con.is_empty():
            return True
        return False

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
        # then reduce remaining transitions
        result = result.reduce_transitions()

        return result

    def reduce_transitions(self):
        """
        Reduces number of transitions by uniting them into one when possible
        :return: reduced automaton
        """
        result = deepcopy(self)
        new_transitions = deepcopy(result.transitions)

        # first join transitions with the same start and end states into one

        # reduce for each state
        for state in deepcopy(result.transitions):
            # iterate through all labels
            queue = list(result.transitions[state].keys())

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

        result.transitions = new_transitions
        result = result.remove_empty_transitions()
        new_transitions = deepcopy(result.transitions)

        # them remove redundant states

        # reduce for each state
        for state in deepcopy(result.transitions):
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

        result.transitions = new_transitions
        result = result.remove_empty_transitions()

        return result

    def is_included_antichain(self, other):
        """
        Checks whether automaton is included in the other one:
        self <= other ?
        Algorithm uses antichains
        :param other: other automaton
        :return: bool
        """
        # alphabet which we work with must be a union of both alphabets
        # otherwise the contradiction doesnt have to be found
        alphabet = self.alphabet.union(other.alphabet)
        self_alpha = deepcopy(self)
        self_alpha.alphabet = alphabet
        other_alpha = deepcopy(other)
        other_alpha.alphabet = alphabet

        self_compl = self_alpha.get_complete()
        other_compl = other_alpha.get_complete()
        # try to find contradiction in empty word
        if self_compl.final.intersection(self_compl.start):
            if not other_compl.final.intersection(other_compl.start):
                return False

        other_sim = other_compl.simulations_preorder()
        self_sim = self_compl.simulations_preorder()

        processed = []
        next = []
        for start in self_compl.start:
            next.append((start, other_compl.minim_antichain(other_compl.start, other_sim)))

        while len(next):
            # (r,R)
            pair = next.pop()
            processed.append(pair)
            post = self_compl.post_antichain(other_compl, pair)
            # (p,P)
            for post_pair in post:
                post_pair_min = (post_pair[0], self_compl.minim_antichain(post_pair[1], other_sim))
                if post_pair_min[0] in self_compl.final and not other_compl.check_superstate_final(post_pair_min[1]):
                    return False
                # (x,X)
                simulation_processed = False
                # check if a simulating pair was not processed before
                for processed_pair in next+processed:
                    if (post_pair_min[0], processed_pair[0]) in self_sim:
                        if other.check_superstate_simulations(processed_pair[1], post_pair_min[1], other_sim):
                            simulation_processed = True
                            break
                if not simulation_processed:
                    for pr in processed.copy():
                        for ne in next.copy():
                            if (processed_pair[0], post_pair[0]) in self_sim:
                                if other.check_superstate_simulations(post_pair_min[1], processed_pair[1], other_sim):
                                    if pr in processed:
                                        processed.remove(pr)
                                    if ne in next:
                                        next.remove(ne)
                    # add for future
                    if post_pair_min not in next and post_pair_min not in processed:
                        next.append(post_pair_min)

        return True

    def is_included_antichain_pure(self, other):
        """
        Checks whether automaton is included in the other one:
        self <= other ?
        Algorithm doesnt use simulations
        :param other: other automaton
        :return: bool
        """
        # alphabet which we work with must be a union of both alphabets
        # otherwise the contradiction doesnt have to be found
        alphabet = self.alphabet.union(other.alphabet)
        self_alpha = deepcopy(self)
        self_alpha.alphabet = alphabet
        other_alpha = deepcopy(other)
        other_alpha.alphabet = alphabet

        self_compl = self_alpha.get_complete()
        other_compl = other_alpha.get_complete()
        # try to find contradiction in empty word
        if self_compl.final.intersection(self_compl.start):
            if not other_compl.final.intersection(other_compl.start):
                return False

        processed = []
        next = []
        for start in self_compl.start:
            next.append((start, other_compl.start))

        while len(next):
            # (r,R)
            pair = next.pop()
            processed.append(pair)
            post = self_compl.post_antichain(other_compl, pair)
            # (p,P)
            for post_pair in post:
                post_pair_min = (post_pair[0], post_pair[1])
                if post_pair_min[0] in self_compl.final and not other_compl.check_superstate_final(post_pair_min[1]):
                    return False
                if post_pair_min not in next and post_pair_min not in processed:
                    next.append(post_pair_min)

        return True

    def check_superstate_simulations(self, less, more, simulations):
        """
        Checks if macrostate simulates M another macrostate L (L<=M)
        :param less: macrostate L
        :param more: macrostate M
        :param simulations: simulations relation
        :return: True or False
        """
        combinations = list(itertools.product(less, more))
        for pair in combinations:
            if (pair[0], pair[1]) not in simulations and (pair[1], pair[0]) not in simulations:
                return False

        return True

    def check_superstate_final(self, states_set):
        """
        Checks if a macrostate is final
        :param states_set: macrostate to check
        :return: True or False
        """
        if self.final.intersection(states_set):
            return True
        return False


    def post_antichain(self, other, pair):
        """
        Computes post relation for antichain algorithm
        :param other: other automaton
        :param pair: pair of states (p,Q), p is a state from self, Q is a superstate from other
        :return: post relation
        """
        result = []
        for a in self.alphabet.union(other.alphabet):
            new_qs = set()
            new_superstates = set()
            if pair[0] in self.transitions:
                for label in self.transitions[pair[0]]:
                    if label.has_letter(a):
                        new_qs = new_qs.union(self.transitions[pair[0]][label])
            for superset_state in pair[1]:
                if superset_state in other.transitions:
                    for label in other.transitions[superset_state]:
                        if label.has_letter(a):
                            new_superstates = new_superstates.union(other.transitions[superset_state][label])

            if new_qs and new_superstates:
                for q in new_qs:
                    result.append((q, new_superstates))

        return result

    def minim_antichain(self, states_set, simulations):
        """
        Removes simulating states from a set of states for antichains algorithm
        :param states_set: set of states to reduce
        :param simulations: simulation relation over automata states
        :return: reduced states set
        """
        for pair in simulations:
            state = pair[0]
            sim_state = pair[1]
            if state != sim_state and state in states_set and sim_state in states_set:
                states_set.remove(state)

        return states_set



    def is_included(self, other):
        """
        Checks whether automaton is included in the other one:
        self <= other ?
        Algorithm checks whether L(self) ^ !L(other) == {}
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
        """
        Checks whether automaton is equivalent to the other one
        :param other: other automaton
        :return: reduced automaton
        """
        if self.is_included(other) and other.is_included(self):
            return True

        return False

    def is_universal(self):
        """
        Checks whether automaton is universal
        :return: bool
        """
        min = self.minimize()
        for state in min.states:
            if state not in min.final:
                return False

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
                # create an error label
                error_label = None
                labels = list(complete.transitions[state].keys())
                for label in labels:
                    if not error_label:
                        error_label = label.negation()
                    else:
                        error_label = error_label.conjunction(label.negation())
                    # rename all error states to "error"
                    endstates = complete.transitions[state][label]
                    for endstate in endstates:
                        if complete.is_useless(endstate):
                            complete.transitions[state][label].remove(endstate)
                            if "qsink" not in complete.transitions[state][label]:
                                complete.transitions[state][label].append("qsink")
                if not error_label:
                    error_label = complete.label.get_universal()
                if error_label not in complete.transitions[state]:
                    complete.transitions[state][error_label] = ["qsink"]
                else:
                    complete.transitions[state][error_label].append("qsink")
            else:
                error_label = complete.label.get_universal()
                complete.transitions[state] = {}
                complete.transitions[state][error_label] = ["qsink"]

        return complete

    def simulations_preorder(self):
        """
        Computes simulation_preorder relation
        :return: pairs of states that simulate each other
        """
        complete = self.get_complete()

        complete.reverse(True)
        rever_trans = complete.reversed.transitions

        card = {}

        for state in complete.states:
            for a in complete.alphabet:
                if state in complete.transitions:
                    for label in complete.transitions[state]:
                        if (state,a) in card:
                            if label.has_letter(a):
                                card[(state, a)] += len(complete.transitions[state][label])
                        else:
                            if label.has_letter(a):
                                card[(state, a)] = len(complete.transitions[state][label])
                            else:
                                card[(state, a)] = 0
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
                if j in rever_trans:
                    for label in rever_trans[j]:
                        if label.has_letter(a):
                            for k in rever_trans[j][label]:
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
                                        if i in rever_trans:
                                            for label in rever_trans[i]:
                                                if label.has_letter(a):
                                                    for l in rever_trans[i][label]:
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
                    if (state, state2) not in result and (state2, state) not in result:
                        simulations.append((state, state2))

        for state in complete.states:
            simulations.append((state, state))

        return simulations

    def to_lfa(self):
        """
        Converts symbolic automaton into a classic finite automaton
        :return: LFA automaton
        """
        from lfa import LFA
        from letter import Letter
        classic = LFA.get_new()
        classic.alphabet = self.alphabet
        classic.states = self.states
        classic.start = self.start
        classic.final = self.final
        classic.label = Letter()

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
                            classic.transitions[state][new] = self.transitions[state][label]

        return classic

    def determinize(self):
        """
        Converts automaton into a deterministic one
        stores the result in attribute determinized
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

        det = det.simple_reduce()
        det.is_deterministic()

        self.determinized = det

        return det

    def minimize(self):
        """
        Converts automaton into a minimal one
        :return: minimal automaton
        """
        det = self.determinize()
        complete = det.get_complete()

        min_states = set()
        min_states.add("|".join(sorted(complete.final)))
        min_states.add("|".join(sorted(complete.states - complete.final)))

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
                    if state in complete.transitions:
                        for label in complete.transitions[state]:
                            for endstate in complete.transitions[state][label]:
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
                    for old_state in complete.states:
                        if old_state in new_trans[state_group]:
                            if new_trans[state_group][old_state] == item:
                                new_state_group.append(old_state)
                    next_iteration.add("|".join(sorted(new_state_group)))

            # if the subsets did not change between iterations, end
            if next_iteration == min_states:
                break
            else:
                min_states = next_iteration

        complete.states = next_iteration
        complete.transitions = {}
        new_final = set()
        new_start = set()
        for state_group in min_states:
            complete.transitions[state_group] = list(new_trans[state_group].values())[0]
            for state_old in state_group.split("|"):
                if state_old in complete.final:
                    new_final.add(state_group)
                if state_old in complete.start:
                    new_start.add(state_group)

        complete.start = new_start
        complete.final = new_final

        complete = complete.simple_reduce()

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

            labels = list(self.transitions[state].keys())
            combinations = list_powerset(len(labels))
            for com in combinations:
                # get label combinations and endstates
                end = set()
                if 0 in com:
                    add = labels[0]
                    end = set(self.transitions[state][labels[0]])
                else:
                    add = labels[0].negation()
                for j in range(1, len(labels)):
                    if j in com:
                        add = add.conjunction(labels[j])
                        end = end.union(set(self.transitions[state][labels[j]]))
                    else:
                        add = add.conjunction(labels[j].negation())
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
        """
        Merges a new transition to existing transitions without ruining determinism
        :param new_transitions: existing transitions from start state of merged transition
        :param add: transition label to add
        :param end: transitions end state to add
        :return: transitions from start state of merged transition
        """
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
                rest = original_label.conjunction(add.negation())
                del new_transitions[original_label]
                if rest and rest.is_satisfiable():
                    new_transitions = self.merge_transition(new_transitions, rest, existing_states)
                break

            if original_label.is_subset(add):
                added = True
                existing_states = set(new_transitions[original_label][0].split(","))
                merged_states = ",".join(sorted(existing_states.union(end)))
                new_transitions[original_label] = [merged_states]
                rest = add.conjunction(original_label.negation())
                if rest and rest.is_satisfiable():
                    new_transitions = self.merge_transition(new_transitions, rest, end)
                break

            conjunction = original_label.conjunction(add)
            if conjunction and conjunction.is_satisfiable():
                added = True
                conend = end.union(new_transitions[original_label][0].split(","))
                original_end = new_transitions[original_label][0].split(",")

                new_transitions = self.merge_transition(new_transitions, conjunction, conend)

                left_label = original_label.conjunction(add.negation())
                if left_label and left_label.is_satisfiable():
                    new_transitions = self.merge_transition(new_transitions, left_label, original_end)

                add_left = add.conjunction(conjunction.negation())
                if add_left and add_left.is_satisfiable():
                    new_transitions = self.merge_transition(new_transitions, add_left, end)

                break

        if not added:
            new_transitions[add] = [",".join(sorted(end))]

        return new_transitions


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
