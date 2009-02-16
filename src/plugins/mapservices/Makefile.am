# This is the src/plugins/mapservices level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/mapservices

pkgdata_PYTHON = \
	googlemap.py\
	openstreetmap.py\
	eniroswedenmap.py

pkgpyexecdir = @pkgpyexecdir@/plugins/mapservices
pkgpythondir = @pkgpythondir@/plugins/mapservices

GLADEFILES = 

GRAPHICS = 

DATAFILES = 

dist_pkgdata_DATA = $(GLADEFILES) $(GRAPHICS) $(DATAFILES)

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
