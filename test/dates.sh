#! /bin/sh
#
# Date Handler test for GRAMPS:
#   o Run date_test.py for every available locale.


TOP_DIR=`dirname $PWD`
SRC_DIR=$TOP_DIR/src
PRG="python date_test.py"

export PYTHONPATH=$SRC_DIR

# Get the list of xx_XX language codes
LANG_LIST=`locale -a | grep _ | cut -f 1 -d . | sort | uniq`
for lang in $LANG_LIST; do
    # for each xx_XX language code, try all available locales
    LOC_LIST=`locale -a | grep $lang`
    false
    for loc in $LOC_LIST; do
	export LANG=$loc
	# Run test
	res=`cd $SRC_DIR && $PRG`
	# Print results
	echo "$res"
	if [ $?=0 ]; then
	    # Finish with this LANG if succeeded.
	    echo "Done testing $LANG"
	    read -p"    ENTER to continue "
	    break
	fi
    done
done
