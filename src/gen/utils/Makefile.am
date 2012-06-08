# This is the src/RelLib level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpythondir = $(datadir)/@PACKAGE@/gen/utils

pkgpython_PYTHON = \
	__init__.py \
	callback.py \
	callman.py \
	configmanager.py \
	fallback.py \
	place.py

pkgpyexecdir = @pkgpyexecdir@/gen/utils

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
