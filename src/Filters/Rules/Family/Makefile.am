# This is the src/Filters/Rules/Family level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/Filters/Rules/Family

pkgdata_PYTHON = \
	_AllFamilies.py\
	_FamilyPrivate.py\
	_HasEvent.py\
	_HasIdOf.py\
	_HasNoteMatchingSubstringOf.py\
	_HasNoteRegexp.py\
	_HasRelType.py\
	__init__.py\
	_RegExpIdOf.py\
	_MatchesFilter.py\
	_FatherHasNameOf.py\
	_FatherHasIdOf.py\
	_MotherHasNameOf.py\
	_MotherHasIdOf.py\
	_ChildHasNameOf.py\
	_ChildHasIdOf.py


pkgpyexecdir = @pkgpyexecdir@/Filters/Rules/Family
pkgpythondir = @pkgpythondir@/Filters/Rules/Family

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
