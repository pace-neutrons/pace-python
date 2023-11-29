#!/bin/bash
find "$1" -name _docify -exec rm -rf '{}' \;
find "$1" -name .git -exec rm -rf '{}' \;
find "$1" -size 0 -exec rm -f '{}' \;
find "$1" -name "@*_old" -exec rm -rf '{}' \;

exit 0
