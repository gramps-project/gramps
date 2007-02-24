# This is the src/Filters/Rules level Makefile for Gramps

SUBDIRS = Person Family Event Place Source MediaObject Repository Note

pkgdatadir = $(datadir)/@PACKAGE@/Filters/Rules

pkgdata_PYTHON = \
	_Everything.py\
	_HasEventBase.py\
	_HasAttributeBase.py\
	_HasGrampsId.py\
	_HasNoteRegexBase.py\
	_HasNoteSubstrBase.py\
	_HasTextMatchingRegexpOf.py\
	_HasTextMatchingSubstringOf.py\
	__init__.py\
	_IsPrivate.py\
	_RegExpIdBase.py\
	_Rule.py\
	_RuleUtils.py\
	_MatchesFilterBase.py\
	_HasMarkerBase.py

pkgpyexecdir = @pkgpyexecdir@/Filters/Rules
pkgpythondir = @pkgpythondir@/Filters/Rules

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
