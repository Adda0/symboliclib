"""
Module defining Predicate Interface

contains list of methods very predicate must implement
"""

import abc


class PredicateInterface(object):
    """
    Module defining Predicate Interface
    """
    __metaclass__ = abc.ABCMeta
    is_epsilon = False

    @abc.abstractmethod
    def negation(self):
        """
        Predicate negation
        :return: negation of given predicate
        """
        return

    @abc.abstractmethod
    def conjunction(self, predicate):
        """
        Predicate conjunction
        :param predicate: second predicate
        :return: conjunction of two predicates
        """
        return

    @abc.abstractmethod
    def disjunction(self, predicate):
        """
        Predicate disjunction
        :param predicate: second predicate
        :return: disjunction of two predicates
        """
        return

    @abc.abstractmethod
    def is_equal(self, predicate):
        """
        Checks whether the given predicates are equal
        :param predicate: second predicate
        :return: bool
        """
        return

    @abc.abstractmethod
    def is_satisfiable(self):
        """
        Checks whether the given predicate is satisfiable
        :return: bool
        """
        return

    @abc.abstractmethod
    def is_subset(self, predicate):
        """
        Checks whether the given predicate represent a subset of the second one
        :param predicate: second predicate
        :return: bool
        """
        return

    @abc.abstractmethod
    def get_universal(self):
        """
        Creates a predicate representing the whole alphabet
        :return: predicate object
        """
        return

    @abc.abstractmethod
    def has_letter(self, symbol):
        """
        Checks whether the given symbol belongs to the predicate
        :param symbol: checked symbol
        :return: bool
        """
        return
