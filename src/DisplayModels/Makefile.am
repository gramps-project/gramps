# This is the src/DisplayModels level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/DisplayModels

pkgdata_PYTHON = \
	__init__.py \
	_BaseModel.py \
	_EventModel.py \
	_FamilyModel.py \
	_MediaModel.py \
	_PeopleModel.py \
	_PlaceModel.py \
	_RepositoryModel.py \
	_SourceModel.py

pkgpyexecdir = @pkgpyexecdir@/DisplayModels
pkgpythondir = @pkgpythondir@/DisplayModels

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
