"""
BA - Buchi Finite Automaton class

represents classic finite automaton

Copyright (c) 2017  Michaela Bielikova <xbieli06@stud.fit.vutbr.cz>
"""
from __future__ import print_function

import itertools

from lfa import LFA
from copy import deepcopy
from itertools import chain, combinations


class BA(LFA):
    """
    Buchi finite automaton class

    Attributes:
        -- classic automaton attributes:
        alphabet        set of symbols
        states          set of states
        start           set of initial states
        final           set of final states
        transitions     dictionary of transitions
        automaton_type  type of automaton - here BA (Buchi Automaton)

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
        self.q1 = set()
        self.q2 = set()
        self.start = set()
        self.final = []
        self.transitions = {}
        self.delta1 = {}
        self.delta2 = {}
        self.deltat = {}
        self.deterministic = None
        self.determinized = None
        self.reversed = None
        self.automaton_type = "GBA"
        self.label = None
        self.is_epsilon_free = None
        self.epsilon_free = None

    @staticmethod
    def get_new():
        """
        Creates and returns new empty object of class
        :return: empty object LFA
        """
        return BA()

    def split_components(self):
        if not self.is_semideterministic():
            print("Automaton is not semideterministic.")
            return None

        self.q1 = set()
        self.q2 = set()
        self.delta1 = {}
        self.delta2 = {}
        self.deltat = {}

        queue = set()
        for sset in self.final:
            queue = queue.union(sset)
        done = set()
        while len(queue):
            state = queue.pop()
            done.add(state)
            self.q2.add(state)
            if state in self.transitions:
                for symbol in self.transitions[state]:
                    end = self.transitions[state][symbol][0]
                    if end not in done:
                        queue.add(end)

        self.q1 = self.states - self.q2

        for left in self.transitions:
            for symbol in self.transitions[left]:
                for right in self.transitions[left][symbol]:
                    if left in self.q1 and right in self.q1:
                        self.delta1 = self.add_trans(self.delta1, left, symbol, right)
                    if left in self.q1 and right in self.q2:
                        self.deltat = self.add_trans(self.deltat, left, symbol, right)
                    if left in self.q2 and right in self.q2:
                        self.delta2 = self.add_trans(self.delta2, left, symbol, right)

    def fix_final_states(self):
        """
        changes F so that every entering state of Q2 is final
        and every I in Q2 is final
        without changing the language
        """
        if len(self.q2) == 0:
            self.split_components()

        # I^Q2 <= F
        entry = self.q2.intersection(self.start)
        if len(entry):
            for state in entry:
                if state in self.transitions:
                    new_name = state + "'"
                    self.states.add(new_name)
                    self.final[0].add(new_name)
                    self.start.add(new_name)
                    self.transitions[new_name] = deepcopy(self.transitions[state])
                    self.start.remove(state)

        # deltat(Q1,a) <= F
        for state in self.deltat:
            for symbol in self.deltat[state]:
                for endstate in self.deltat[state][symbol]:
                    if not self.is_final(endstate):
                        new_name = endstate + "'"
                        self.states.add(new_name)
                        self.final[0].add(new_name)
                        self.transitions[state][symbol].remove(endstate)
                        self.transitions[state][symbol].append(new_name)
                        if endstate in self.transitions:
                            self.transitions[new_name] = deepcopy(self.transitions[endstate])

        # vypocitat nove Q1,Q2,delta1,delta2,deltat
        self.split_components()

    def is_final(self, state):
        for sset in self.final:
            if state in sset:
                return True
        return False

    def print_components(self):
        print("q1:")
        print(self.q1)
        print("q2:")
        print(self.q2)
        print("delta1:")
        print(self.delta1)
        print("deltat:")
        print(self.deltat)
        print("delta2:")
        print(self.delta2)

    def complement_ncsb(self):
        # get division to Qn,Qd, delta_n, delta_t, delta_d
        self.split_components()
        final = self.final[0]
        complement = self.get_new()
        complement.alphabet = deepcopy(self.alphabet)
        complement_final = set()

        #get initial states
        start_n = self.q1.intersection(self.start)
        c_or_s = self.q2.intersection(self.start)
        if len(c_or_s):
            # @TODO !!!
            start_c = c_or_s.intersection(final)
            c_or_s = c_or_s - final
            print(self.get_posibilities(c_or_s))
        else:
            start = self.get_ncsb(start_n, set(), set(), set())
            complement.start.add(self.get_text_label(start))

        queue = []
        queue.append(start)
        done = []

        while len(queue):
            state_set = queue.pop()
            done.append(state_set)

            if state_set["s"].intersection(final):
                # Block if a final state is in S
                continue
            if state_set["s"].intersection(state_set["c"]):
                # block if S and C have common state
                continue

            # add to states and final
            label = self.get_text_label(state_set)
            if label not in complement.states:
                complement.states.add(label)
            if not len(state_set["b"]) and label not in complement_final:
                complement_final.add(label)

            for symbol in self.alphabet:
                # check if every state from C-F has an successor
                block = False
                check_block = state_set["c"] - final
                for block_state in check_block:
                    if block_state not in self.transitions or symbol not in self.transitions[block_state]:
                        block = True
                        break
                if block:
                    # Blocking because of C-F succesors
                    continue

                # compute N', C', S'
                new_n = self.post(self.delta1, state_set["n"], symbol)
                new_s = self.post(self.delta2, state_set["s"], symbol)
                if new_s.intersection(final):
                    # Blocking because S has final successor
                    continue
                new_c = self.post(self.delta2, state_set["c"] - final, symbol)
                if new_s.intersection(new_c):
                    # "Blocking because S has common successor with C
                    continue

                # compute states which can be in both S and C, to decide later
                c_or_s = self.post(self.deltat, state_set["n"], symbol).union(
                    self.post(self.delta2, state_set["c"].intersection(final), symbol))
                # remove final states - they must do in C
                new_c = new_c.union(c_or_s.intersection(final))
                c_or_s = c_or_s - final

                if len(c_or_s):
                    # generate all possible C'/S' combinations
                    posibilities = self.get_posibilities(c_or_s)
                    for pos in posibilities:
                        new_new_c = new_c.union(pos[0])
                        new_new_s = new_s.union(pos[1])

                        if len(state_set["b"]):
                            new_b = self.post(self.delta2, state_set["b"], symbol).intersection(new_new_c)
                        else:
                            new_b = deepcopy(new_new_c)
                        new_state = self.get_ncsb(new_n, new_new_c, new_new_s, new_b)
                        new_label = self.get_text_label(new_state)
                        complement.transitions = self.add_trans(complement.transitions, label, symbol, new_label)
                        # save for later processing
                        if new_state not in queue and new_state not in done:
                            queue.append(new_state)
                else:
                    # no C'/S' nondeterminism, just add new state
                    if len(state_set["b"]):
                        new_b = self.post(self.delta2, state_set["b"], symbol).intersection(new_c)
                    else:
                        new_b = deepcopy(new_c)
                    new_state = self.get_ncsb(new_n, new_c, new_s, new_b)
                    new_label = self.get_text_label(new_state)
                    complement.transitions = self.add_trans(complement.transitions, label, symbol, new_label)
                    # save for later processing
                    if new_state not in queue and new_state not in done:
                        queue.append(new_state)

        complement.final.append(complement_final)

        return complement

    def complement_ncsb_early_flush(self):
        # get division to Qn,Qd, delta_n, delta_t, delta_d
        self.split_components()
        final = self.final[0]
        complement = self.get_new()
        complement.alphabet = deepcopy(self.alphabet)
        complement_final = set()

        #get initial states
        start_n = self.q1.intersection(self.start)
        c_or_s = self.q2.intersection(self.start)
        if len(c_or_s):
            # @TODO !!!
            # alfa = true
            start_c = c_or_s.intersection(final)
            c_or_s = c_or_s - final
            print(self.get_posibilities(c_or_s))
        else:
            start = self.get_ncsba(start_n, set(), set(), set(), True)
            complement.start.add(self.get_text_label(start))

        queue = []
        queue.append(start)
        done = []

        while len(queue):
            state_set = queue.pop()
            done.append(state_set)

            if state_set["s"].intersection(final):
                # Block if a final state is in S
                continue
            if state_set["s"].intersection(state_set["c"]):
                # block if S and C have common state
                continue

            # add to states and final
            label = self.get_text_label(state_set)
            if label not in complement.states:
                complement.states.add(label)
            if state_set["a"] and label not in complement_final:
                complement_final.add(label)

            for symbol in self.alphabet:
                # check if every state from C-F has an successor
                block = False
                check_block = state_set["c"] - final
                for block_state in check_block:
                    if block_state not in self.transitions or symbol not in self.transitions[block_state]:
                        block = True
                        break
                if block:
                    # Blocking because of C-F succesors
                    continue

                # compute N', C', S'
                new_n = self.post(self.delta1, state_set["n"], symbol)
                new_s = self.post(self.delta2, state_set["s"], symbol)
                if new_s.intersection(final):
                    # Blocking because S has final successor
                    continue
                new_c = self.post(self.delta2, state_set["c"] - final, symbol)
                if new_s.intersection(new_c):
                    # "Blocking because S has common successor with C
                    continue

                # compute states which can be in both S and C, to decide later
                c_or_s = self.post(self.deltat, state_set["n"], symbol).union(
                    self.post(self.delta2, state_set["c"].intersection(final), symbol))
                # remove final states - they must do in C
                new_c = new_c.union(c_or_s.intersection(final))
                c_or_s = c_or_s - final

                if len(c_or_s):
                    # generate all possible C'/S' combinations
                    posibilities = self.get_posibilities(c_or_s)
                    for pos in posibilities:
                        new_new_c = new_c.union(pos[0])
                        new_new_s = new_s.union(pos[1])

                        new_a = self.post(self.delta2, state_set["b"], symbol).intersection(new_new_c)
                        if len(new_a):
                            new_b = deepcopy(new_a)
                            new_a = False
                        else:
                            new_b = deepcopy(new_new_c)
                            new_a = True

                        new_state = self.get_ncsba(new_n, new_new_c, new_new_s, new_b, new_a)
                        new_label = self.get_text_label(new_state)
                        complement.transitions = self.add_trans(complement.transitions, label, symbol, new_label)
                        # save for later processing
                        if new_state not in queue and new_state not in done:
                            queue.append(new_state)
                else:
                    # no C'/S' nondeterminism, just add new state
                    new_a = self.post(self.delta2, state_set["b"], symbol).intersection(new_c)
                    if len(new_a):
                        new_b = deepcopy(new_a)
                        new_a = False
                    else:
                        new_b = deepcopy(new_c)
                        new_a = True
                    new_state = self.get_ncsba(new_n, new_c, new_s, new_b, new_a)
                    new_label = self.get_text_label(new_state)
                    complement.transitions = self.add_trans(complement.transitions, label, symbol, new_label)
                    # save for later processing
                    if new_state not in queue and new_state not in done:
                        queue.append(new_state)

        complement.final.append(complement_final)

        return complement

    @staticmethod
    def get_ncsba(n, c, s, b, a):
        return {"n": n, "c": c, "s": s, "b": b, "a": a}

    @staticmethod
    def get_ncsb(n, c, s, b):
        return {"n": n, "c": c, "s": s, "b": b}

    def post(self, transitions, state_set, symbol):
        post = set()
        for state in state_set:
            if state in transitions:
                if symbol in transitions[state]:
                    for endstate in transitions[state][symbol]:
                        post.add(endstate)
        return post

    @staticmethod
    def get_text_label(state_set):
        if len(state_set) == 4:
            text = ("({" + ",".join(sorted(state_set["n"])) + "},{" +
                    ",".join(sorted(state_set["c"])) + "},{" +
                    ",".join(sorted(state_set["s"])) + "},{" +
                    ",".join(sorted(state_set["b"])) + "})")
        else:
            text = ("({" + ",".join(sorted(state_set["n"])) + "},{" +
                    ",".join(sorted(state_set["c"])) + "},{" +
                    ",".join(sorted(state_set["s"])) + "},{" +
                    ",".join(sorted(state_set["b"])) + "}," + str(state_set["a"]) +
                    ")")
        return text

    def get_posibilities(self, state_set):
        result = []
        posibilities = self.powerset(state_set)
        #print("get_posibilities")
        for pos in posibilities:
            one = set()
            for p in pos:
                one.add(p)
            result.append((one, state_set - one))
        #print("end")
        #print(result)
        return result

    @staticmethod
    def add_trans(transitions, text, symbol, new_text):
        if text in transitions:
            if symbol in transitions[text]:
                transitions[text][symbol].add(new_text)
            else:
                transitions[text][symbol] = set()
                transitions[text][symbol].add(new_text)
        else:
            transitions[text] = {}
            transitions[text][symbol] = set()
            transitions[text][symbol].add(new_text)


        return transitions

    @staticmethod
    def powerset(iterable):
        """
        powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
        """
        xs = list(iterable)
        # note we return an iterator rather than a list
        return chain.from_iterable(combinations(xs, n) for n in range(len(xs) + 1))

    def is_semideterministic(self):
        queue = set()
        for sset in self.final:
            queue = queue.union(sset)
        done = set()
        while len(queue):
            state = queue.pop()
            done.add(state)
            if state in self.transitions:
                for symbol in self.alphabet:
                    if symbol in self.transitions[state]:
                        if len(self.transitions[state][symbol]) > 1:
                            return False
                        else:
                            end = self.transitions[state][symbol][0]
                            if end not in done:
                                queue.add(end)
        return True

    def simple_reduce(self):
        """
        Reduces automaton by removing unreachable and useless states
        :return: reduced automaton
        """
        result = deepcopy(self)
        # then remove unreachable transitions
        result = result.remove_unreachable()

        return result

    def get_final_union(self, other, uni):
        uni.final = []
        uni.final.append(set())
        for q in self.final[0]:
            uni.final[0].add(q + "_1")
        for q in other.final[0]:
            uni.final[0].add(q + "_2")

    def intersection(self, a2):
        """
        Performs intersection of two automata
        Works only on buchi automata with one states set in F
        :param a2: the second automaton
        :return: automaton created by intersection
        """
        # self.print_automaton()
        # a2.print_automaton()
        intersect = self.get_new()
        intersect.alphabet = self.alphabet.intersection(a2.alphabet)
        intersect.reversed = None

        queue = list(itertools.product(self.start, a2.start))
        intersect.start = set()

        for q in queue:
            intersect.start.add("[" + q[0] + "_1|" + q[1] + "_2]")

        final1 = set()
        final2 = set()

        while len(queue) > 0:
            combined = queue.pop()
            state1 = combined[0]
            state2 = combined[1]
            combined_str = "[" + state1 + "_1|" + state2 + "_2]"
            intersect.states.add(combined_str)
            if combined_str not in intersect.transitions:
                intersect.transitions[combined_str] = {}

            for sset in self.final:
                if state1 in sset:
                    final1.add(combined_str)

            for sset in a2.final:
                if state2 in sset:
                    final2.add(combined_str)

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

        intersect.final.append(final1)
        intersect.final.append(final2)

        return intersect

    def is_empty(self):
        print("Is_empty not implemented yet for Buchi automata")
        return None

    def simulations_preorder(self):
        print("Simulations not implemented yet for Buchi automata")
        return None

    def is_included(self, other):
        print("Inclusion not implemented yet for Buchi automata")
        return None

    def get_deterministic_transitions(self, state_group):
        print("Simulations not implemented yet for Buchi automata")
        return None

    def post_antichain(self, other, pair):
        print("Antichains not implemented yet for Buchi automata")
        return None
