# This is the src/gen/simple level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/simple

pkgpython_PYTHON = \
	_simpledoc.py\
	_simpleaccess.py\
        _simpletable.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gen/simple

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
