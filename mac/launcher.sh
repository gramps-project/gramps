#!/bin/sh
PWD=`dirname $0`
export PYTHON="$PWD/python"
exec "$PYTHON" "$PWD/rungramps.py" $@
