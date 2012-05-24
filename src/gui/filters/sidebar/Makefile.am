# This is the src/gui/filters/sidebar level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gui/filters/sidebar

pkgpython_PYTHON = \
	_eventsidebarfilter.py \
	_familysidebarfilter.py \
	__init__.py \
	_sidebarfilter.py \
	_personsidebarfilter.py\
	_sourcesidebarfilter.py\
	_citationsidebarfilter.py\
	_placesidebarfilter.py\
	_mediasidebarfilter.py\
	_reposidebarfilter.py\
	_notesidebarfilter.py

pkgpyexecdir = @pkgpyexecdir@/gui/filters/sidebar

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
