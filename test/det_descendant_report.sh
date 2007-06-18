#! /bin/sh
#
# Report test for GRAMPS: Generate det_descendant_report testing
# different option combinations.

# $Id$

REP="det_ancestor_report"
FMT="txt"

TOP_DIR=`dirname $PWD`
TEST_DIR=$TOP_DIR/test
SRC_DIR=$TOP_DIR/src
PRG="python gramps.py"
EXAMPLE_XML=$TOP_DIR/example/gramps/example.gramps

REP_DIR=$TEST_DIR/reports/$REP
mkdir -p $REP_DIR

DATA_DIR=$TEST_DIR/data
mkdir -p $DATA_DIR
if [ -f $DATA_DIR/example.grdb ]; then
    rm $DATA_DIR/example.grdb
fi

echo ""
echo "+--------------------------------------------------------------"
echo "| Import XML, write GRDB"
echo "+--------------------------------------------------------------"
OPTS="-i $EXAMPLE_XML -o $DATA_DIR/example.grdb"
(cd $SRC_DIR; $PRG $OPTS)

OPTS="-O $DATA_DIR/example.grdb"

echo ""
echo "+--------------------------------------------------------------"
echo "| Text Report: "$REP
echo "| Text Format: "$FMT
echo "+--------------------------------------------------------------"
for desref in {0,1}; do
for incphotos in {0,1}; do
for omitda in {0,1}; do
for incsources in {0,1}; do
for usenick in {0,1}; do
for fulldates in {0,1}; do
for incnotes in {0,1}; do
for repplace in {0,1}; do
for repdate in {0,1}; do
for computeage in {0,1}; do
for incnames in {0,1}; do
for incevents in {0,1}; do
for listc in {0,1}; do
    output="$desref$incphotos$omitda$incsources$usenick$fulldates$incnotes$repplace$repdate$computeage$incnames$incevents$listc"
    action="-a report -p name=$REP,id=I44,off=$FMT,of=$REP_DIR/$output.$FMT,desref=$desref,incphotos=$incphotos,omitda=$omitda,incsources=$incsources,usenick=$usenick,fulldates=$fulldates,incnotes=$incnotes,repplace=$repplace,repdate=$repdate,computeage=$computeage,incnames=$incnames,incevents=$incevents,listc=$listc"
    (cd $SRC_DIR; $PRG $OPTS $action)
done
done
done
done
done
done
done
done
done
done
done
done
done
