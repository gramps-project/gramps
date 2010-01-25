# This is the src/gen/plug level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

SUBDIRS = \
	docbackend\
	docgen\
	menu

pkgdatadir = $(datadir)/@PACKAGE@/gen/plug

pkgdata_PYTHON = \
	__init__.py \
	_docgenplugin.py \
	_export.py \
	_gramplet.py \
	_import.py \
	_manager.py \
	_plugin.py \
    _pluginreg.py \
	utils.py

pkgpyexecdir = @pkgpyexecdir@/gen/plug
pkgpythondir = @pkgpythondir@/gen/plug


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
