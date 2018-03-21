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
        """
        Buchi semideterministic automaton complementation
        Using NCSB algorithm
        Algorithm can be found here: https://www.fi.muni.cz/~xstrejc/publications/tacas2016coSDBA_preprint.pdf
        :return: complement
        """
        # make automaton complete
        self = self.get_complete()
        complete = True

        # split automaton compoments to Q1, Q2, delta1, delta2, delta_t
        self.split_components()
        self.fix_final_states()

        # prepare first ncsb set
        n = self.start.intersection(self.q1)
        c = self.start.intersection(self.q2)
        s = set()
        b = self.start.intersection(self.q2)
        queue = list()
        start_set = {"n": n, "c": c, "s": s, "b": b}
        queue.append(start_set)
        done = set()

        # prepare complements
        complement = BA()
        complement.alphabet = deepcopy(self.alphabet)
        complement.start.add(self.get_text_label(start_set))
        complement.final.append(set())
        if b == set():
            complement.final[0].add(self.get_text_label(start_set))

        # loop through reached ncsb sets
        while len(queue):
            state_set = queue.pop()
            text = self.get_text_label(state_set)
            if text in done:
                continue
            done.add(text)

            complement.states.add(text)

            for symbol in self.alphabet:
                n2 = set()
                c2 = set()
                s2 = set()
                b2 = set()
                possible_s = set()
                block = False

                # N2 = delta1(N,a)
                n2 = self.post(self.delta1, state_set["n"], symbol)
                # C2 >= delta_t(N,a)
                c2 = self.post(self.deltat, state_set["n"], symbol)

                # C2 <= delta(N,a) U (delta(N,a) ^ F)
                # possible_s - states that can be transferred to S, or can stay in C, to be decided later
                for state in state_set["c"]:
                    ss = set()
                    ss.add(state)
                    post_c = self.post(self.delta2, ss, symbol)
                    for endstate in post_c:
                        if self.is_final(state) and not self.is_final(endstate):
                            possible_s.add(endstate)
                        else:
                            c2.add(endstate)

                # S >= delta(S,a)
                post_s = self.post(self.delta2, state_set["s"], symbol)
                for endstate in post_s:
                    if not self.is_final(endstate):
                        if endstate in c2:
                            # C >= delta2(C,a), S >= delta2(S,a), S ^ C = {}
                            # => wrong branch, blocked
                            block = True
                        else:
                            s2.add(endstate)
                    else:
                        # if a state reached in S is final, this branch is blocked
                        block = True

                if not block:
                    # decide which states stay in S and which in C
                    if len(possible_s):
                        posibilities = self.powerset(possible_s)
                        # generate all possible combinations
                        for comb in posibilities:
                            ps = set()
                            for c in comb:
                                ps.add(c)

                            possible_c = c2 - ps
                            possible_s = s2.union(ps)

                            # a run can be safe or unsafe, not both
                            if len(possible_c.intersection(possible_s)) == 0:
                                # if automaton is complete, state ({},{},{},{}) is not possible
                                if not complete or (len(n2) or len(possible_c) or len(possible_s) or len(b2)):
                                    new_set = {"n": n2, "c": possible_c, "s": possible_s, "b": b2}
                                    self.add_transitions_generate_b(complement, self.delta2, queue, done, new_set, b, state_set, symbol)

                            possible_c = c2.union(ps)
                            possible_s = s2
                            b2 = set()
                            # a run can be safe or unsafe, not both
                            if len(possible_c.intersection(possible_s)) == 0:
                                # if automaton is complete, state ({},{},{},{}) is not possible
                                if not complete or (len(n2) or len(possible_c) or len(possible_s) or len(b2)):
                                    new_set = {"n": n2, "c": possible_c, "s": possible_s, "b": b2}
                                    self.add_transitions_generate_b(complement, self.delta2, queue, done, new_set, b, state_set, symbol)

                    else:
                        # if automaton is complete, state ({},{},{},{}) is not possible
                        if not complete or (len(n2) or len(c2) or len(s2) or len(b2)):
                            self.add_transitions_generate_b(complement, self.delta2, queue, done, {"n": n2, "c": c2, "s": s2, "b": b2},
                                                     b, state_set, symbol)

        return complement

    def post(self, transitions, state_set, symbol):
        post = set()
        for state in state_set:
            if state in transitions:
                if symbol in transitions[state]:
                    for endstate in transitions[state][symbol]:
                        post.add(endstate)
        return post

    def complement_ncsb_onthefly(self):
        """
        On the fly semideterministic buchi automaton complementation
        Algorithm can be found here: https://www.fi.muni.cz/~xstrejc/publications/tacas2016coSDBA_preprint.pdf
        :return: complement
        """
        # make automaton complete
        self = self.get_complete()
        complete = True
        # prepare first ncsb set
        n = self.start - self.final
        c = self.start.intersection(self.final)
        s = set()
        b = self.start.intersection(self.final)
        queue = list()
        start_set = {"n": n, "c": c, "s": s, "b": b}
        queue.append(start_set)
        done = set()

        # prepare complement
        complement = BA()
        complement.alphabet = deepcopy(self.alphabet)
        complement.start.add(self.get_text_label(start_set))
        complement.final.append(set())
        if b == set():
            complement.final[0].add(self.get_text_label(start_set))

        # loop through reached ncsb sets
        while len(queue):
            state_set = queue.pop()
            text = self.get_text_label(state_set)
            if text in done:
                continue
            done.add(text)

            complement.states.add(text)

            for symbol in self.alphabet:
                n2 = set()
                c2 = set()
                s2 = set()
                b2 = set()
                possible_s = set()
                block = False
                # N2 = delta(N,a)-F ; C2 <= delta(C,a) U (delta(N,a) ^ F)
                post_n = self.post(self.transitions, state_set["n"], symbol)
                for endstate in post_n:
                    if self.is_final(endstate):
                        c2.add(endstate)
                    else:
                        n2.add(endstate)

                # C2 <= delta(C,a) U (delta(N,a) ^ F)
                # possible_s - states that can be transferred to S, or can stay in C, to be decided later
                for state in state_set["c"]:
                    ss = set()
                    ss.add(state)
                    post_c = self.post(self.transitions, ss, symbol)
                    for endstate in post_c:
                        if self.is_final(state) and not self.is_final(endstate):
                            possible_s.add(endstate)
                        else:
                            c2.add(endstate)

                # S >= delta(S,a)
                post_s = self.post(self.transitions, state_set["s"], symbol)
                for endstate in post_s:
                    if not self.is_final(endstate):
                        if endstate in c2:
                            # C >= delta2(C,a), S >= delta2(S,a), S ^ C = {}
                            # => wrong branch, blocked
                            block = True
                        else:
                            s2.add(endstate)
                    # if a state reached in S is final, this branch is blocked
                    else:
                        block = True

                if not block:
                # decide which states stay in S and which in C
                    if len(possible_s):
                        posibilities = self.powerset(possible_s)
                        # generate all possible combinations
                        for comb in posibilities:
                            ps = set()
                            for c in comb:
                                ps.add(c)

                            possible_c = c2 - ps
                            possible_s = s2.union(ps)
                            # a run can be safe or unsafe, not both
                            if len(possible_c.intersection(possible_s)) == 0:
                                # if automaton is complete, state ({},{},{},{}) is not possible
                                if not complete or (len(n2) or len(possible_c) or len(possible_s) or len(b2)):
                                    new_set = {"n": n2, "c": possible_c, "s": possible_s, "b": b2}
                                    self.add_transitions_generate_b(complement, self.transitions, queue, done, new_set, b, state_set, symbol)

                            possible_c = c2.union(ps)
                            possible_s = s2
                            b2 = set()
                            # a run can be safe or unsafe, not both
                            if len(possible_c.intersection(possible_s)) == 0:
                                # if automaton is complete, state ({},{},{},{}) is not possible
                                if not complete or (len(n2) or len(possible_c) or len(possible_s) or len(b2)):
                                    new_set = {"n": n2, "c": possible_c, "s": possible_s, "b": b2}
                                    self.add_transitions_generate_b(complement, self.transitions, queue, done, new_set, b, state_set, symbol)

                    else:
                        # if automaton is complete, state ({},{},{},{}) is not possible
                            if not complete or (len(n2) or len(c2) or len(s2) or len(b2)):
                                self.add_transitions_generate_b(complement, self.transitions, queue, done, {"n": n2, "c": c2, "s": s2, "b": b2}, b, state_set, symbol)

        return complement

    def complement_ncsb_lazy(self):
        """
        Semideterministic buchi automaton complementation
        Algorithm NCSB lazy
        :return: complement
        """
        # make automaton complete
        self = self.get_complete()
        complete = True

        # split automaton compoments to Q1, Q2, delta1, delta2, delta_t
        self.split_components()
        self.fix_final_states()

        # prepare first ncsb set
        n = self.start.intersection(self.q1)
        c = self.start.intersection(self.q2)
        s = set()
        b = self.start.intersection(self.q2)
        queue = list()
        start_set = {"n": n, "c": c, "s": s, "b": b}
        queue.append(start_set)
        done = set()

        # prepare complements
        complement = BA()
        complement.alphabet = deepcopy(self.alphabet)
        complement.start.add(self.get_text_label(start_set))
        complement.final.append(set())
        if b == set():
            complement.final[0].add(self.get_text_label(start_set))

        # loop through reached ncsb sets
        while len(queue):
            state_set = queue.pop()
            text = self.get_text_label(state_set)

            if text in done:
                continue

            done.add(text)
            complement.states.add(text)

            n2 = set()
            c2 = set()
            s2 = set()
            b2 = set()
            possible_s = set()
            possible_bs = set()
            block = False


            # B = {}
            if state_set["b"] == set():
                for symbol in self.alphabet:
                    # N2 = delta1(N,a)
                    n2 = self.post(self.delta1, state_set["n"], symbol)
                    # C2 >= delta_t(N,a)
                    c2 = self.post(self.deltat, state_set["n"], symbol)

                    # C2 <= delta(N,a) U (delta(N,a) ^ F)
                    # possible_s - states that can be transferred to S, or can stay in C, to be decided later
                    for state in state_set["c"]:
                        ss = set()
                        ss.add(state)
                        post_c = self.post(self.delta2, ss, symbol)
                        for endstate in post_c:
                            if self.is_final(state) and not self.is_final(endstate):
                                possible_s.add(endstate)
                            else:
                                c2.add(endstate)

                    # S >= delta(S,a)
                    post_s = self.post(self.delta2, state_set["s"], symbol)
                    for endstate in post_s:
                        if not self.is_final(endstate):
                            if endstate in c2:
                                # C >= delta2(C,a), S >= delta2(S,a), S ^ C = {}
                                # => wrong branch, blocked
                                block = True
                            else:
                                s2.add(endstate)
                        else:
                            block = True

                    if not block:
                        # decide which states stay in S and which in C
                        if len(possible_s):
                            posibilities = self.powerset(possible_s)
                            # generate all possible combinations
                            for comb in posibilities:
                                ps = set()
                                for c in comb:
                                    ps.add(c)

                                possible_c = c2 - ps
                                possible_s = s2.union(ps)

                                # a run can be safe or unsafe, not both
                                if len(possible_c.intersection(possible_s)) == 0:
                                    # if automaton is complete, state ({},{},{},{}) is not possible
                                    if not complete or (len(n2) or len(possible_c) or len(possible_s) or len(b2)):
                                        new_set = {"n": n2, "c": possible_c, "s": possible_s, "b": b2}
                                        self.add_transitions_generate_b(complement, self.delta2, queue, done, new_set, b, state_set, symbol)

                                possible_c = c2.union(ps)
                                possible_s = s2
                                b2 = set()
                                # a run can be safe or unsafe, not both
                                if len(possible_c.intersection(possible_s)) == 0:
                                    # if automaton is complete, state ({},{},{},{}) is not possible
                                    if not complete or (len(n2) or len(possible_c) or len(possible_s) or len(b2)):
                                        new_set = {"n": n2, "c": possible_c, "s": possible_s, "b": b2}
                                        self.add_transitions_generate_b(complement, self.delta2, queue, done, new_set, b, state_set, symbol)

                        else:
                            # if automaton is complete, state ({},{},{},{}) is not possible
                            if not complete or (len(n2) or len(c2) or len(s2) or len(b2)):
                                self.add_transitions_generate_b(complement, self.delta2, queue, done, {"n": n2, "c": c2, "s": s2, "b": b2},
                                                     b, state_set, symbol)
            # B =/= {}
            else:
                for symbol in self.alphabet:
                    # N2 = delta1(N,a)
                    n2 = self.post(self.delta1, state_set["n"], symbol)
                    # C2 >= delta_t(N,a)
                    c2 = self.post(self.deltat, state_set["n"], symbol)

                    # C2 >= delta_2(C,a)
                    for state in state_set["c"]:
                        ss = set()
                        ss.add(state)
                        post_c = self.post(self.delta2, ss, symbol)
                        for endstate in post_c:
                            c2.add(endstate)

                    # S >= delta2(S,a)
                    post_s = self.post(self.delta2, state_set["s"], symbol)
                    for endstate in post_s:
                        if not self.is_final(endstate):
                            s2.add(endstate)
                        else:
                            # if a state reached in S is final, this branch is blocked
                            block = True

                    if block:
                        continue

                    # B >= delta2(B-F,a)
                    b2 = self.post(self.delta2, state_set["b"] - self.final[0], symbol)
                    # possible_bs - states that can be transferred to S, or can stay in B, to be decided later
                    possible_bs = self.post(self.delta2, state_set["b"].intersection(self.final[0]), symbol)

                    # no run can be in B and S at the same time -> block branch
                    if len(b2.intersection(s2)):
                        continue

                    # decide which states stay in S and which in B
                    if len(possible_bs):
                        # generate all possible combinations
                        posibilities = self.powerset(possible_bs)
                        original_c = deepcopy(c2)
                        for comb in posibilities:
                            ps = set()
                            for c in comb:
                                ps.add(c)

                            possible_b = b2 - ps
                            possible_s = s2.union(ps)
                            # if automaton is complete, state ({},{},{},{}) is not possible
                            if not complete or (len(n2) or len(c2) or len(possible_s) or len(possible_b)):
                                new_set = {"n": n2, "c": original_c - possible_s, "s": possible_s, "b": possible_b}
                                self.add_transition(complement, state_set, symbol, new_set, queue, done)

                            possible_b = b2.union(ps)
                            possible_s = s2
                            b2 = set()
                            # if automaton is complete, state ({},{},{},{}) is not possible
                            if not complete or (len(n2) or len(c2) or len(possible_s) or len(possible_b)):
                                new_set = {"n": n2, "c": original_c - possible_s, "s": possible_s, "b": possible_b}
                                self.add_transition(complement, state_set, symbol, new_set, queue, done)

                    else:
                        # if automaton is complete, state ({},{},{},{}) is not possible
                        if not complete or (len(n2) or len(c2) or len(s2) or len(b2)):
                            self.add_transition(complement, state_set, symbol, {"n": n2, "c": c2, "s": s2, "b": b2}, queue, done)

        return complement

    def complement_ncsb_early_flush(self):
        """
        Buchi semideterministic automaton complementation
        Using NCSB algorithm with early flush modification
        :return: complement
        """
        # make automaton complete
        self = self.get_complete()
        complete = True

        # split automaton compoments to Q1, Q2, delta1, delta2, delta_t
        self.split_components()
        self.fix_final_states()

        # prepare first ncsb set
        n = self.start.intersection(self.q1)
        c = self.start.intersection(self.q2)
        s = set()
        b = self.start.intersection(self.q2)
        f = False   # tells if the state is final
        queue = list()
        start_set = {"n": n, "c": c, "s": s, "b": b, "f": f}
        queue.append(start_set)
        done = set()

        # prepare complements
        complement = BA()
        complement.alphabet = deepcopy(self.alphabet)
        complement.start.add(self.get_text_label_early_flush(start_set))
        complement.final.append(set())

        # loop through reached ncsb sets
        while len(queue):
            state_set = queue.pop()
            text = self.get_text_label_early_flush(state_set)
            if text in done:
                continue
            done.add(text)

            complement.states.add(text)

            for symbol in self.alphabet:
                n2 = set()
                c2 = set()
                s2 = set()
                b2 = set()
                possible_s = set()
                block = False

                # N2 = delta1(N,a)
                n2 = self.post(self.delta1, state_set["n"], symbol)
                # C2 >= delta_t(N,a)
                c2 = self.post(self.deltat, state_set["n"], symbol)

                # C2 <= delta(N,a) U (delta(N,a) ^ F)
                # possible_s - states that can be transferred to S, or can stay in C, to be decided later
                for state in state_set["c"]:
                    ss = set()
                    ss.add(state)
                    post_c = self.post(self.delta2, ss, symbol)
                    for endstate in post_c:
                        if self.is_final(state) and not self.is_final(endstate):
                            possible_s.add(endstate)
                        else:
                            c2.add(endstate)

                # S >= delta(S,a)
                post_s = self.post(self.delta2, state_set["s"], symbol)
                for endstate in post_s:
                    if not self.is_final(endstate):
                        if endstate in c2:
                            # C >= delta2(C,a), S >= delta2(S,a), S ^ C = {}
                            # => wrong branch, blocked
                            block = True
                        else:
                            s2.add(endstate)
                    else:
                        # if a state reached in S is final, this branch is blocked
                        block = True

                if not block:
                    # decide which states stay in S and which in C
                    if len(possible_s):
                        posibilities = self.powerset(possible_s)
                        # generate all possible combinations
                        for comb in posibilities:
                            ps = set()
                            for c in comb:
                                ps.add(c)

                            possible_c = c2 - ps
                            possible_s = s2.union(ps)

                            # a run can be safe or unsafe, not both
                            if len(possible_c.intersection(possible_s)) == 0:
                                # if automaton is complete, state ({},{},{},{}) is not possible
                                if not complete or (len(n2) or len(possible_c) or len(possible_s) or len(b2)):
                                    new_set = {"n": n2, "c": possible_c, "s": possible_s, "b": b2}
                                    self.add_transitions_generate_b_early_flush(complement, self.delta2, queue, done, new_set, b, state_set, symbol)

                            possible_c = c2.union(ps)
                            possible_s = s2
                            b2 = set()
                            # a run can be safe or unsafe, not both
                            if len(possible_c.intersection(possible_s)) == 0:
                                # if automaton is complete, state ({},{},{},{}) is not possible
                                if not complete or (len(n2) or len(possible_c) or len(possible_s) or len(b2)):
                                    new_set = {"n": n2, "c": possible_c, "s": possible_s, "b": b2}
                                    self.add_transitions_generate_b_early_flush(complement, self.delta2, queue, done, new_set, b, state_set, symbol)

                    else:
                        # if automaton is complete, state ({},{},{},{}) is not possible
                        if not complete or (len(n2) or len(c2) or len(s2) or len(b2)):
                            self.add_transitions_generate_b_early_flush(complement, self.delta2, queue, done, {"n": n2, "c": c2, "s": s2, "b": b2},
                                                     b, state_set, symbol)

        return complement

    def add_transitions_generate_b(self, complement, trans, queue, done, new_set, b, state_set, symbol):
        if len(b) > 0:
            post_b = self.post(trans, state_set["b"], symbol)
            for endstate in post_b:
                if endstate in new_set["c"]:
                    new_set["b"].add(endstate)
        else:
            new_set["b"] = deepcopy(new_set["c"])

        self.add_transition(complement, state_set, symbol, new_set, queue, done)

    def add_transition(self, complement, state_set, symbol, new_set, queue, done):
        text = self.get_text_label(state_set)
        new_text = self.get_text_label(new_set)
        complement.transitions = self.add_trans(complement.transitions, text, symbol, new_text)
        if len(new_set["b"]) == 0:
            complement.final[0].add(new_text)
        if new_text not in done and new_set not in queue:
            queue.append(new_set)

    def add_transitions_generate_b_early_flush(self, complement, trans, queue, done, new_set, b, state_set, symbol):
        alfa = set()
        post_b = self.post(trans, state_set["b"], symbol)
        for endstate in post_b:
            if endstate in new_set["c"]:
                alfa.add(endstate)

        if len(alfa):
            new_set["b"] = alfa
            new_set["f"] = False
        else:
            new_set["b"] = deepcopy(new_set["c"])
            new_set["f"] = True

        text = self.get_text_label_early_flush(state_set)
        new_text = self.get_text_label_early_flush(new_set)
        complement.transitions = self.add_trans(complement.transitions, text, symbol, new_text)
        if new_set["f"]:
            complement.final[0].add(new_text)
        if new_text not in done and new_set not in queue:
            queue.append(new_set)

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
    def get_text_label(state_set):
        text = ("({" + ",".join(sorted(state_set["n"])) + "},{" +
                ",".join(sorted(state_set["c"])) + "},{" +
                ",".join(sorted(state_set["s"])) + "},{" +
                ",".join(sorted(state_set["b"])) + "})")
        return text

    @staticmethod
    def get_text_label_early_flush(state_set):
        if state_set["f"]:
            text = ("({" + ",".join(sorted(state_set["n"])) + "},{" +
                    ",".join(sorted(state_set["c"])) + "},{" +
                    ",".join(sorted(state_set["s"])) + "},{" +
                    ",".join(sorted(state_set["b"])) + "},T)")
        else:
            text = ("({" + ",".join(sorted(state_set["n"])) + "},{" +
                    ",".join(sorted(state_set["c"])) + "},{" +
                    ",".join(sorted(state_set["s"])) + "},{" +
                    ",".join(sorted(state_set["b"])) + "},F)")
        return text

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
