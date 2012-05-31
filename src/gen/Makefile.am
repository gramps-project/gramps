# This is the src/RelLib level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

SUBDIRS = \
	datehandler \
	db \
    display \
	filters \
	lib \
	locale \
	merge \
	mime \
	plug \
	proxy \
	simple \
	utils

pkgpythondir = $(datadir)/@PACKAGE@/gen

pkgpython_PYTHON = \
	__init__.py \
	ggettext.py \
	updatecallback.py \
	user.py

pkgpyexecdir = @pkgpyexecdir@/gen

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
