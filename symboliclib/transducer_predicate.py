"""
Transducer predicate class and parser
has input and output predicate and defines operations with them
"""
import abc
import random
from predicate_interface import PredicateInterface


class TransPred(PredicateInterface):
    """
    Transducer predicate class
    has input and output predicate and defines operations with them
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
        """Return complement of given predicate"""
        result = TransPred()
        result.identity = self.identity
        result.input = result.input.complement()
        result.output = result.output.complement()
        return result

    @abc.abstractmethod
    def conjunction(self, predicate):
        """Return conjunction of given predicates
        Return disjunction of given predicates"""
        result = TransPred()
        if self.identity or predicate.identity:
            result.identity = True
        else:
            result.identity = False

        if result.identity:
            identic_input = result.input.conjunction(predicate.input)
            identic_output = result.output.conjunction(predicate.output)
            identic = identic_input.conjunction(identic_output)
            result.input = identic
            result.output = identic
        else:
            result.input = result.input.conjunction(predicate.input)
            result.output = result.output.conjunction(predicate.output)

        return result

    @abc.abstractmethod
    def disjunction(self, predicate):
        """Return disjunction of given predicates"""
        result = TransPred()

        if self.identity or predicate.identity:
            result.identity = True
        else:
            result.identity = False

        if result.identity:
            identic_input = result.input.disjunction(predicate.input)
            identic_output = result.output.disjunction(predicate.output)
            identic = identic_input.conjunction(identic_output)
            result.input = identic
            result.output = identic
        else:
            result.input = result.input.disjunction(predicate.input)
            result.output = result.output.disjunction(predicate.output)

        return result

    @abc.abstractmethod
    def is_equal(self, predicate):
        """Checks whether the given predicates are equal
        Returns true or false"""
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
        """is_subset(predicate) Checks whether self is subset of predicate
        Returns true or false"""
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
        """Checks whether the given predicate is satisfiable
        Returns true or false"""
        if not self.input.is_satisfiable():
            return False
        if not self.output.is_satisfiable():
            return False

        return True

    def combine(self, other):
        """ For composition
        Returns composed label"""
        result = TransPred()
        if self.identity or result.identity:
            result.identity = True
            identic = self.input.conunction(other.output)
            result.input = identic
            result.output = identic
        else:
            result.identity = False
            result.input = self.input
            result.output = other.output
        return result

    def translates(self, a, b):
        """Checks whether the given predicate is satisfiable
        Returns true or false"""
        if self.identity:
            if self.input.has_letter(a) and a == b:
                return True
        else:
            if self.input.has_letter(a) and self.output.has_letter(b):
                return True
        return False

    def translate(self, a, alphabet):
        """Checks whether the given predicate is satisfiable
        Returns true or false"""
        if self.input.has_letter(a):
            if self.identity:
                return a
            else:
                return random.choice(list(self.output.to_letters(alphabet)))
        else:
            return False


def parsePredicate(pred, automaton_type):
    """
    Parses given predicate
    :param pred:
    :param automaton_type:
    :return:
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
