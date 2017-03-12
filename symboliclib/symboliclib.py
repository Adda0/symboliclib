"""
Just a main class
"""

from __future__ import print_function
from symbolic_parser import parse


def test_transducer_parser():
    """
    Test transducer parsing
    """
    automaton = parse("./test/trans")
    automaton.print_automaton()


def test_reduce_trans():
    """
    Test simple reduction of transitions
    """
    automaton = parse("./test/unite2")
    automaton.print_automaton()


def test_deter():
    """
    Test determinization
    """
    automaton = parse("./test/deter2")
    automaton.determinize()
    automaton.print_automaton()
    print(automaton.is_deterministic())


def test_complete():
    """
    Test complement
    """
    automaton = parse("./test/big")
    automaton.get_complete()
    automaton.print_automaton()
    print(automaton.is_deterministic())


def test_minim():
    """
    Test minimization
    """
    automaton = parse("./test/big")
    automaton.minimize()
    automaton.print_automaton()
    print(automaton.is_deterministic())


def test_simulation():
    """
    Test simulation - simulation is not working yet
    """
    automaton = parse("./test/minim")
    automaton.simulations()

    b = automaton.reversed
    b.simulations()

def test_similarity():
    """
    Test simulation - simulation is not working yet
    """
    automaton = parse("./test/minim-letter")
    efficient = automaton.efficient_similiarity()
    print("Efficient similiarity")
    print(efficient)

    simulation = automaton.simulations()
    print("Navaro simulations")
    print(simulation)


def test_intersection():
    """
    Test intersection
    """
    automaton = parse("./test/infa-intersection-1")
    automaton.print_automaton()
    automaton_b = parse("./test/infa-intersection-2")
    automaton_b.print_automaton()
    automaton_c = automaton.intersection(automaton_b)
    automaton_c.print_automaton()

def test_transducer_composition():
    """
    Test transducer composition
    """
    trans_a = parse("./test/trans2")
    trans_a.print_automaton()
    trans_b = parse("./test/trans3")
    trans_b.print_automaton()
    trans_c = trans_a.composition(trans_b)
    trans_c.print_automaton()

def test_automata_equivalence():
    """
    Test transducer composition
    """
    automaton = parse("./test/comb2 (kópia)")
    automaton.print_automaton()
    automaton_b = parse("./test/comb (kópia)")
    automaton_b.print_automaton()
    print(automaton.is_equivalent(automaton_b))

def test_automata_inclusion():
    """
    Test transducer composition
    """
    automaton = parse("./test/comb2 (kópia)")
    automaton_b = parse("./test/comb (kópia)")
    print(automaton.is_inclusion(automaton_b))

def test_to_classic():
    """
    Test transducer composition
    """
    automaton = parse("./test/comb (kópia)")
    automaton_b = automaton.to_classic()
    automaton_b.print_automaton()

def parse_timbuk():
    automaton = parse("./test/timbuk")
    automaton.print_automaton()

def word_transl():
    automaton = parse("./test/trans")
    print(automaton.check_translation("dae", "bac"))

def translate_word():
    automaton = parse("./test/trans")
    print(automaton.translate_word("dddcee"))

if __name__ == '__main__':
    #test_to_classic()
    #test_automata_inclusion()
    #test_automata_equivalence()
    #parse_timbuk()
    translate_word()
