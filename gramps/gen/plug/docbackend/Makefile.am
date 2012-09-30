# This is the src/gen/plug/menu level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpythondir = $(datadir)/@PACKAGE@/gen/plug/docbackend

pkgpython_PYTHON = \
	__init__.py \
	cairobackend.py \
	docbackend.py 

pkgpyexecdir = @pkgpyexecdir@/gen/plug/docbackend

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
