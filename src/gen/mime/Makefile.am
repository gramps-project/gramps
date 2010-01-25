# This is the src/gen/mime level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/gen/mime

pkgdata_PYTHON = \
	__init__.py\
	_gnomemime.py\
	_winmime.py\
	_pythonmime.py

pkgpyexecdir = @pkgpyexecdir@/gen/mime
pkgpythondir = @pkgpythondir@/gen/mime

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
