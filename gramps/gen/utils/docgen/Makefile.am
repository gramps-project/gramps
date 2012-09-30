# This is the src/docgen level Makefile for Gramps
# $Id$
# Use GNU make's ':=' syntax for nice wildcard use.
# If not using GNU make, then list all .py files individually

pkgpythondir = $(datadir)/@PACKAGE@/gen/utils/docgen

pkgpython_PYTHON = \
	__init__.py \
	CSVTab.py \
	ODSTab.py \
	TabbedDoc.py

pkgpyexecdir = @pkgpyexecdir@/gen/utils/docgen

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
