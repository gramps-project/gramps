# This is the src/plugins/webstuff level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

SUBDIRS = css images 

pkgdatadir = $(datadir)/@PACKAGE@/plugins/webstuff

pkgdata_PYTHON = \
      webstuff.py \
      webstuff.gpr.py

pkgpyexecdir = @pkgpyexecdir@/plugins/webstuff
pkgpythondir = @pkgpythondir@/plugins/webstuff

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
