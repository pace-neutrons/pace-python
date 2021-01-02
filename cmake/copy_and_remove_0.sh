#!/bin/bash

if [ ! -d $2 ]
then
    mkdir "$2"
fi

cp -r "$1" "$2"
find "$2" -name _docify -exec rm -rf '{}' \;
find "$2" -name .git -exec rm -rf '{}' \;
find "$2" -size 0 -exec rm -f '{}' \;

exit 0
