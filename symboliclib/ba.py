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

    def post(self, transitions, state_set, symbol):
        post = set()
        for state in state_set:
            if state in transitions:
                if symbol in transitions[state]:
                    for endstate in transitions[state][symbol]:
                        post.add(endstate)
        return post


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

    def union(self, other):
        print("Union not implemented yet for Buchi automata")
        return None

    def intersection(self, a2):
        print("Intersection not implemented yet for Buchi automata")
        return None

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
