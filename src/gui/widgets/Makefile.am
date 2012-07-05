# This is the src/gui/widgets level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgpythondir = $(datadir)/@PACKAGE@/gui/widgets

pkgpython_PYTHON = \
	__init__.py \
	basicentry.py \
	buttons.py \
	expandcollapsearrow.py \
	grampletpane.py \
	labels.py \
	linkbox.py \
	menuitem.py \
	menutoolbuttonaction.py \
	monitoredwidgets.py \
	multitreeview.py \
	photo.py \
	progressdialog.py \
	shortlistcomboentry.py \
	springseparator.py \
	statusbar.py \
	styledtextbuffer.py \
	styledtexteditor.py \
	toolcomboentry.py \
	undoablebuffer.py \
	undoableentry.py \
	undoablestyledbuffer.py \
	validatedcomboentry.py \
	validatedmaskedentry.py \
	valueaction.py \
	valuetoolitem.py

pkgpyexecdir = @pkgpyexecdir@/gui/widgets

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));

