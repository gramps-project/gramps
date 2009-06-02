# This is the src/gen/plug/menu level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/gen/plug/docbackend

pkgdata_PYTHON = \
	__init__.py \
	cairobackend.py \
	docbackend.py 

pkgpyexecdir = @pkgpyexecdir@/gen/plug/docbackend
pkgpythondir = @pkgpythondir@/gen/plug/docbackend


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
