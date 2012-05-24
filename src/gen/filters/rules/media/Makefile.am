# This is the src/Filters/Rules/MediaObject level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules/media

pkgpython_PYTHON = \
	_AllMedia.py\
	_ChangedSince.py\
	_HasIdOf.py\
	_HasMedia.py\
	_HasNoteMatchingSubstringOf.py\
	_HasNoteRegexp.py\
	_HasReferenceCountOf.py\
	_HasTag.py\
	_MatchesFilter.py\
	_MediaPrivate.py\
	_HasAttribute.py\
	_RegExpIdOf.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules/media


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
