# This is the src/Filters/SideBar level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/Filters/SideBar

pkgpython_PYTHON = \
	_EventSidebarFilter.py \
	_FamilySidebarFilter.py \
	__init__.py \
	_SidebarFilter.py \
	_PersonSidebarFilter.py\
	_SourceSidebarFilter.py\
	_CitationSidebarFilter.py\
	_PlaceSidebarFilter.py\
	_MediaSidebarFilter.py\
	_RepoSidebarFilter.py\
	_NoteSidebarFilter.py

pkgpyexecdir = @pkgpyexecdir@/Filters/SideBar

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
