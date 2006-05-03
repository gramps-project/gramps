# This is the src/Filters/Rules/Event level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/Filters/Rules/Event

pkgdata_PYTHON = \
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Filters/Rules/Event
pkgpythondir = @pkgpythondir@/Filters/Rules/Event

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
