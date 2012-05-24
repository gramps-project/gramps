# This is the src/Filters/Rules/Media level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters/rules/repository

pkgpython_PYTHON = \
	_AllRepos.py\
	_ChangedSince.py\
	_HasIdOf.py\
	_HasNoteMatchingSubstringOf.py\
	_HasNoteRegexp.py\
	_HasReferenceCountOf.py\
	_HasRepo.py\
	_MatchesFilter.py\
        _MatchesNameSubstringOf.py\
	_RegExpIdOf.py\
	_RepoPrivate.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters/rules/repository

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
