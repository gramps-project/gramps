pkgdatadir = $(datadir)/@PACKAGE@/maps

pkgdata_PYTHON = \
	constants.py\
	geography.py\
	grampsmaps.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/maps
pkgpythondir = @pkgpythondir@/maps

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
