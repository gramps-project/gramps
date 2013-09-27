# This is the src/Filters/Rules/Source level Makefile for Gramps

pkgpythondir = $(datadir)/@PACKAGE@/Filters/Rules/Source

pkgpython_PYTHON = \
	_ChangedSince.py\
	_MatchesFilter.py\
	_SourcePrivate.py\
	_RegExpIdOf.py\
	_HasGallery.py \
	_HasNoteMatchingSubstringOf.py\
	_HasReferenceCountOf.py\
	_AllSources.py\
	_HasIdOf.py\
	_HasSource.py\
	_HasNote.py \
	_HasNoteRegexp.py\
	_HasRepository.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Filters/Rules/Source

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
