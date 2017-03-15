"""
Super cool parser module
"""
from __future__ import print_function
from sa import SA
from lfa import LFA
from st import ST


def parse(testfile):
    """
    Parse given automaton in Timbuk format and return FA instance.
    """
    if not testfile:
        print("No filename was given.")
        exit(1)
    parse_transitions = False
    alpha = set()
    automaton_type = ""
    states = set()
    final = set()
    transitions = {}
    start = set()

    with open(testfile) as filep:
        for line in filep:
            if parse_transitions and not line.isspace():
                parts = line.split("->")
                """if '"' not in line:
                    start.add(parts[1].strip())
                    continue"""
                if not start:
                    start.add(parts[1].strip())
                    continue

                end_state = parts[1].strip()
                if '"' in line:
                    parts = parts[0].split("\"")
                    predicate = parsePredicate(parts[1], automaton_type)
                else:
                    symbol = parts[0].split("(")[0].strip()
                    start_st = parts[0].split("(")[1]
                    parts = ["", "", start_st]
                    predicate = parsePredicate(symbol, automaton_type)

                start_state = parts[2].replace("(", "").replace(")", "").strip()

                if predicate not in transitions[start_state]:
                    transitions[start_state][predicate] = [end_state]
                else:
                    if end_state not in transitions[start_state][predicate]:
                        transitions[start_state][predicate].append(end_state)

                continue

            if line.startswith("Ops "):
                for element in line.split(" ")[1:]:
                    if not element.isspace():
                        if ":" in element:
                            parts = element.split(":")
                            if int(parts[1]) > 0 and not parts[0].isspace():
                                alpha.add(parts[0])
                        else:
                            alpha.add(element)
                continue

            if line.startswith("Automaton "):
                if "@" in line:
                    automaton_type = line.split("@")[1].strip()
                    if automaton_type == "INFA":
                        from in_notin_parser import parsePredicate
                    elif automaton_type == "LFA":
                        from letter_parser import parsePredicate
                    elif automaton_type == "INT":
                        from transducer_predicate import parsePredicate
                else:
                    automaton_type = "LFA"
                    from letter_parser import parsePredicate

            if line.startswith("States "):
                for element in line.split(" ")[1:]:
                    if not element.isspace():
                        element = element.strip()
                        states.add(element)
                        transitions[element] = {}
                continue

            if line.startswith("Final States"):
                for element in line.split(" ")[2:]:
                    if not element.isspace():
                        element = element.strip()
                        final.add(element)
                continue

            if line.startswith("Transitions"):
                parse_transitions = True

    transitions_reduced = transitions.copy()
    for state in transitions:
        if not transitions[state]:
            del transitions_reduced[state]
    transitions = transitions_reduced

    automaton = type_to_class(automaton_type)
    automaton.alphabet = alpha
    automaton.states = states
    automaton.start = start
    automaton.final = final
    automaton.transitions = transitions
    automaton.automaton_type = automaton_type
    automaton.is_deterministic()

    check_result = automaton.check_automaton()
    if check_result != "OK":
        print("ERROR: " + testfile + " : " + check_result)
        exit(-1)

    automaton.simple_reduce()

    return automaton


def type_to_class(type_name):
    return {
        "INFA": SA(),
        "LFA": LFA(),
        "INT": ST(),
    }[type_name]
