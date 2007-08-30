# This is the src/Filters/Rules/Note level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/Filters/Rules/Note

pkgdata_PYTHON = \
	_AllNotes.py\
	_HasIdOf.py\
	_HasMarkerOf.py\
	_HasNoteMatchingSubstringOf.py\
	_HasNoteRegexp.py\
	_HasNote.py\
	_HasReferenceCountOf.py\
	_MatchesFilter.py\
	_RegExpIdOf.py\
	_NotePrivate.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Filters/Rules/Note
pkgpythondir = @pkgpythondir@/Filters/Rules/Note

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
