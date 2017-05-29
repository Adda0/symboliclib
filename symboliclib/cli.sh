#!/bin/bash

if [ $# -gt 1 ]; then
    command=$1
    file1=$2
else
    if [ "$1" = "--help" ]; then
        echo "COMMAND LINE INTERFACE TO SYMBOLICLIB
    Copyright (c) 2017  Michaela Bielikova <xbieli06@stud.fit.vutbr.cz>

    Usage: ./cli.sh [command] [file1] [file2]
    file is a name of input file with automaton in Timbuk format

    Generate pydoc:
        ./cli.sh doc
        - documentation goes into a folder ./doc/

    Available commands:
        [command - number of needed automata]
        load - 1 [only reads and pints an automaton]
        complement - 1
        determinize - 1
        determinize_simulations - 1 [only for classic letter automata]
        minimize - 1
        simulations - 1
        epsilon - 1
        union - 2
        intersection - 2
        inclusion - 2
        inclusion_simple - 2
        inclusion_antichain - 2
        inclusion_antichain_pure - 2
        equality - 2
        runonnfa - 2
        "
    elif [ "$1" = "doc" ]; then
        mkdir -p doc
        pydoc -w ./*.py
        mv *.html doc
    else
        echo "COMMAND LINE INTERFACE TO SYMBOLICLIB
Please give some command and input file. Help: ./cli --help
Copyright (c) 2017  Michaela Bielikova <xbieli06@stud.fit.vutbr.cz>"
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
determinize_simulations)
  python3 -c "import symboliclib; a = symboliclib.parse('$file1'); r = a.determinize_simulations(); r.print_automaton();"
  ;;
minimize)
  python3 -c "import symboliclib; a = symboliclib.parse('$file1'); r = a.minimize(); r.print_automaton();"
  ;;
epsilon)
  python3 -c "import symboliclib; a = symboliclib.parse('$file1'); b = a.remove_epsilon(); b.print_automaton();"
  ;;
simulations)
  python3 -c "import symboliclib; a = symboliclib.parse('$file1'); print(a.simulations_preorder());"
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
    python3 -c "import symboliclib; a = symboliclib.parse('$file1'); b = symboliclib.parse('$file2'); print(a.is_included(b));"
  else
    echo "Another argument needed."
    exit 0
  fi
  ;;
inclusion_simple)
  if [ $# -gt 2 ]; then
    file2=$3
    python3 -c "import symboliclib; a = symboliclib.parse('$file1'); b = symboliclib.parse('$file2'); print(a.is_included_simple(b));"
  else
    echo "Another argument needed."
    exit 0
  fi
  ;;
inclusion_antichain)
  if [ $# -gt 2 ]; then
    file2=$3
    python3 -c "import symboliclib; a = symboliclib.parse('$file1'); b = symboliclib.parse('$file2'); print(a.is_included_antichain(b));"
  else
    echo "Another argument needed."
    exit 0
  fi
  ;;
inclusion_antichain_pure)
  if [ $# -gt 2 ]; then
    file2=$3
    python3 -c "import symboliclib; a = symboliclib.parse('$file1'); b = symboliclib.parse('$file2'); print(a.is_included_antichain_pure(b));"
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
