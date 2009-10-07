# This is the src/DataViews level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

SUBDIRS = \
	treemodels

pkgdatadir = $(datadir)/@PACKAGE@/gui/views

pkgdata_PYTHON = \
	__init__.py \
	listview.py \
        navigationview.py \
	pageview.py

pkgpyexecdir = @pkgpyexecdir@/gui/views
pkgpythondir = @pkgpythondir@/gui/views

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));

pylint:
	PYTHONPATH=$(GRAMPS_PY_MODPATH) pylint $(pkgdata_PYTHON) > pylint.out
