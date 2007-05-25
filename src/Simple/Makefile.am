# This is the src/Report level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/Simple

pkgdata_PYTHON = \
	_SimpleDoc.py\
	_SimpleAccess.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Simple
pkgpythondir = @pkgpythondir@/Simple

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
