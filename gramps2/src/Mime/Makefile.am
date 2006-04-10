# This is the src/Mime level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/Mime

pkgdata_PYTHON = \
	__init__.py\
	_GnomeMime.py\
	_PythonMime.py

pkgpyexecdir = @pkgpyexecdir@/Mime
pkgpythondir = @pkgpythondir@/Mime

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
