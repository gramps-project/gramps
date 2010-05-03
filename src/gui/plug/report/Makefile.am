# This is the src/gui/plug/report level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/gui/plug/report

pkgdata_PYTHON = \
	__init__.py\
	_docreportdialog.py\
	_drawreportdialog.py\
	_fileentry.py\
	_graphvizreportdialog.py\
        _options.py\
	_papermenu.py\
	_reportdialog.py\
	_stylecombobox.py\
	_styleeditor.py\
	_textreportdialog.py\
	_webreportdialog.py

pkgpyexecdir = @pkgpyexecdir@/gui/plug/report
pkgpythondir = @pkgpythondir@/gui/plug/report

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../../../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
