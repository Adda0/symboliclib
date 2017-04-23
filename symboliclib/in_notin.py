"""
in and not_in predicates class
"""

import abc
from predicate_interface import PredicateInterface


class InNotin(PredicateInterface):
    """
    in and not_in predicates class

    Attributes:
        symbols     set of symbols
        type        type of predicate - in or not_in
        is_epsilon  flag whether the predicate represents epsilon
    """

    def __init__(self):
        self.symbols = set()
        self.type = ""
        self.is_epsilon = False

    def __str__(self):
        return self.type + "{" + ",".join(sorted(self.symbols)) + "}"

    def __repr__(self):
        return self.type + "{" + ",".join(sorted(self.symbols)) + "}"

    def __eq__(self, other):
        return (self.type, set(sorted(self.symbols))) == (other.type, set(sorted(other.symbols)))

    def __hash__(self):
        return hash((self.type, str(sorted(self.symbols))))

    @abc.abstractmethod
    def negation(self):
        """
        Predicate negation
        :return: negation of given predicate
        """
        result = InNotin()
        result.symbols = set(sorted(self.symbols.copy()))
        if self.type == "not_in":
            result.type = "in"
        else:
            result.type = "not_in"
        return result

    @abc.abstractmethod
    def conjunction(self, predicate):
        """
        Predicate conjunction
        :param predicate: second predicate
        :return: conjunction of two predicates
        """
        result = InNotin()

        if self.type == "not_in":
            if predicate.type == "not_in":
                result.type = "not_in"
                result.symbols = self.symbols.union(predicate.symbols)
            else:
                result.type = "in"
                result.symbols = predicate.symbols - self.symbols
        else:
            if predicate.type == "not_in":
                result.type = "in"
                result.symbols = self.symbols - predicate.symbols
            else:
                result.type = "in"
                result.symbols = self.symbols.intersection(predicate.symbols)

        result.symbols = set(sorted(result.symbols))
        return result

    @abc.abstractmethod
    def disjunction(self, predicate):
        """
        Predicate disjunction
        :param predicate: second predicate
        :return: disjunction of two predicates
        """
        result = InNotin()

        if self.type == "not_in":
            if predicate.type == "not_in":
                result.type = "not_in"
                result.symbols = self.symbols.intersection(predicate.symbols)
            else:
                result.type = "not_in"
                result.symbols = self.symbols - predicate.symbols
        else:
            if predicate.type == "not_in":
                result.type = "not_in"
                result.symbols = predicate.symbols - self.symbols
            else:
                result.type = "in"
                result.symbols = self.symbols.union(predicate.symbols)

        result.symbols = set(sorted(result.symbols))
        return result

    @abc.abstractmethod
    def is_equal(self, predicate):
        """
        Checks whether the given predicates are equal
        :param predicate: second predicate
        :return: bool
        """
        if self.type == predicate.type and self.symbols == predicate.symbols:
            return True
        else:
            return False

    @abc.abstractmethod
    def is_subset(self, predicate):
        """
        Checks whether the given predicate represent a subset of the second one
        :param predicate: second predicate
        :return: bool
        """
        if self.type == "in" and predicate.type == "in" and self.symbols <= predicate.symbols:
            return True
        if self.type == "not_in" and predicate.type == "not_in" and self.symbols >= predicate.symbols:
            return True

        return False

    @abc.abstractmethod
    def is_satisfiable(self):
        """
        Checks whether the given predicate is satisfiable
        :return: bool
        """
        if self.type == "in" and len(self.symbols) == 0:
            return False

        return True

    @abc.abstractmethod
    def get_universal(self):
        """
        Creates a predicate representing the whole alphabet
        :return: predicate object
        """
        result = InNotin()

        result.type = "not_in"
        result.symbols = set()

        return result

    @abc.abstractmethod
    def has_letter(self, letter):
        """
        Checks whether the given symbol belongs to the predicate
        :param letter: checked symbol
        :return: bool
        """
        if self.type == "in":
            if letter in self.symbols:
                return True
        else:
            if letter not in self.symbols:
                return True

        return False
