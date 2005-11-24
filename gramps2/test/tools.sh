#! /bin/sh
#
# Tool test for GRAMPS: Run tools with the default options.
#
# The results of this test set depend on what options were used
# previously with the tools, because this test set is not
# specifying all possible options and their combinations. 
# Instead, this is a general test for all tools.

# $Id$

TOP_DIR=`dirname $PWD`
TEST_DIR=$TOP_DIR/test
SRC_DIR=$TOP_DIR/src
PRG="python gramps.py"
EXAMPLE_XML=$TOP_DIR/example/gramps/example.gramps

TOOL_DIR=$TEST_DIR/tools
mkdir -p $TOOL_DIR

OPTS="-i $EXAMPLE_XML"

TOOLS1="reorder_ids verify chkpoint rebuild dgenstats check"
TOOLS2="chtype cmdref testcasegenerator"

# Run all tools on the example data, check at the end
echo ""
echo "+--------------------------------------------------------------"
echo "| Tools: chtype cmdref $TOOLS1"
echo "+--------------------------------------------------------------"
action=
action="$action -a tool -p name=chtype,fromtype=Burial,totype=WeirdType"
action="$action -a tool -p name=cmdref,include=1,target=$TOOL_DIR/junk.xml"
for tool in $TOOLS1; do
    action="$action -a tool -p name=$tool"
done
(cd $SRC_DIR; $PRG $OPTS $action)

# Run random test generator on an empty db, preserve the result.
echo ""
echo "+--------------------------------------------------------------"
echo "| Tool: testcasegenerator"
echo "+--------------------------------------------------------------"
TEST_DATA=$TOOL_DIR/junk.grdb
if [ -f $TEST_DATA ]; then
    rm $TEST_DATA
fi
touch $TEST_DATA
OPTS="-O $TEST_DATA"
action="-a tool -p name=testcasegenerator"
(cd $SRC_DIR; $PRG $OPTS $action)
