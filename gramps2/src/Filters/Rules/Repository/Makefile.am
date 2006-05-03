# This is the src/Filters/Rules/Media level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/Filters/Rules/Repository

pkgdata_PYTHON = \
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Filters/Rules/Repository
pkgpythondir = @pkgpythondir@/Filters/Rules/Repository

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
