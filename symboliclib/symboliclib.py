"""
Main module of the library containing method main

Copyright (c) 2017  Michaela Bielikova <xbieli06@stud.fit.vutbr.cz>
"""

from __future__ import print_function
from symbolic_parser import parse


def wait(msg):
    input("Press Enter to go to function:\n" + msg + "\n")


def test_operations_automata(filename, filename2):
    """
    Test available operations for symbolic or classic finite automata
    :param filename: filename of first automaton
    :param filename2: filename of second automaton
    """
    wait(filename + " load")
    automaton = parse(filename)
    automaton.print_automaton()

    wait(filename + " reverse")
    result = automaton.reverse()
    result.print_automaton()

    wait(filename + " complement")
    result = automaton.complement()
    result.print_automaton()

    wait(filename + " remove epsilon")
    result = automaton.remove_epsilon()
    result.print_automaton()

    wait(filename + " determinize")
    result = automaton.determinize()
    result.print_automaton()

    wait(filename + " minimize")
    result = automaton.minimize()
    result.print_automaton()

    wait(filename + " compute simulations relation")
    print(automaton.simulations_preorder())

    wait(filename + " transform to classic")
    result = automaton.to_lfa()
    result.print_automaton()

    wait(filename + " transform to complete")
    result = automaton.get_complete()
    result.print_automaton()

    wait(filename2 + " load")
    automaton2 = parse(filename2)
    automaton2.print_automaton()

    wait(filename + " " + filename2 + " intersection")
    result = automaton.intersection(automaton2)
    result.print_automaton()

    wait(filename + " " + filename2 + " union")
    result = automaton.union(automaton2)
    result.print_automaton()

    wait(filename + " " + filename2 + " inclusion simple")
    result = automaton.is_included_simple(automaton2)
    print(result)

    wait(filename + " " + filename2 + " inclusion")
    result = automaton.is_included(automaton2)
    print(result)

    wait(filename + " " + filename2 + " inclusion antichain")
    result = automaton.is_included_antichain(automaton2)
    print(result)

    wait(filename + " " + filename2 + " equality")
    result = automaton.is_equivalent(automaton2)
    print(result)

if __name__ == '__main__':
    test_operations_automata("./test/symbolic_test1", "./test/symbolic_test2")
