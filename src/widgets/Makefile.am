# This is the src/widgets level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/widgets

pkgdata_PYTHON = \
	__init__.py \
	grampswidgets.py \
	multitypecomboentry.py \
	toolbarwidgets.py \
	styledtextbuffer.py \
	styledtexteditor.py

pkgpyexecdir = @pkgpyexecdir@/widgets
pkgpythondir = @pkgpythondir@/widgets

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
