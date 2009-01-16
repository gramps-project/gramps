# This is the src/plugins level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

SUBDIRS = \
	rel \
	tool

pkgdatadir = $(datadir)/@PACKAGE@/plugins

pkgdata_PYTHON = \
	all_events.py\
	all_relations.py\
	AgeOnDate.py\
	AgeStats.py\
	AncestorTree.py\
	AncestorReport.py\
	AttributeMatch.py\
	AttributesGramplet.py\
	BookReport.py\
	Calendar.py \
	CustomBookText.py\
	DefaultGramplets.py\
	DescendTree.py\
	DescendReport.py\
	DescendGramplet.py\
	DetAncestralReport.py\
	DetDescendantReport.py\
	EndOfLineReport.py\
	ExportCd.py\
	ExportCsv.py\
	ExportFtree.py\
	ExportGedcom.py\
	ExportGeneWeb.py\
	ExportPkg.py\
	ExportVCalendar.py\
	ExportVCard.py\
	ExportXml.py\
	FamilyGroup.py\
	FanChart.py\
	FilterByName.py\
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
	lineage.py\
	MarkerReport.py\
	NarrativeWeb.py\
	NumberOfAncestorsReport.py\
	OnThisDay.py\
	PlaceReport.py\
	Records.py\
	References.py\
	SameSurnames.py\
	siblings.py\
	SimpleBookTitle.py\
	StatisticsChart.py\
	Summary.py\
	TimeLine.py\
	WebCal.py\
	WhatsNext.py

pkgpyexecdir = @pkgpyexecdir@/plugins
pkgpythondir = @pkgpythondir@/plugins

GLADEFILES = \
	book.glade\
	ExportCsv.glade\
	ExportFtree.glade\
	ExportGeneWeb.glade\
	ExportVCalendar.glade\
	ExportVCard.glade\
	ImportGedcom.glade

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
