# This is the src/gui/filters level Makefile for Gramps
# $Id$

SUBDIRS = sidebar

pkgpythondir = $(datadir)/@PACKAGE@/gui/filters

pkgpython_PYTHON = \
	_FilterComboBox.py \
	_FilterMenu.py \
	_FilterStore.py \
	__init__.py \
	_SearchBar.py

pkgpyexecdir = @pkgpyexecdir@/gui/filters

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
