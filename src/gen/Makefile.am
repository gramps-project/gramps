# This is the src/RelLib level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

SUBDIRS = \
	db \
    display \
	lib \
	mime \
	plug \
	proxy \
	utils

pkgdatadir = $(datadir)/@PACKAGE@/gen

pkgdata_PYTHON = \
	__init__.py \
	ggettext.py \
	updatecallback.py

pkgpyexecdir = @pkgpyexecdir@/gen
pkgpythondir = @pkgpythondir@/gen


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
