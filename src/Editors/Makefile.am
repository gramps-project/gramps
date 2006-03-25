# This is the src/Editors level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/Editors

pkgdata_PYTHON = \
	__init__.py\
	_EditAddress.py \
	_EditAttribute.py \
	_EditEvent.py \
	_EditEventRef.py \
	_EditFamily.py \
	_EditLocation.py \
	_EditMedia.py \
	_EditMediaRef.py \
	_EditName.py \
	_EditPerson.py \
	_EditPlace.py \
	_EditPrimary.py \
	_EditReference.py \
	_EditRepository.py \
	_EditRepoRef.py \
	_EditSecondary.py \
	_EditSource.py \
	_EditSourceRef.py \
	_EditUrl.py

pkgpyexecdir = @pkgpyexecdir@/Editors
pkgpythondir = @pkgpythondir@/Editors

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
