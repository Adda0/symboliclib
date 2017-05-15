"""
Parser of in_notin predicates

Copyright (c) 2017  Michaela Bielikova <xbieli06@stud.fit.vutbr.cz>
"""
from in_notin import InNotin


def parsePredicate(pred, automaton_type=""):
    """
    Parse one predicate string
    :param pred: predicate to parse
    :param automaton_type: compatibility with transducer parser
    :return: predicate object
    """
    result = InNotin()
    if "not_in" in pred:
        result.type = "not_in"
    else:
        result.type = "in"
    sym = pred.split("{")[1]
    sym = sym.split("}")[0]
    result.symbols = set(sorted(sym.split(",")))

    return result
