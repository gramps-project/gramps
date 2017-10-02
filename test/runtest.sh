#! /bin/sh
#
# Report test for GRAMPS: Generate every report in every format.
#
# The results of this test set depend on what options were used
# previously with the reports, because this test set is not
# specifying all possible options and their combinations. 
# Instead, this is a general test for all formats.


TOP_DIR=`dirname $PWD`
TEST_DIR=$TOP_DIR/test
SRC_DIR=$TOP_DIR/gramps
PRG="python ../Gramps.py"
EXAMPLE_XML=$TOP_DIR/example/gramps/example.gramps

REP_DIR=$TEST_DIR/reports
mkdir -p $REP_DIR

OPTS="-i $EXAMPLE_XML"

GRPH_FMT="sxw ps pdf svg"
TEXT_FMT="sxw ps pdf kwd abw rtf txt html tex"

GRPH_REP="ancestor_chart descend_chart fan_chart statistics_chart timeline calendar"
TEXT_REP="ancestor_report descend_report det_ancestor_report det_descendant_report family_group"

# Single run with all graphical reports in all formats
echo ""
echo "+--------------------------------------------------------------"
echo "| Graphical Reports: "$GRPH_REP
echo "| Graphical Formats: "$GRPH_FMT
echo "+--------------------------------------------------------------"
action=
for report in $GRPH_REP; do
    for fmt in $GRPH_FMT; do
	action="$action -a report -p name=$report,id=I44,off=$fmt,of=$REP_DIR/$report.$fmt"
    done
done
(cd $SRC_DIR; $PRG $OPTS $action)

# Single run with all textual reports in all formats
echo ""
echo "+--------------------------------------------------------------"
echo "| Text Reports: "$TEXT_REP
echo "| Text Formats: "$TEXT_FMT
echo "+--------------------------------------------------------------"
action=
for report in $TEXT_REP; do
    for fmt in $TEXT_FMT; do
	action="$action -a report -p name=$report,id=I44,off=$fmt,of=$REP_DIR/$report.$fmt"
    done
done
(cd $SRC_DIR; $PRG $OPTS $action)
