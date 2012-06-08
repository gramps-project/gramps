# This is the src/gui/editors level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

SUBDIRS = \
	displaytabs

pkgpythondir = $(datadir)/@PACKAGE@/gui/editors

pkgpython_PYTHON = \
	addmedia.py\
	__init__.py\
	editaddress.py \
	editattribute.py \
	editchildref.py \
	editcitation.py \
	editdate.py \
	editevent.py \
	editeventref.py \
	editfamily.py \
	editldsord.py \
	editlocation.py \
	editlink.py \
	editmedia.py \
	editmediaref.py \
	editname.py \
	editnote.py \
	editperson.py \
	editpersonref.py \
	editplace.py \
	editprimary.py \
	editreference.py \
	editrepository.py \
	editreporef.py \
	editsecondary.py \
	editsource.py \
	editurl.py \
	objectentries.py

pkgpyexecdir = @pkgpyexecdir@/gui/editors

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
