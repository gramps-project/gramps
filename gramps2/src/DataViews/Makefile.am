# This is the src/DataViews level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/DataViews

pkgdata_PYTHON = \
	__init__.py\
	PersonView.py\
	FamilyView.py\
	FamilyList.py\
	PedView.py\
	EventView.py\
	SourceView.py\
	PlaceView.py\
	MediaView.py\
	MapView.py\
	RepositoryView.py

pkgpyexecdir = @pkgpyexecdir@/DataViews
pkgpythondir = @pkgpythondir@/DataViews

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
