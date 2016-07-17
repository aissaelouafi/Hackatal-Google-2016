#! /bin/bash
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd`
popd > /dev/null

PPATH=$1
STR=$2
REPL=$3

for file in $(find $PPATH -iname "*$STR*"); do
    $SCRIPTPATH/normalize.py -i $file -s $STR -r $REPL
done
