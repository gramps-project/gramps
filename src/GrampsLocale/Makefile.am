# This is the src/GrampsLocale level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/GrampsLocale

pkgdata_PYTHON = \
	_GrampsLocale.py\
	__init__.py
	

pkgpyexecdir = @pkgpyexecdir@/GrampsLocale
pkgpythondir = @pkgpythondir@/GrampsLocale


dist_pkgdata_DATA = 

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
