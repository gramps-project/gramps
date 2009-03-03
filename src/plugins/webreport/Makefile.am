# This is the src/plugins/webreport level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/webreport

pkgdata_PYTHON = \
	NarrativeWeb.py \
	WebCal.py \
    html.py

pkgpyexecdir = @pkgpyexecdir@/plugins/webreport
pkgpythondir = @pkgpythondir@/plugins/webreport

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
