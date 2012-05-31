# This is the src/gui/plug/quick level Makefile for Gramps
# $Id: Makefile.am 18851 2012-02-10 20:25:15Z josipsf $

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
