#! /bin/sh

GDIR=`dirname $PWD`
TDIR=$GDIR/test
OPTS="-i $GDIR/example/gramps/example.gramps -f gramps-xml"
PRG="python gramps.py"

for report in ancestor_chart ancestor_chart2 descendant_graph
do
  for fmt in "sxw" "ps" "pdf" "svg"
    do
    echo ""
    echo "+--------------------------------------------------------------"
    echo "|"
    echo "| $report in $fmt format"
    echo "|"
    echo "+--------------------------------------------------------------"
    
    (cd $GDIR/src; $PRG $OPTS -a report -p name=$report,id=I44,off=$fmt,of=$TDIR/$report.$fmt)
  done
done

for report in ancestor_report ancestors_report descend_report det_ancestor_report det_descendant_report
do
  for fmt in "sxw" "pdf" "kwd" "abw" "rtf"
    do
    echo ""
    echo "+--------------------------------------------------------------"
    echo "|"
    echo "| $report in $fmt format"
    echo "|"
    echo "+--------------------------------------------------------------"
    
    (cd $GDIR/src; $PRG $OPTS -a report -p name=$report,id=I44,off=$fmt,of=$TDIR/$report.$fmt)
  done
done

