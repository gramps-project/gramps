# This is the src/plugins level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

SUBDIRS = \
	drawreport \
	gramplet \
	quickview \
	rel \
	tool

pkgdatadir = $(datadir)/@PACKAGE@/plugins

pkgdata_PYTHON = \
	AgeStats.py\
	AncestorReport.py\
	BookReport.py\
	Calendar.py \
	CustomBookText.py\
	DescendReport.py\
	DetAncestralReport.py\
	DetDescendantReport.py\
	EndOfLineReport.py\
	ExportXml.py\
	FamilyGroup.py\
	ImportGpkg.py\
	ImportXml.py\
	IndivComplete.py\
	KinshipReport.py\
	MarkerReport.py\
	NarrativeWeb.py\
	NumberOfAncestorsReport.py\
	PlaceReport.py\
	Records.py\
	SimpleBookTitle.py\
	Summary.py\
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
