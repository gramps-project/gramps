# This is the src/Filters/Rules/Media level Makefile for Gramps

pkgpythondir = $(datadir)/@PACKAGE@/Filters/Rules/Repository

pkgpython_PYTHON = \
	_AllRepos.py\
	_ChangedSince.py\
	_HasIdOf.py\
	_HasNoteMatchingSubstringOf.py\
	_HasNoteRegexp.py\
	_HasReferenceCountOf.py\
	_HasRepo.py\
	_MatchesFilter.py\
	_RegExpIdOf.py\
	_RepoPrivate.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Filters/Rules/Repository

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
