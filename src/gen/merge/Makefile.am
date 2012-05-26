# This is the src/RelLib level Makefile for Gramps
# $Id: Makefile.am 18851 2012-02-10 20:25:15Z josipsf $
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpythondir = $(datadir)/@PACKAGE@/gen/merge

pkgpython_PYTHON = \
	__init__.py \
	mergepersonquery.py \
	mergefamilyquery.py \
	mergeeventquery.py \
	mergeplacequery.py \
	mergesourcequery.py \
	mergecitationquery.py \
	mergerepositoryquery.py \
	mergemediaquery.py \
	mergenotequery.py

pkgpyexecdir = @pkgpyexecdir@/gen/merge

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
