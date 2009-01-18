# This is the src/plugins/drawreport level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/gramplet

pkgdata_PYTHON = \
	AgeStats.py \
	AttributesGramplet.py \
	DefaultGramplets.py \
	DescendGramplet.py \
	GivenNameGramplet.py \
	NoteGramplet.py \
	WhatsNext.py

pkgpyexecdir = @pkgpyexecdir@/plugins/gramplet
pkgpythondir = @pkgpythondir@/plugins/gramplet

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
