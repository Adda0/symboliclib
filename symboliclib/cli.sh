#!/bin/bash

if [ $# -gt 1 ]; then
    command=$1
    file1=$2
else
    if [ "$1" = "--help" ]; then
        echo "COMMAND LINE INTERFACE TO SYMBOLICLIB

    Usage: ./cli [command] [file1] [file2]
    file is a name of input file with automaton in Timbuk format

    Available commands:
        [command - number of needed automata]
        load - 1 [only reads and pints an automaton]
        complement - 1
        determinize - 1
        minimize - 1
        simulations - 1
        epsilon - 1
        union - 2
        intersection - 2
        inclusion - 2
        equality - 2
        runonnfa - 2
        "
    else
    echo "Please give some command and input file. Help: ./cli --help"
    fi
    exit 0
fi

case $command in
complement)
  python3 -c "import symboliclib; a = symboliclib.parse('$file1');  r = a.complement(); r.print_automaton();"
  ;;
load)
  python3 -c "import symboliclib; a = symboliclib.parse('$file1'); a.print_automaton();"
  ;;
determinize)
  python3 -c "import symboliclib; a = symboliclib.parse('$file1'); r = a.determinize(); r.print_automaton();"
  ;;
minimize)
  python3 -c "import symboliclib; a = symboliclib.parse('$file1'); r = a.minimize(); r.print_automaton();"
  ;;
epsilon)
  python3 -c "import symboliclib; a = symboliclib.parse('$file1'); b = a.remove_epsilon(); b.print_automaton();"
  ;;
simulations)
  python3 -c "import symboliclib; a = symboliclib.parse('$file1'); print(a.simulations());"
  ;;
union)
  if [ $# -gt 2 ]; then
    file2=$3
    python3 -c "import symboliclib; a = symboliclib.parse('$file1'); b = symboliclib.parse('$file2'); c = a.union(b); c.print_automaton();"
  else
    echo "Another argument needed."
    exit 0
  fi
  ;;
intersection)
  if [ $# -gt 2 ]; then
    file2=$3
    python3 -c "import symboliclib; a = symboliclib.parse('$file1'); b = symboliclib.parse('$file2'); c = a.intersection(b); c.print_automaton();"
  else
    echo "Another argument needed."
    exit 0
  fi
  ;;
inclusion)
  if [ $# -gt 2 ]; then
    file2=$3
    python3 -c "import symboliclib; a = symboliclib.parse('$file1'); b = symboliclib.parse('$file2'); print(a.is_inclusion(b));"
  else
    echo "Another argument needed."
    exit 0
  fi
  ;;
inclusion_simple)
  if [ $# -gt 2 ]; then
    file2=$3
    python3 -c "import symboliclib; a = symboliclib.parse('$file1'); b = symboliclib.parse('$file2'); print(a.is_inclusion_simple(b));"
  else
    echo "Another argument needed."
    exit 0
  fi
  ;;
inclusion_antichain)
  if [ $# -gt 2 ]; then
    file2=$3
    python3 -c "import symboliclib; a = symboliclib.parse('$file1'); b = symboliclib.parse('$file2'); print(a.is_inclusion_antichain(b));"
  else
    echo "Another argument needed."
    exit 0
  fi
  ;;
equality)
  if [ $# -gt 2 ]; then
    file2=$3
    python3 -c "import symboliclib; a = symboliclib.parse('$file1'); b = symboliclib.parse('$file2'); print(a.is_equivalent(b));"
  else
    echo "Another argument needed."
    exit 0
  fi
  ;;
runonnfa)
  if [ $# -gt 2 ]; then
    file2=$3
    python3 -c "import symboliclib; a = symboliclib.parse('$file1'); b = symboliclib.parse('$file2'); c = a.run_on_nfa(b); c.print_automaton();"
  else
    echo "Another argument needed."
    exit 0
  fi
  ;;
*)
  echo "Unknown command."
  ;;
esac
