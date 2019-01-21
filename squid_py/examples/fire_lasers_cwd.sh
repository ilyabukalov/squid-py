#!/bin/bash

#PYTHON="/usr/bin/python"
#python ./squid_py/examples/register_asset.py

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

let passes=0
let fails=0
let total=0
unset summarystring
let summarystring=""

runtest() {
#    conda env list
    SCRIPT_PATH=$1
    SCRIPT_NAME=$2
    echo "\n*********************************************************"
    echo -e " Running test: " $2
    echo "*********************************************************\n"

    python $SCRIPT_PATH$SCRIPT_NAME

    exit_status=$?
    if [ $exit_status -eq 0 ]; then
        MESSAGE="Success, (exit code "$exit_status")"
        passes=$((passes + 1))
        total=$((total + 1))
#        summarystring="${GREEN} $summarystring    \xE2\x9C\x94   $SCRIPT_NAME  \n"
        summarystring="$summarystring${GREEN}     ✔ $SCRIPT_NAME  \n"
    else
        MESSAGE="Fail, (exit code "$exit_status")"
        fails=$((fails + 1))
        total=$((total + 1))
#        summarystring="${RED} $summarystring    \xE2\x9D\x8C   $SCRIPT_NAME    \n"
        summarystring="$summarystring${RED}     ✗ $SCRIPT_NAME    \n"
    fi

    echo "\n********* TEST COMPLETE *********************************"
    echo " $SCRIPT_NAME: $MESSAGE"
    echo "*********************************************************\n"
}

runtest ./squid_py/examples/ register_asset.py
runtest ./squid_py/examples/ resolve_asset.py
runtest ./squid_py/examples/ search_assets.py
runtest ./squid_py/examples/ sign_agreement.py
runtest ./squid_py/examples/ buy_asset.py



echo "\n********* SUMMARY OF $total TESTS ***************************"

echo -e "\n"
if [ $TEST_NILE -eq 1 ]; then
    echo "     Summary of $total tests against deployed Nile network"
else
    echo "     Summary of $total tests against local Spree network"
fi

echo "\n"
echo "     "$passes" scripts passed"
echo "     "$fails" scripts failed"

echo "\n"

echo $summarystring
echo ${NC}

echo "*********************************************************\n"