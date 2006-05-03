# This is the src/Filters/Rules/Source level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/Filters/Rules/Source

pkgdata_PYTHON = \
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Filters/Rules/Source
pkgpythondir = @pkgpythondir@/Filters/Rules/Source

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
