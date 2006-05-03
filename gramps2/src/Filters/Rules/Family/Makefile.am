# This is the src/Filters/Rules/Family level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/Filters/Rules/Family

pkgdata_PYTHON = \
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Filters/Rules/Family
pkgpythondir = @pkgpythondir@/Filters/Rules/Family

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
