# This is the src/PluginUtils level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

SUBDIRS = \
	export \
	quick \
	report

pkgpythondir = $(datadir)/@PACKAGE@/gui/plug

pkgpython_PYTHON = \
	__init__.py\
	_guioptions.py\
	_windows.py\
	_dialogs.py\
	tool.py

pkgpyexecdir = @pkgpyexecdir@/gui/plug

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
