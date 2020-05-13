#!/bin/bash

if [ ! -d $2 ]
then
    mkdir "$2"
fi

cp -r "$1/Horace/horace_core" "$2/Horace"
find "$2/Horace" -size 0 -exec rm -f '{}' \;
find "$2/Horace" -name _docify -exec rm -rf '{}' \;

cp -r "$1/Herbert/herbert_core" "$2/Herbert"
find "$2/Herbert" -size 0 -exec rm -f '{}' \;
find "$2/Herbert" -name _docify -exec rm -rf '{}' \;
rm -rf "$2/Herbert/applications/docify"
