"""
Parsr for predicate letter - clssic finite automata symbol

Copyright (c) 2017  Michaela Bielikova <xbieli06@stud.fit.vutbr.cz>
"""
from letter import Letter


def parsePredicate(pred, automaton_type=""):
    """
    Parses given predicate string
    :param pred: predicate string
    :param automaton_type: compatibility with transducer parser
    :return: predicate object
    """
    result = Letter()
    result.symbol = pred

    return result
