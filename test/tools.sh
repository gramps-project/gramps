#! /bin/sh
#
# Tool test for GRAMPS: Run tools with the default options.
#
# The results of this test set depend on what options were used
# previously with the tools, because this test set is not
# specifying all possible options and their combinations. 
# Instead, this is a general test for all tools.


TOP_DIR=`dirname $PWD`
TEST_DIR=$TOP_DIR/test
SRC_DIR=$TOP_DIR/gramps
PRG="python ../Gramps.py"
EXAMPLE_XML=$TOP_DIR/example/gramps/example.gramps
MINIMAL_XML=$TOP_DIR/example/gramps/minimal.gramps

TOOL_DIR=$TEST_DIR/tools
mkdir -p $TOOL_DIR

OPTS="-i $EXAMPLE_XML"

TOOLS1="reorder_ids verify rebuild dgenstats rebuild_genstats rebuild_refmap test_for_date_parser_and_displayer check"

# Run all tools on the example data, check at the end
echo ""
echo "+--------------------------------------------------------------"
echo "| Tools: chtype $TOOLS1"
echo "+--------------------------------------------------------------"
action=
action="$action -a tool -p name=chtype,fromtype=Burial,totype=WeirdType"
for tool in $TOOLS1; do
    action="$action -a tool -p name=$tool"
done
/bin/rm -f $TOOL_DIR/tools1.gramps
(cd $SRC_DIR; $PRG $OPTS $action -e $TOOL_DIR/tools1.gramps)

# Run random test generator on an empty db, preserve the result.
echo ""
echo "+--------------------------------------------------------------"
echo "| Tool: testcasegenerator"
echo "+--------------------------------------------------------------"
TEST_DATA=$MINIMAL_XML
/bin/rm -f $TOOL_DIR/testcases.gramps
OPTS="-i $TEST_DATA -e $TOOL_DIR/testcases.gramps"
action="-a tool -p name=testcasegenerator"
(cd $SRC_DIR; $PRG $OPTS $action)
