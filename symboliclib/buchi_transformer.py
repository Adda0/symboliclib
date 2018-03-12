from os import listdir

# transorms .ats format to Timbuk format

# folder with .ats buch automata
filelist = listdir("./semi-buchi-automata")
# folder for Timbuk results
result_directory = "./test-buchi/"
for filename in filelist:
    with open( "./semi-buchi-automata/" + filename, "r") as ins:
        start_translation = False
        parse_transitions = False
        result = ""
        for line in ins:
            if "inclusionRHS" in line:
                start_translation = True
            if "inclusionLHS" in line:
                start_translation = False
            if "alphabet" in line and start_translation:
                items = line.split("{")[1].split("}")[0]
                result += "Ops " + items + "\n\nAutomaton A @GBA \n"
            if "states" in line and start_translation:
                items = line.split("{")[1].split("}")[0]
                result += "States " + items + "\n"
            if "initialStates" in line and start_translation:
                init_states = line.split("{")[1].split("}")[0]
            if "finalStates" in line and start_translation:
                items = line.split("{")[1].split("}")[0]
                result += "Final States  " + items + "\nTransitions\n"
                for ini in init_states.split():
                    result += "x -> " + ini + "\n"
            if parse_transitions and "}" in line:
                parse_transitions = False
            if parse_transitions:
                items = line.split("(")[1].split(")")[0].split()
                result += "\"" + items[1] + "\"(" + items[0] + ") -> " + items[2] + "\n"
            if "transitions" in line and start_translation:
                parse_transitions = True
        with open(result_directory + filename, "w+") as file:
            file.write(result)