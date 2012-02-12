# This is the src/plugins/textreport level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpythondir = $(datadir)/@PACKAGE@/plugins/textreport

pkgpython_PYTHON = \
	AlphabeticalIndex.py\
	AncestorReport.py\
	BirthdayReport.py\
	CustomBookText.py\
	DescendReport.py\
	DetAncestralReport.py\
	DetDescendantReport.py\
	EndOfLineReport.py\
	FamilyGroup.py\
	IndivComplete.py\
	KinshipReport.py\
	NumberOfAncestorsReport.py\
	PlaceReport.py\
	SimpleBookTitle.py\
	Summary.py\
	TableOfContents.py\
	TagReport.py\
	textplugins.gpr.py

pkgpyexecdir = @pkgpyexecdir@/plugins/textreport

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
