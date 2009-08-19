# This is the src/RelLib level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/gen/db

pkgdata_PYTHON = \
	__init__.py\
	base.py \
	bsddbtxn.py \
	cursor.py \
	dbconst.py \
	dbdir.py \
	exceptions.py \
	iterator.py \
	read.py \
	txn.py \
	undoredo.py \
	upgrade.py \
	write.py

pkgpyexecdir = @pkgpyexecdir@/gen/db
pkgpythondir = @pkgpythondir@/gen/db


# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
