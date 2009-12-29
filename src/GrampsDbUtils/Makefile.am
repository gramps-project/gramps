# This is the src/GrampsDbUtils level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/GrampsDbUtils

pkgdata_PYTHON = \
	_GedcomParse.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/GrampsDbUtils
pkgpythondir = @pkgpythondir@/GrampsDbUtils

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));

pylint: 
	(export PYTHONPATH=..:.; pylint --rcfile=pylintrc _GedcomParse.py)
