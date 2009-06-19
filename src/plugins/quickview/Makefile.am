# This is the src/plugins/quickview level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/quickview

pkgdata_PYTHON = \
	AgeOnDate.py \
	all_events.py \
	all_relations.py \
	AttributeMatch.py \
	FilterByName.py \
	lineage.py \
	OnThisDay.py \
	References.py \
	Reporef.py \
	SameSurnames.py\
	siblings.py

pkgpyexecdir = @pkgpyexecdir@/plugins/quickview
pkgpythondir = @pkgpythondir@/plugins/quickview

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
