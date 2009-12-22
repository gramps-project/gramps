# This is the src/RelLib level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/gen/proxy

pkgdata_PYTHON = \
	__init__.py \
	filter.py \
	living.py \
	private.py \
	referenced.py \
	proxybase.py

pkgpyexecdir = @pkgpyexecdir@/gen/proxy
pkgpythondir = @pkgpythondir@/gen/proxy


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
