# This is the src/plugins/quickview level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/plugins/quickview

pkgpython_PYTHON = \
	ageondate.py \
	all_events.py \
	all_relations.py \
	attributematch.py \
	filterbyname.py \
	lineage.py \
	onthisday.py \
	quickview.gpr.py \
	references.py \
	linkreferences.py \
	reporef.py \
	samesurnames.py\
	siblings.py

pkgpyexecdir = @pkgpyexecdir@/plugins/quickview
pkgpythondir = $(datadir)/@PACKAGE@/plugins/quickview

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
