#!/usr/bin/env bash

DREAL="/home/penlu/Downloads/software/dreal3/bin/dReal"

COUNTER=0

python dreal.py exptest/exptest.sk exptest/exptest${COUNTER}.dr
while [ $COUNTER -lt 100 ] ; do
  $DREAL --model exptest/exptest${COUNTER}.dr
  if [ ! d exptest/exptest${COUNTER}.dr.model ];
  then
    echo "no model for sketch; terminating"
    exit
  fi
  python counter.py exptest/exptest${COUNTER}.dr exptest/exptest${COUNTER}.dr.model exptest/exptest${COUNTER}_counter.dr
  $DREAL --model exptest/exptest${COUNTER}_counter.dr
  if [ ! d exptest/exptest${COUNTER}_counter.dr.model ];
  then
    echo "no model for counterexample; finished!"
    echo "see exptest/exptest${COUNTER}.dr.model for final assignments"
    exit
  fi
  python exam.py exptest/exptest${COUNTER}.dr exptest/exptest${COUNTER}_counter.dr.model exptest/exptest$[$COUNTER+1].dr
  COUNTER=$[$COUNTER+1]
done
