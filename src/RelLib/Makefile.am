# This is the src/RelLib level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/RelLib

pkgdata_PYTHON = \
	__init__.py\
	_helper.py\
	_secondary.py\
	Researcher.py\
	GenderStats.py\
	Person.py\
	Family.py\
	Event.py\
	Place.py\
	Source.py\
	MediaObject.py\
	Repository.py

pkgpyexecdir = @pkgpyexecdir@/RelLib
pkgpythondir = @pkgpythondir@/RelLib

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
