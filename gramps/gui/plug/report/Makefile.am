# This is the src/gui/plug/report level Makefile for Gramps
# $Id$

pkgpythondir = $(datadir)/@PACKAGE@/gui/plug/report

pkgpython_PYTHON = \
	__init__.py\
	_docreportdialog.py\
	_drawreportdialog.py\
	_fileentry.py\
	_graphvizreportdialog.py\
	_papermenu.py\
	_reportdialog.py\
	_stylecombobox.py\
	_styleeditor.py\
	_textreportdialog.py\
	_webreportdialog.py

pkgpyexecdir = @pkgpyexecdir@/gui/plug/report

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgpython_PYTHON));
