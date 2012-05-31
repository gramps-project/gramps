# This is the src/GrampsLogger level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpython_PYTHON = \
	_errorreportassistant.py\
	_errorview.py\
	_gtkhandler.py\
	__init__.py\
	_rotatehandler.py

pkgpyexecdir = @pkgpyexecdir@/gui/logger
pkgpythondir = $(datadir)/@PACKAGE@/gui/logger

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
