# This is the src/RelLib level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/ObjectSelector

pkgdata_PYTHON = \
	_Constants.py\
	_Factories.py\
	_FamilyFilterFrame.py\
	_FamilyFrame.py\
	_FamilyPreviewFrame.py\
	_FamilyTreeFrame.py\
	_FilterFrameBase.py\
	_FilterSpec.py\
	_FilterSpecBase.py\
	_ObjectFrameBase.py\
	_ObjectSelectorResult.py\
	_ObjectSelectorWindow.py\
	_PersonFilterFrame.py\
	_PersonFilterSpec.py\
	_PersonFrame.py\
	_PersonPreviewFrame.py\
	_PersonTreeFrame.py\
	__init__.py

pkgpyexecdir = @pkgpyexecdir@/ObjectSelector
pkgpythondir = @pkgpythondir@/ObjectSelector

GRAMPS_PY_MODPATH = "../"

pycheck:
        (export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
        pychecker $(pkgdata_PYTHON));
