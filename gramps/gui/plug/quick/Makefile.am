# This is the src/gui/plug/quick level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gui/plug/quick

pkgpython_PYTHON = \
	__init__.py\
	_quickreports.py\
	_quicktable.py\
	_textbufdoc.py

pkgpyexecdir = @pkgpyexecdir@/gui/plug/quick

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
