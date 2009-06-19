# This is the src/RelLib level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

SUBDIRS = \
	views

pkgdatadir = $(datadir)/@PACKAGE@/gui

pkgdata_PYTHON = \
	__init__.py \
	dbloader.py \
	dbman.py \
	grampsgui.py \
	utilsgui.py \
	viewmanager.py

pkgpyexecdir = @pkgpyexecdir@/gui
pkgpythondir = @pkgpythondir@/gui


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
