# This is the src/DisplayTabs level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/FilterEditor

pkgdata_PYTHON = \
	__init__.py \
	_FilterEditor.py \
	_EditFilter.py \
	_EditRule.py \
	_ShowResults.py

pkgpyexecdir = @pkgpyexecdir@/FilterEditor
pkgpythondir = @pkgpythondir@/FilterEditor

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
