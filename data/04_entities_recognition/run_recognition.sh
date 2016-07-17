#! /bin/bash
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd`
popd > /dev/null

PPATH=$1
ENTITY=$2
STR=$3
REPL=$4

for file in $(find $PPATH -iname "*$STR*"); do
    $SCRIPTPATH/entities_match.py -i $file -e $ENTITY -s $STR -r $REPL 
done
