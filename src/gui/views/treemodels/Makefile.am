# This is the src/DataViews level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpythondir = $(datadir)/@PACKAGE@/gui/views/treemodels

pkgpython_PYTHON = \
	__init__.py \
	bugfix.py \
	eventmodel.py \
	familymodel.py \
	flatbasemodel.py \
	lru.py \
	mediamodel.py \
	notemodel.py \
	peoplemodel.py \
	placemodel.py \
	repomodel.py \
	sourcemodel.py \
	citationbasemodel.py \
	citationlistmodel.py \
	citationtreemodel.py \
	treebasemodel.py

pkgpyexecdir = @pkgpyexecdir@/gui/views/treemodels

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));

pylint:
	PYTHONPATH=$(GRAMPS_PY_MODPATH) pylint $(pkgpython_PYTHON) > pylint.out
