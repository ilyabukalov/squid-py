#!/bin/bash

echo "Starting $1 orders on the Ocean Protocol network."

for i in $(eval echo {1..$1})
do
   echo "Starting order # $i "
   python ./examples/performance_test.py  ${i} &
done
