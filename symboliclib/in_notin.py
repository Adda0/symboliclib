"""
in and not_in predicates class
"""

import abc
from predicate_interface import PredicateInterface


class InNotin(PredicateInterface):
    """
    in and not_in predicates class
    """
    __metaclass__ = abc.ABCMeta

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
    def complement(self):
        """Return complement of given predicate"""
        result = InNotin()
        result.symbols = set(sorted(self.symbols.copy()))
        if self.type == "not_in":
            result.type = "in"
        else:
            result.type = "not_in"
        return result

    @abc.abstractmethod
    def conjunction(self, predicate):
        """Return conjunction of given predicates
        Return disjunction of given predicates"""
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
        """Return disjunction of given predicates"""
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
        """Checks whether the given predicates are equal
        Returns true or false"""
        if self.type == predicate.type and self.symbols == predicate.symbols:
            return True
        else:
            return False

    @abc.abstractmethod
    def is_subset(self, predicate):
        """is_subset(predicate) Checks whether self is subset of predicate
        Returns true or false"""
        if self.type == "in" and predicate.type == "in" and self.symbols <= predicate.symbols:
            return True
        if self.type == "not_in" and predicate.type == "not_in" and self.symbols >= predicate.symbols:
            return True

        return False

    @abc.abstractmethod
    def is_satisfiable(self):
        """Checks whether the given predicate is satisfiable
        Returns true or false"""
        if self.type == "in" and len(self.symbols) == 0:
            return False

        return True

    @abc.abstractmethod
    def get_universal(self):
        """Checks whether the given predicate is satisfiable
        Returns true or false"""
        result = InNotin()

        result.type = "not_in"
        result.symbols = set()

        return result

    def has_letter(self, letter):
        if self.type == "in":
            if letter in self.symbols:
                return True
        else:
            if letter not in self.symbols:
                return True

        return False
