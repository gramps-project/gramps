#!/bin/sh
PWD=`dirname $0`
exec "$PWD/python" "$PWD/rungramps.py" $@
