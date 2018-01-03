#! /bin/sh
#
# Report test for GRAMPS: Generate det_descendant_report testing
# different option combinations.


REP="det_descendant_report"
FMT="txt"

TOP_DIR=`dirname $PWD`
TEST_DIR=$TOP_DIR/test
SRC_DIR=$TOP_DIR
PRG="python3 Gramps.py"
EXAMPLE_XML=$TOP_DIR/example/gramps/example.gramps
EXAMPLE_GED=$TOP_DIR/example/gedcom/sample.ged

REP_DIR=$TEST_DIR/reports/$REP
mkdir -p $REP_DIR

DATA_DIR=$TEST_DIR/data
mkdir -p $DATA_DIR
if [ -f $DATA_DIR/example.gramps ]; then
    rm $DATA_DIR/example.gramps
fi

echo ""
echo "+--------------------------------------------------------------"
echo "| Import XML, write .gramps"
echo "+--------------------------------------------------------------"
OPTS="-i $EXAMPLE_XML -e $DATA_DIR/example.gramps"
#(cd $SRC_DIR; $PRG $OPTS)

OPTS="-i $DATA_DIR/example.gramps"

echo ""
echo "+--------------------------------------------------------------"
echo "| Export Test Files"
echo "| Text Report: "$REP
echo "| Text Format: "$FMT
echo "+--------------------------------------------------------------"
for desref in 'True' 'False'; do
for incphotos in 'True' 'False'; do
for omitda in 'True' 'False'; do
for incsources in 'True' 'False'; do
for fulldates in 'True' 'False'; do
for incnotes in 'True' 'False'; do
for repplace in 'True' 'False'; do
for repdate in 'True' 'False'; do
for computeage in 'True' 'False'; do
for incnames in 'True' 'False'; do
for incevents in 'True' 'False'; do
for listc in 'True' 'False'; do
    output="$desref$incphotos$omitda$incsources$usenick$fulldates$incnotes$repplace$repdate$computeage$incnames$incevents$listc"
    action="-a report -p name=$REP,off=$FMT,of=$REP_DIR/$output.$FMT,desref=$desref,incphotos=$incphotos,omitda=$omitda,incsources=$incsources,fulldates=$fulldates,incnotes=$incnotes,repplace=$repplace,repdate=$repdate,computeage=$computeage,incnames=$incnames,incevents=$incevents,listc=$listc"
    #(cd $SRC_DIR; $PRG $OPTS $action)
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

(cd $SRC_DIR; $PRG -i $EXAMPLE_GED -e $DATA_DIR/example.gramps)
output="NoChildren"
action="-a report -p name=$REP,off=$FMT,of=$REP_DIR/$output.$FMT,listc=False,listc_spouses=False"
(cd $SRC_DIR; $PRG $OPTS $action)
output="ChildrenNoSpouse"
action="-a report -p name=$REP,off=$FMT,of=$REP_DIR/$output.$FMT,listc=True,listc_spouses=False"
(cd $SRC_DIR; $PRG $OPTS $action)
output="ChildrenSpouse"
action="-a report -p name=$REP,off=$FMT,of=$REP_DIR/$output.$FMT,listc=True,listc_spouses=True"
(cd $SRC_DIR; $PRG $OPTS $action)
