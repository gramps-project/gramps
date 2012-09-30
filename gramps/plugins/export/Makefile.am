# This is the src/plugins/export level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpython_PYTHON = \
	export.gpr.py \
	exportcsv.py \
	exportftree.py \
	exportgedcom.py \
	exportgeneweb.py \
	exportpkg.py \
	exportvcalendar.py \
	exportvcard.py \
	exportxml.py

pkgpyexecdir = @pkgpyexecdir@/plugins/export
pkgpythondir = $(datadir)/@PACKAGE@/plugins/export


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
