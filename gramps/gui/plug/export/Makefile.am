# This is the src/gui/plug/export level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gui/plug/export

pkgpython_PYTHON = \
	__init__.py\
	_exportassistant.py\
	_exportoptions.py

pkgpyexecdir = @pkgpyexecdir@/gui/plug/export

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
