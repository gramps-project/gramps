# This is the src/gen/filters level Makefile for Gramps
# $Id$

SUBDIRS = rules

pkgpythondir = $(datadir)/@PACKAGE@/gen/filters

pkgpython_PYTHON = \
	_filterlist.py \
	_filterparser.py \
	_genericfilter.py \
	_paramfilter.py \
	__init__.py \
	_searchfilter.py

pkgpyexecdir = @pkgpyexecdir@/gen/filters

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
