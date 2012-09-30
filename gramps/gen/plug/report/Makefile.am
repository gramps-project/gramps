# This is the src/gen/plug/report level Makefile for Gramps
# $Id$

pkgdatadir = $(datadir)/@PACKAGE@/gen/plug/report

pkgpython_PYTHON = \
	__init__.py\
	_bibliography.py\
	_constants.py\
        _options.py\
	_paper.py\
	_reportbase.py\
	endnotes.py\
	utils.py

pkgpyexecdir = @pkgpyexecdir@/gen/plug/report
pkgpythondir = $(datadir)/@PACKAGE@/gen/plug/report

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
