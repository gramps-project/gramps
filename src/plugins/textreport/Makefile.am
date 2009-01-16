# This is the src/plugins/textreport level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/textreport

pkgdata_PYTHON = \
	AncestorReport.py\
	CustomBookText.py\
	DescendReport.py\
	DetAncestralReport.py\
	DetDescendantReport.py\
	EndOfLineReport.py\
	FamilyGroup.py\
	IndivComplete.py\
	KinshipReport.py\
	MarkerReport.py\
	NumberOfAncestorsReport.py\
	PlaceReport.py\
	SimpleBookTitle.py\
	Summary.py\

pkgpyexecdir = @pkgpyexecdir@/plugins/textreport
pkgpythondir = @pkgpythondir@/plugins/textreport

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
