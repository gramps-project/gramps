# This is the src/Selectors level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/gui/selectors

pkgdata_PYTHON = \
	__init__.py \
	baseselector.py \
	selectevent.py \
	selectfamily.py \
	selectnote.py \
	selectobject.py \
	selectperson.py \
	selectrepository.py \
	selectsource.py \
	selectplace.py \
	selectorexceptions.py \
	selectorfactory.py

pkgpyexecdir = @pkgpyexecdir@/gui/selectors
pkgpythondir = @pkgpythondir@/gui/selectors

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
