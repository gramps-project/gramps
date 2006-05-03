# This is the src/Filters/Rules level Makefile for Gramps

SUBDIRS = Person Family Event Place Source Media Repository

pkgdatadir = $(datadir)/@PACKAGE@/Filters/Rules

pkgdata_PYTHON = \
	_Rule.py \
	_RuleUtils.py \
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/Filters/Rules
pkgpythondir = @pkgpythondir@/Filters/Rules

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
