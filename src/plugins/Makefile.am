# This is the src/plugins level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins

pkgdata_PYTHON = \
	all_events.py\
	all_relations.py\
	AgeOnDate.py\
	AncestorChart.py\
	AncestorReport.py\
	BookReport.py\
	CalculateEstimatedDates.py\
	Calendar.py \
	ChangeTypes.py\
	ChangeNames.py\
	Check.py\
	CmdRef.py\
	CountAncestors.py\
	CustomBookText.py\
	DateParserDisplayTest.py\
	DefaultGramplets.py\
	Desbrowser.py\
	DescendChart.py\
	DescendReport.py\
	DetAncestralReport.py\
	DetDescendantReport.py\
	EndOfLineReport.py\
	Eval.py\
	EventCmp.py\
	EventNames.py\
	ExportCSV.py\
	ExportVCalendar.py\
	ExportVCard.py\
	ExtractCity.py\
	FamilyGroup.py\
	FanChart.py\
	FindDupes.py\
	GVFamilyLines.py \
	GVHourGlass.py\
	GVRelGraph.py\
	ImportCSV.py\
	ImportGeneWeb.py\
	ImportvCard.py\
	IndivComplete.py\
	KinshipReport.py\
	Leak.py\
	lineage.py\
	MarkerReport.py\
	MediaManager.py\
	NarrativeWeb.py\
	NotRelated.py\
	OnThisDay.py\
	OwnerEditor.py\
	PatchNames.py\
	ReadGrdb.py\
	ReadPkg.py\
	Rebuild.py\
	RebuildRefMap.py\
	References.py\
	RelCalc.py\
	rel_cs.py\
	rel_da.py\
	rel_de.py\
	rel_es.py\
	rel_fi.py\
	rel_fr.py\
	rel_hu.py\
	rel_it.py\
	rel_nl.py\
	rel_no.py\
	rel_pl.py\
	rel_pt.py\
	rel_ru.py\
	rel_sk.py\
	rel_sv.py\
	RemoveUnused.py\
	ReorderIds.py\
	SameSurnames.py\
	siblings.py\
	SimpleBookTitle.py\
	SoundGen.py\
	StatisticsChart.py\
	Summary.py\
	TimeLine.py\
	Verify.py\
	WebCal.py\
	WriteFtree.py\
	WriteGeneWeb.py\
	WritePkg.py\
	WriteCD.py

#        DateParserDisplayTest.py\
#        DumpGenderStats.py\
#        PHPGedViewConnector.py\
#        TestcaseGenerator.py


pkgpyexecdir = @pkgpyexecdir@/plugins
pkgpythondir = @pkgpythondir@/plugins

GLADEFILES = \
	NotRelated.glade\
	changetype.glade\
	csvexport.glade\
	desbrowse.glade\
	eventcmp.glade\
	merge.glade\
	patchnames.glade\
	changenames.glade\
	relcalc.glade\
	soundex.glade\
	summary.glade\
	verify.glade\
	cdexport.glade\
	eval.glade\
	leak.glade\
	book.glade\
	ownereditor.glade\
	writeftree.glade\
	genewebexport.glade\
	vcardexport.glade\
	vcalendarexport.glade\
	unused.glade

GRAPHICS = 

DATAFILES = \
	holidays.xml

dist_pkgdata_DATA = $(GLADEFILES) $(GRAPHICS) $(DATAFILES)

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../:../docgen"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
