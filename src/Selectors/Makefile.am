# This is the src/Selectors level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/Selectors

pkgdata_PYTHON = \
	__init__.py \
	_BaseSelector.py \
	_SelectEvent.py \
	_SelectFamily.py \
	_SelectNote.py \
	_SelectObject.py \
	_SelectPerson.py \
	_SelectRepository.py \
	_SelectSource.py \
	_SelectPlace.py \
	_SelectorExceptions.py \
	_SelectorFactory.py

pkgpyexecdir = @pkgpyexecdir@/Selectors
pkgpythondir = @pkgpythondir@/Selectors

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
