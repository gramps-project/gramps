# This is the src/Filters level Makefile for Gramps

SUBDIRS = Rules

pkgdatadir = $(datadir)/@PACKAGE@/Filters

pkgdata_PYTHON = \
	_FilterComboBox.py \
	_FilterList.py \
	_FilterMenu.py \
	_FilterParser.py \
	_FilterStore.py \
	_FilterWidget.py \
	_GenericFilter.py \
	_ParamFilter.py \
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Filters
pkgpythondir = @pkgpythondir@/Filters

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
