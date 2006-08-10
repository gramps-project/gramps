# This is the src/Filters/SideBar level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/Filters/SideBar

pkgdata_PYTHON = \
	_EventSidebarFilter.py \
	_FamilySidebarFilter.py \
	__init__.py \
	_SidebarFilter.py \
	_PersonSidebarFilter.py\
	_SourceSidebarFilter.py\
	_PlaceSidebarFilter.py\
	_MediaSidebarFilter.py\
	_RepoSidebarFilter.py

pkgpyexecdir = @pkgpyexecdir@/Filters/SideBar
pkgpythondir = @pkgpythondir@/Filters/SideBar

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
