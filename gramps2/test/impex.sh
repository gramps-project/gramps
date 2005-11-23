#! /bin/sh

# $Id$

TOP_DIR=`dirname $PWD`
TEST_DIR=$TOP_DIR/test
SRC_DIR=$TOP_DIR/src
PRG="python gramps.py"
EXAMPLE_XML=$TOP_DIR/example/gramps/example.gramps
OUT_FMT="gedcom gramps-xml gramps-pkg wft geneweb"

echo ""
echo "+--------------------------------------------------------------"
echo "| Import XML, write GRDB"
echo "+--------------------------------------------------------------"
rm $TEST_DIR/example.grdb
OPTS="-i $EXAMPLE_XML -o $TEST_DIR/example.grdb"
(cd $SRC_DIR; $PRG $OPTS)

echo ""
echo "+--------------------------------------------------------------"
echo "| Check GRDB for errors"
echo "+--------------------------------------------------------------"
OPTS="-O $TEST_DIR/example.grdb -a tool -p name=check"
(cd $SRC_DIR; $PRG $OPTS)

echo ""
echo "+--------------------------------------------------------------"
echo "| Open GRDB, write all other formats"
echo "+--------------------------------------------------------------"
OPTS="-O $TEST_DIR/example.grdb"
for fmt in $OUT_FMT; do
    OPTS="$OPTS -o $TEST_DIR/example.$fmt -f $fmt"
done
(cd $SRC_DIR; $PRG $OPTS)

echo ""
echo "+--------------------------------------------------------------"
echo "| Validate produced XML"
echo "+--------------------------------------------------------------"
echo "* Regular well-formedness and DTD validation"
xmllint --noout --valid example.gramps-xml
echo "* Post-parsing DTD validation"
xmllint --noout --postvalid example.gramps-xml
echo "* Validate against RelaxNG schema"
xmllint --noout --relaxng ../doc/grampsxml.rng example.gramps-xml
