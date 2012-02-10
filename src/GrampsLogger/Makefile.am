# This is the src/GrampsLogger level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpython_PYTHON = \
	_ErrorReportAssistant.py\
	_ErrorView.py\
	_GtkHandler.py\
	__init__.py\
	_RotateHandler.py

pkgpyexecdir = @pkgpyexecdir@/GrampsLogger
pkgpythondir = $(datadir)/@PACKAGE@/GrampsLogger

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
