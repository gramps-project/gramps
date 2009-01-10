# This is the src/plugins level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins

pkgdata_PYTHON = \
	all_events.py\
	all_relations.py\
	AgeOnDate.py\
	AgeStats.py\
	AncestorTree.py\
	AncestorReport.py\
	BookReport.py\
	CalculateEstimatedDates.py\
	Calendar.py \
	ChangeTypes.py\
	ChangeNames.py\
	Check.py\
	CmdRef.py\
	CustomBookText.py\
	DateParserDisplayTest.py\
	DefaultGramplets.py\
	Desbrowser.py\
	DescendTree.py\
	DescendReport.py\
	DescendGramplet.py\
	DetAncestralReport.py\
	DetDescendantReport.py\
	EndOfLineReport.py\
	Eval.py\
	EventCmp.py\
	EventNames.py\
	ExportCd.py\
	ExportCsv.py\
	ExportFtree.py\
	ExportGedcom.py\
	ExportGeneWeb.py\
	ExportPkg.py\
	ExportVCalendar.py\
	ExportVCard.py\
	ExportXml.py\
	ExtractCity.py\
	FamilyGroup.py\
	FanChart.py\
	FilterByName.py\
	FindDupes.py\
	GivenNameGramplet.py\
	GVFamilyLines.py \
	GVHourGlass.py\
	GVRelGraph.py\
	ImportCsv.py\
	ImportGedcom.py\
	ImportGeneWeb.py\
	ImportGpkg.py\
	ImportGrdb.py\
	ImportProGen.py\
	ImportVCard.py\
	ImportXml.py\
	IndivComplete.py\
	KinshipReport.py\
	Leak.py\
	lineage.py\
	MarkerReport.py\
	MediaManager.py\
	NarrativeWeb.py\
	NotRelated.py\
	NumberOfAncestorsReport.py\
	OnThisDay.py\
	OwnerEditor.py\
	PatchNames.py\
	PlaceReport.py\
	Rebuild.py\
	RebuildRefMap.py\
	Records.py\
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
	SortEvents.py\
	SoundGen.py\
	StatisticsChart.py\
	Summary.py\
	TimeLine.py\
	Verify.py\
	WebCal.py\
	WhatsNext.py

#        DateParserDisplayTest.py\
#        DumpGenderStats.py\
#        PHPGedViewConnector.py\
#        TestcaseGenerator.py


pkgpyexecdir = @pkgpyexecdir@/plugins
pkgpythondir = @pkgpythondir@/plugins

GLADEFILES = \
	book.glade\
	changenames.glade\
	changetype.glade\
	desbrowse.glade\
	eval.glade\
	eventcmp.glade\
	ExportCsv.glade\
	ExportFtree.glade\
	ExportGeneWeb.glade\
	ExportVCalendar.glade\
	ExportVCard.glade\
	ImportGedcom.glade\
	leak.glade\
	merge.glade\
	NotRelated.glade\
	ownereditor.glade\
	patchnames.glade\
	relcalc.glade\
	soundex.glade\
	summary.glade\
	unused.glade\
	verify.glade

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
