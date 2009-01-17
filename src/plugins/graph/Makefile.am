# This is the src/plugins/graph level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/graph

pkgdata_PYTHON = \
	GVFamilyLines.py \
	GVHourGlass.py \
	GVRelGraph.py

pkgpyexecdir = @pkgpyexecdir@/plugins/graph
pkgpythondir = @pkgpythondir@/plugins/graph

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
