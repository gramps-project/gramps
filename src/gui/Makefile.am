# This is the src/RelLib level Makefile for Gramps
# $Id$
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

SUBDIRS = \
	editors \
	filters \
	glade \
	logger \
	merge \
	plug \
	selectors \
	views \
	widgets

pkgpythondir = $(datadir)/@PACKAGE@/gui

pkgpython_PYTHON = \
	__init__.py \
	aboutdialog.py \
	basesidebar.py \
	columnorder.py \
	configure.py \
	dbguielement.py \
	dbloader.py \
	dbman.py \
	dialog.py \
	display.py \
	displaystate.py \
	filtereditor.py \
	glade.py \
	grampsbar.py \
	grampsgui.py \
	makefilter.py \
	managedwindow.py \
	navigator.py \
	pluginmanager.py \
	tipofday.py \
	undohistory.py \
	user.py \
	utils.py \
	viewmanager.py

pkgpyexecdir = @pkgpyexecdir@/gui

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
