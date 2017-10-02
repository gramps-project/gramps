#! /bin/sh
#
# Import/export test for GRAMPS:
#   o Import example XML data and create internal Gramps DB
#   o Open produced example Gramps DB, then
#     * check data for integrity
#     * output in all formats
#   o Check resulting XML for well-formedness and validate it
#     against DTD and RelaxNG schema.
#   o Import every exported file produced if the format
#     is also supported for import, and run a text summary report.
#   o Diff each report with the summary of the produced example DB


TOP_DIR=`dirname $PWD`
TEST_DIR=$TOP_DIR/test
SRC_DIR=$TOP_DIR/gramps
PRG="python ../Gramps.py --yes --quiet"
EXAMPLE_XML=$TOP_DIR/example/gramps/example.gramps

OUT_FMT="csv ged gramps gpkg wft gw vcs vcf"
IN_FMT="csv ged gramps gpkg gw vcf"
DATA_DIR=$TEST_DIR/data
mkdir -p $DATA_DIR
GRAMPSHOME=$DATA_DIR/grampshome
export GRAMPSHOME
echo ""
echo "+--------------------------------------------------------------"
echo "| GRAMPSHOME set to: $GRAMPSHOME "
echo "+--------------------------------------------------------------"

if [ -d $GRAMPSHOME/. ]; then
    rm -rf $GRAMPSHOME
fi

echo ""
echo "+--------------------------------------------------------------"
echo "| Import XML, create Gramps DB 'example'"
echo "+--------------------------------------------------------------"
OPTS="-i $EXAMPLE_XML -C example"
(cd $SRC_DIR; $PRG $OPTS)

echo ""
echo "+--------------------------------------------------------------"
echo "| Check the example DB for errors"
echo "+--------------------------------------------------------------"
OPTS="-O example -a tool -p name=check"
(cd $SRC_DIR; $PRG $OPTS)

echo ""
echo "+--------------------------------------------------------------"
echo "| Open the example DB, write all other formats"
echo "+--------------------------------------------------------------"
OPTS="-O example"
for fmt in $OUT_FMT; do
    OPTS="$OPTS -e $DATA_DIR/example.$fmt -f $fmt"
done
(cd $SRC_DIR; echo "$PRG $OPTS"; $PRG $OPTS)

echo ""
echo "+--------------------------------------------------------------"
echo "| Validate produced XML"
echo "+--------------------------------------------------------------"
RESULT_GRAMPS=$DATA_DIR/example.gramps
if [ -f $RESULT_GRAMPS ]; then
    RESULT_XML=$DATA_DIR/example.xml
	gunzip < $RESULT_GRAMPS > $RESULT_XML
else
	echo "+--------------------------------------------------------------"
	echo "| ERROR: $RESULT_GRAMPS not found"
	echo "+--------------------------------------------------------------"
	exit 1
fi
echo "* Regular well-formedness and DTD validation"
xmllint --noout --valid $RESULT_XML
echo "* Post-parsing DTD validation"
xmllint --noout --postvalid $RESULT_XML
echo "* Validate against RelaxNG schema"
xmllint --noout --relaxng $TOP_DIR/data/grampsxml.rng $RESULT_XML

echo ""
echo "+----------------------------------------------------------------"
echo "| For each produced format supported for import, generate summary"
echo "+----------------------------------------------------------------"
for fmt in $IN_FMT; do
	EXPORTED_DATA=$DATA_DIR/example.$fmt
	REPORT_TXT=$EXPORTED_DATA.report.txt
    OPTS="-i $EXPORTED_DATA -f $fmt -a report -p name=summary,off=txt,of=$REPORT_TXT"
    (cd $SRC_DIR; $PRG $OPTS)
done

echo ""
echo "+--------------------------------------------------------------"
echo "| Compare to the summary of the original database"
echo "+--------------------------------------------------------------"
IMPORTED_REPORT_TXT=$DATA_DIR/example.report.txt
OPTS="-O example -a report -p name=summary,off=txt,of=$IMPORTED_REPORT_TXT"
(cd $SRC_DIR; $PRG $OPTS)
for exported_report_txt in $DATA_DIR/example.*.report.txt; do
	diff -u $IMPORTED_REPORT_TXT $exported_report_txt
done
