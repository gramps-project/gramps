# This is the src/plugins level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins

pkgdata_PYTHON = \
	AncestorChart2.py\
	AncestorReport.py\
	BookReport.py\
	Calendar.py \
	ChangeTypes.py\
	ChangeNames.py\
	Check.py\
	CountAncestors.py\
	Desbrowser.py\
	DescendReport.py\
	DescendChart.py\
	DetAncestralReport.py\
	DetDescendantReport.py\
	EventCmp.py\
	EventNames.py\
	ExportCSV.py\
	ExportVCalendar.py\
	ExportVCard.py\
	ExtractCity.py\
	FamilyGroup.py\
	FamilyLines.py\
	FanChart.py\
	GraphViz.py\
	ImportCSV.py\
	IndivComplete.py\
	ImportvCard.py\
	FindDupes.py\
	NarrativeWeb.py\
	PatchNames.py\
	ReadPkg.py\
	ReadGrdb.py\
	Rebuild.py\
	RelCalc.py\
	ReorderIds.py\
	SoundGen.py\
	StatisticsChart.py\
	Summary.py\
	TimeLine.py\
	Verify.py\
	WriteFtree.py\
	WritePkg.py\
	WriteCD.py\
	OwnerEditor.py\
	rel_ru.py\
	Eval.py\
	Leak.py\
	SimpleBookTitle.py\
	CustomBookText.py\
	rel_cs.py\
	rel_it.py\
	rel_hu.py\
	rel_da.py\
	rel_de.py\
	rel_fi.py\
	rel_fr.py\
	rel_no.py\
	rel_sv.py\
	rel_sk.py\
	ImportGeneWeb.py\
	WriteGeneWeb.py\
	rel_es.py\
	Checkpoint.py\
	MediaManager.py\
	RemoveUnused.py\
	rel_pl.py\
	RebuildRefMap.py\
	all_events.py \
	siblings.py

pkgpyexecdir = @pkgpyexecdir@/plugins
pkgpythondir = @pkgpythondir@/plugins

GLADEFILES = \
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
	checkpoint.glade\
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
