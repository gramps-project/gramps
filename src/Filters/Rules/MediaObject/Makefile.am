# This is the src/Filters/Rules/MediaObject level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/Filters/Rules/MediaObject

pkgdata_PYTHON = \
	_AllMedia.py\
	_HasIdOf.py\
	_HasMedia.py\
	_HasNoteMatchingSubstringOf.py\
	_HasNoteRegexp.py\
	_MatchesFilter.py\
	_MediaPrivate.py\
	_RegExpIdOf.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Filters/Rules/MediaObject
pkgpythondir = @pkgpythondir@/Filters/Rules/MediaObject

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
