# This is the src/RelLib level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/GrampsDb

pkgdata_PYTHON = \
	_DbUtils.py \
	_GrampsBSDDB.py\
	_GrampsDbBase.py\
	_GrampsDBCallback.py\
	_GrampsDbExceptions.py\
	_GrampsDbFactories.py\
	_GrampsGEDDB.py\
	_GrampsInMemDB.py\
	_GrampsXMLDB.py\
	_GrampsDbConst.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/GrampsDb
pkgpythondir = @pkgpythondir@/GrampsDb


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
