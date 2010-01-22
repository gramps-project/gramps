# This is the src/gen/display level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/gen/display

pkgdata_PYTHON = \
	name.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gen/display
pkgpythondir = @pkgpythondir@/gen/display


dist_pkgdata_DATA = 

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
