# This is the src/Filters/Rules/Place level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules/place

pkgpython_PYTHON = \
	_AllPlaces.py\
	_ChangedSince.py\
	_HasIdOf.py\
	_HasNoLatOrLon.py\
	_InLatLonNeighborhood.py\
	_HasGallery.py \
	_HasNoteMatchingSubstringOf.py\
	_HasNoteRegexp.py\
	_HasPlace.py\
	_HasNote.py \
	_HasReferenceCountOf.py\
	_MatchesFilter.py\
	_MatchesEventFilter.py\
	_PlacePrivate.py\
	_RegExpIdOf.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules/place

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
