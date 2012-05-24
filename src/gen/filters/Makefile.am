# This is the src/gen/filters level Makefile for Gramps
# $Id$

SUBDIRS = rules

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters

pkgpython_PYTHON = \
	_FilterList.py \
	_FilterParser.py \
	_GenericFilter.py \
	_ParamFilter.py \
	__init__.py \
	_SearchFilter.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
