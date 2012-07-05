# This is the src/plugins/graph level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpythondir = $(datadir)/@PACKAGE@/plugins/graph

pkgpython_PYTHON = \
	graphplugins.gpr.py\
	gvfamilylines.py \
	gvhourglass.py \
	gvrelgraph.py

pkgpyexecdir = @pkgpyexecdir@/plugins/graph

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
