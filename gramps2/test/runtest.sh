#! /bin/sh

# $Id$

GDIR=`dirname $PWD`
TDIR=$GDIR/test
OPTS="-i $GDIR/example/gramps/example.gramps -f gramps-xml"
PRG="python gramps.py"

GRPH_FMT="sxw ps pdf svg"
TEXT_FMT="sxw pdf kwd abw rtf txt"

GRPH_REP="ancestor_chart ancestor_chart2 descendant_graph"
TEXT_REP="ancestor_report ancestors_report descend_report det_ancestor_report det_descendant_report family_group"

# Single run with all graphical reports in all formats
echo ""
echo "+--------------------------------------------------------------"
echo "| Reports:"
echo "|          "$GRPH_REP
echo "| Formats:"
echo "|          "$GRPH_FMT
echo "+--------------------------------------------------------------"
action=
for report in $GRPH_REP; do
    for fmt in $GRPH_FMT; do
	action="$action -a report -p name=$report,id=I44,off=$fmt,of=$TDIR/$report.$fmt"
    done
done
(cd $GDIR/src; $PRG $OPTS $action)

# Single run with all textual reports in all formats
echo ""
echo "+--------------------------------------------------------------"
echo "| Reports:"
echo "|          "$TEXT_REP
echo "| Formats:"
echo "|          "$TEXT_FMT
echo "+--------------------------------------------------------------"
action=
for report in $TEXT_REP; do
    for fmt in $TEXT_FMT; do
	action="$action -a report -p name=$report,id=I44,off=$fmt,of=$TDIR/$report.$fmt"
    done
done
(cd $GDIR/src; $PRG $OPTS $action)
