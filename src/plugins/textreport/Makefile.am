# This is the src/plugins/textreport level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpythondir = $(datadir)/@PACKAGE@/plugins/textreport

pkgpython_PYTHON = \
	alphabeticalindex.py\
	ancestorreport.py\
	birthdayreport.py\
	custombooktext.py\
	descendreport.py\
	detancestralreport.py\
	detdescendantreport.py\
	endoflinereport.py\
	familygroup.py\
	indivcomplete.py\
	kinshipreport.py\
	numberofancestorsreport.py\
	placereport.py\
	simplebooktitle.py\
	summary.py\
	tableofcontents.py\
	tagreport.py\
	textplugins.gpr.py

pkgpyexecdir = @pkgpyexecdir@/plugins/textreport

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
