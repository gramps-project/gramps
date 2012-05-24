# This is the src/Filters/Rules/Note level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules/note

pkgpython_PYTHON = \
	_AllNotes.py\
	_ChangedSince.py\
	_HasIdOf.py\
	_MatchesSubstringOf.py\
	_MatchesRegexpOf.py\
	_HasNote.py\
	_HasReferenceCountOf.py\
	_HasTag.py\
	_MatchesFilter.py\
	_RegExpIdOf.py\
	_NotePrivate.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules/note

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
