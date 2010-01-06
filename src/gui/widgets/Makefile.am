# This is the src/gui/widgets level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/gui/widgets

pkgdata_PYTHON = \
	__init__.py \
	buttons.py \
	expandcollapsearrow.py \
	labels.py \
	linkbox.py \
	menutoolbuttonaction.py \
	monitoredwidgets.py \
	progressdialog.py \
	shortlistcomboentry.py \
	springseparator.py \
	statusbar.py \
	styledtextbuffer.py \
	styledtexteditor.py \
	toolcomboentry.py \
	validatedcomboentry.py \
	validatedmaskedentry.py \
	valueaction.py \
	valuetoolitem.py

pkgpyexecdir = @pkgpyexecdir@/gui/widgets
pkgpythondir = @pkgpythondir@/gui/widgets

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));

