pkgdatadir = $(datadir)/@PACKAGE@/plugins/lib/maps

pkgdata_PYTHON = \
	constants.py\
	geography.py\
	grampsmaps.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/plugins/lib/maps
pkgpythondir = @pkgpythondir@/plugins/lib/maps

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../:../view"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
