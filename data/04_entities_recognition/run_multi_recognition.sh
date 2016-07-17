#! /bin/bash
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd`
popd > /dev/null

PPATH=$1
ENTITY=$2
STR=$3
REPL=$4

for G in A B C D E F; do
    nohup $SCRIPTPATH/run_recognition.sh $PPATH/Groupe_$G $ENTITY $STR $REPL &
done
