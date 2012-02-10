# This is the src/Filters/Rules/Citation level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/Filters/Rules/Citation

pkgpython_PYTHON = \
	__init__.py \
	_AllCitations.py \
	_ChangedSince.py \
	_CitationPrivate.py \
	_HasGallery.py \
	_HasIdOf.py \
	_HasNote.py \
	_HasNoteMatchingSubstringOf.py \
	_HasNoteRegexp.py \
	_HasReferenceCountOf.py \
	_HasSource.py \
	_MatchesFilter.py \
	_MatchesPageSubstringOf.py \
	_MatchesRepositoryFilter.py \
	_MatchesSourceFilter.py \
	_RegExpIdOf.py

pkgpyexecdir = @pkgpyexecdir@/Filters/Rules/Citation

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
