# This is the src/BasicUtils level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/BasicUtils

pkgdata_PYTHON = \
	BasicUtils.py\
	__init__.py
	

pkgpyexecdir = @pkgpyexecdir@/BasicUtils
pkgpythondir = @pkgpythondir@/BasicUtils


dist_pkgdata_DATA = 

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
