# This is the src/Report level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/Simple

pkgpython_PYTHON = \
	_SimpleDoc.py\
	_SimpleAccess.py\
        _SimpleTable.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Simple
pkgpythondir = $(datadir)/@PACKAGE@/Simple

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
