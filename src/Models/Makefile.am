# This is the src/Mime level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/Models

pkgdata_PYTHON = \
	__init__.py\
	_FastFilterModel.py\
	_FastModel.py\
	_ListCursor.py\
	_PathCursor.py\
	_PersonFilterModel.py\
	_PersonListModel.py\
	_PersonTreeModel.py

pkgpyexecdir = @pkgpyexecdir@/Models
pkgpythondir = @pkgpythondir@/Models

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
