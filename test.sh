#!/bin/bash


SCRIPT=$(readlink -f "$0")
DIR=$(dirname "$SCRIPT")

if [ -z "$1" ]; then
    ARGV="bluetooth_mesh"
else
    ARGV="$@"
fi

cd "$DIR"

set -x
PYTEST_ADDOPTS="--color=auto -vv $ARGV" python3 setup.py test
