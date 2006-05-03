# This is the src/Filters/Rules/Place level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/Filters/Rules/Place

pkgdata_PYTHON = \
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Filters/Rules/Place
pkgpythondir = @pkgpythondir@/Filters/Rules/Place

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
