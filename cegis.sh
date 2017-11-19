#!/usr/bin/env bash

DREAL="/home/penlu/Downloads/software/dreal3/bin/dReal"

COUNTER=0

mkdir -p exptest

# generate first synth target by compiling sketch
python dreal.py exptest/exptest.sk exptest/exptest${COUNTER}.dr

# high level summary:
# ITERATION 23 BEGINS
# - call dReal on "exptest23.dr"
# - it generates "exptest23.dr.model", containing a proposed program
# - create "exptest23_counter.dr" to seek counterexamples to proposed program
# - call dReal on "exptest23_counter.dr" to generate "exptest23_counter.dr.model"
# - this contains counterexamples to proposed program
# - generate new constraints and add to exptest23.dr to produce "exptest24.dr"
# REPEAT... ITERATION 24

# CEGIS loop
while true ; do
  echo "iteration ${COUNTER}"

  # attempt to find satisfying sketch var assignment; a proposed program
  $DREAL --model exptest/exptest${COUNTER}.dr
  if [ ! -e exptest/exptest${COUNTER}.dr.model ];
  then
    echo "no model for sketch; terminating"
    exit
  fi

  # generate counterexample constraint problem for proposed program
  python counter.py exptest/exptest${COUNTER}.dr exptest/exptest${COUNTER}.dr.model exptest/exptest${COUNTER}_counter.dr

  # attempt to find counterexamples to proposed program
  $DREAL --model exptest/exptest${COUNTER}_counter.dr
  if [ ! -e exptest/exptest${COUNTER}_counter.dr.model ];
  then
    echo "no model for counterexample; finished!"
    echo "see exptest/exptest${COUNTER}.dr.model for final assignments"
    exit
  fi

  # add found counterexample to sketch constraints
  python exam.py exptest/exptest${COUNTER}.dr exptest/exptest${COUNTER}_counter.dr.model exptest/exptest$[$COUNTER+1].dr

  # REPEAT!
  COUNTER=$[$COUNTER+1]
done
