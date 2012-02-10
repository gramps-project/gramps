# This is the src/cli/plug level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/cli/plug

pkgpython_PYTHON = \
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/cli/plug
pkgpythondir = $(datadir)/@PACKAGE@/cli/plug


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
