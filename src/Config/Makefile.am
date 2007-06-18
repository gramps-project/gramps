# This is the src/Config level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/Config

pkgdata_PYTHON = \
	__init__.py\
	_GrampsGconfKeys.py\
	_GrampsConfigKeys.py\
	_GrampsIniKeys.py

pkgpyexecdir = @pkgpyexecdir@/Config
pkgpythondir = @pkgpythondir@/Config

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
