"""
Transducer predicate class and parser
has input and output predicate and defines operations with them

Copyright (c) 2017  Michaela Bielikova <xbieli06@stud.fit.vutbr.cz>
"""
import abc
import random
from predicate_interface import PredicateInterface


class TransPred(PredicateInterface):
    """
    Transducer predicate class
    represents a transducer label with input and output predicates

    Attributes:
        input       input predicate
        output      output predicate
        identity    flag if the label represents identity
    """
    def __init__(self):
        self.input = None
        self.output = None
        self.identity = False

    def __str__(self):
        if self.identity:
            return "@" + str(self.input) + "/@" + str(self.output)
        else:
            return str(self.input) + "/" + str(self.output)

    def __repr__(self):
        if self.identity:
            return "@" + str(self.input) + "/@" + str(self.output)
        else:
            return str(self.input) + "/" + str(self.output)

    def __eq__(self, other):
        return (self.identity, self.input, self.output) == (other.identity, other.input, other.output)

    def __hash__(self):
        return hash((self.identity, str(self.input), str(self.output)))

    @abc.abstractmethod
    def complement(self):
        """
        Predicate negation
        :return: negation of given predicate
        """
        result = TransPred()
        result.identity = self.identity
        result.input = self.input.complement()
        result.output = self.output.complement()
        return result

    @abc.abstractmethod
    def conjunction(self, predicate):
        """
        Predicate conjunction
        :param predicate: second predicate
        :return: conjunction of two predicates
        """
        result = TransPred()
        if self.identity or predicate.identity:
            result.identity = True
        else:
            result.identity = False

        if result.identity:
            identic_input = self.input.conjunction(predicate.input)
            identic_output = self.output.conjunction(predicate.output)
            identic = identic_input.conjunction(identic_output)
            result.input = identic
            result.output = identic
        else:
            result.input = self.input.conjunction(predicate.input)
            result.output = self.output.conjunction(predicate.output)

        return result

    @abc.abstractmethod
    def disjunction(self, predicate):
        """
        Predicate disjunction
        :param predicate: second predicate
        :return: disjunction of two predicates
        """
        result = TransPred()

        if self.identity or predicate.identity:
            result.identity = True
        else:
            result.identity = False

        if result.identity:
            identic_input = self.input.disjunction(predicate.input)
            identic_output = self.output.disjunction(predicate.output)
            identic = identic_input.conjunction(identic_output)
            result.input = identic
            result.output = identic
        else:
            result.input = self.input.disjunction(predicate.input)
            result.output = self.output.disjunction(predicate.output)

        return result

    @abc.abstractmethod
    def is_equal(self, predicate):
        """
        Checks whether the given predicates are equal
        :param predicate: second predicate
        :return: bool
        """
        if self.identity != predicate.identity:
            # if every predicate has exactly one symbol, they can be equal even if their .identity is not the same
            if len(self.input) != 1 or len(self.output) != 1 or len(predicate.input) != 1 or len(predicate.output) != 1:
                return False
        if not self.input.is_equal(predicate.input):
            return False
        if not self.output.is_equal(predicate.output):
            return False

        return True

    @abc.abstractmethod
    def is_subset(self, predicate):
        """
        Checks whether the given predicate represent a subset of the second one
        :param predicate: second predicate
        :return: bool
        """
        if self.identity != predicate.identity:
            if predicate.identity and not self.is_equal(predicate):
                return False
        if not self.input.is_subset(predicate.input):
            return False
        if not self.output.is_subset(predicate.output):
            return False

        return True

    @abc.abstractmethod
    def is_satisfiable(self):
        """
        Checks whether the given predicate is satisfiable
        :return: bool
        """
        if not self.input.is_satisfiable():
            return False
        if not self.output.is_satisfiable():
            return False

        return True

    def combine(self, other):
        """
        Creates composition of two given labels
        :param other: the second predicate
        :return: composed predicate
        """
        result = TransPred()
        if self.identity or result.identity:
            result.identity = True
            identic = self.input.conjunction(other.output)
            result.input = identic
            result.output = identic
        else:
            result.identity = False
            result.input = self.input
            result.output = other.output
        return result

    def translates(self, a, b):
        """
        Checks whether predicates translates symbol a to symbol b
        :param a: the input symbol
        :param b: the output symbol
        :return: bool
        """
        if self.identity:
            if self.input.has_letter(a) and a == b:
                return True
        else:
            if self.input.has_letter(a) and self.output.has_letter(b):
                return True
        return False

    def translate(self, a, alphabet):
        """
        Translates symbol a to another symbol
        :param a: the input symbol
        :param alphabet: alphabet of the automaton
        :return: translation fo the symbol
        """
        if self.input.has_letter(a):
            if self.identity:
                return a
            else:
                for symbol in alphabet:
                    if self.output.has_letter(symbol):
                        return symbol
        else:
            return False


def parsePredicate(pred, automaton_type):
    """
    Parses given predicate
    :param pred: predicate string
    :param automaton_type: type of the automaton
    :return: predicate object
    """
    result = TransPred()
    if pred[0] == "@":
        result.identity = True
        pred = pred.replace("@", "")
    pred_parts = pred.split("/")
    if automaton_type == "INT":
        from in_notin_parser import parsePredicate as parsePr
    elif automaton_type == "LT":
        from letter_parser import parsePredicate as parsePr
    else:
        print("Unsupported transducer type.")
        exit(-1)
    result.input = parsePr(pred_parts[0])
    result.output = parsePr(pred_parts[1])

    return result
