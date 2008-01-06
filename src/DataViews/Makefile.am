# This is the src/DataViews level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/DataViews

pkgdata_PYTHON = \
	__init__.py\
	GrampletView.py\
	PersonView.py\
	RelationView.py\
	FamilyList.py\
	PedigreeView.py\
	EventView.py\
	SourceView.py\
	PlaceView.py\
	MediaView.py\
	NoteView.py\
	GoogleView.py\
	RepositoryView.py

#	_MapView.py

pkgpyexecdir = @pkgpyexecdir@/DataViews
pkgpythondir = @pkgpythondir@/DataViews

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));

pylint:
	PYTHONPATH=$(GRAMPS_PY_MODPATH) pylint $(pkgdata_PYTHON) > pylint.out
