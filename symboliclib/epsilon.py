"""
Class representing epsilon
"""
import abc


class Epsilon:
    """
    Class representing epsilon
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.is_epsilon = True

    def __str__(self):
        return ""

    def __repr__(self):
        return ""

    def __eq__(self, other):
        if other.is_epsilon:
            return True
        return False

    def __hash__(self):
        return hash(self.is_epsilon)
