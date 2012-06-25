# This is the src/RelLib level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

SUBDIRS = docgen

pkgpythondir = $(datadir)/@PACKAGE@/gen/utils

pkgpython_PYTHON = \
	__init__.py \
	alive.py \
	callback.py \
	callman.py \
	cast.py \
	configmanager.py \
	db.py \
	file.py \
	id.py \
	image.py \
	keyword.py \
	lds.py \
	name.py \
	mactrans.py \
	place.py \
	referent.py \
	string.py \
	trans.py \
	tree.py \
	unknown.py

pkgpyexecdir = @pkgpyexecdir@/gen/utils

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
