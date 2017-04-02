"""
Module defining Predicte Interface
"""

import abc


class PredicateInterface(object):
    """
    Module defining Predicate Interface
    """
    __metaclass__ = abc.ABCMeta
    is_epsilon = False

    @abc.abstractmethod
    def complement(self):
        """Return complement of given predicate"""
        return

    @abc.abstractmethod
    def conjunction(self, predicate):
        """Return conjunction of given predicates"""
        return

    @abc.abstractmethod
    def disjunction(self, predicate):
        """Return disjunction of given predicates"""
        return

    @abc.abstractmethod
    def is_equal(self, predicate):
        """Checks whether the given predicates are equal
        Returns true or false"""
        return

    @abc.abstractmethod
    def is_satisfiable(self):
        """Checks whether the given predicate is satisfiable
        Returns true or false"""
        return

    @abc.abstractmethod
    def get_universal(self):
        """Return predicate that is true for every symbol in alphabet"""
        return
