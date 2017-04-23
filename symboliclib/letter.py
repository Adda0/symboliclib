"""
Symbol predicates class
"""
import abc
from predicate_interface import PredicateInterface


class Letter(PredicateInterface):
    """
    Symbol predicates class

    Attributes:
        symbol      symbol represented by the predicate
        is_epsilon  flag whether the predicate represents epsilon
    """

    def __init__(self):
        self.symbol = ""
        self.is_epsilon = False

    def __str__(self):
        return self.symbol

    def __repr__(self):
        return self.symbol

    def __eq__(self, other):
        if isinstance(other, str):
            return self.symbol == other
        return self.symbol == other.symbol

    def __hash__(self):
        return hash(self.symbol)

    @abc.abstractmethod
    def negation(self):
        """
        Predicate negation
        :return: negation of given predicate
        """
        result = Letter()
        result.symbol = ""
        return result

    @abc.abstractmethod
    def conjunction(self, predicate):
        """
        Predicate conjunction
        :param predicate: second predicate
        :return: conjunction of two predicates
        """
        result = Letter()
        if self.symbol == predicate.symbol:
            result.symbol = self.symbol
        elif self.symbol == "":
            result.symbol = predicate.symbol
        elif predicate.symbol == "":
            result.symbol = self.symbol
        else:
            result.symbol = ""
        return result

    @abc.abstractmethod
    def disjunction(self, predicate):
        """
        Predicate disjunction
        :param predicate: second predicate
        :return: disjunction of two predicates
        """
        result = Letter()
        if self.symbol == predicate.symbol:
            result.symbol = self.symbol
        elif self.symbol == "":
            result.symbol = predicate.symbol
        elif predicate.symbol == "":
            result.symbol = self.symbol
        else:
            result.symbol = ""
        return result

    @abc.abstractmethod
    def is_equal(self, predicate):
        """
        Checks whether the given predicates are equal
        :param predicate: second predicate
        :return: bool
        """
        if self.symbol == predicate.symbol:
            return True
        else:
            return False

    @abc.abstractmethod
    def is_satisfiable(self):
        """
        Checks whether the given predicate is satisfiable
        :return: bool
        """
        if self.symbol != "":
            return True
        return False

    def is_subset(self, predicate):
        """
        Checks whether the given predicate represent a subset of the second one
        :param predicate: second predicate
        :return: bool
        """
        if self.symbol == predicate.symbol:
            return True
        elif self.symbol == "":
            return True
        return False

    def create(self, symbol):
        """Checks whether the given predicate is satisfiable
        Returns true or false"""
        result = Letter()
        result.symbol = symbol

        return result

    @abc.abstractmethod
    def has_letter(self, symbol):
        """
        Checks whether the given symbol belongs to the predicate
        :param symbol: checked symbol
        :return: bool
        """
        return self.symbol == symbol
