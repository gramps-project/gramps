# This is the src/Report level Makefile for Gramps

pkgdatadir = $(datadir)/@PACKAGE@/ReportBase

pkgdata_PYTHON = \
	__init__.py\
	_BareReportDialog.py\
	_Bibliography.py\
	_BookFormatComboBox.py\
	_CommandLineReport.py\
	_Constants.py\
	_DocReportDialog.py\
	_DrawFormatComboBox.py\
	_DrawReportDialog.py\
	_Endnotes.py\
	_FileEntry.py\
	_GraphvizReportDialog.py\
	_PaperMenu.py\
	_PrintTools.py\
	_Report.py\
	_ReportDialog.py\
	_ReportOptions.py\
	_ReportUtils.py\
	_StyleComboBox.py\
	_StyleEditor.py\
	_TemplateParser.py\
	_TextFormatComboBox.py\
	_TextReportDialog.py

pkgpyexecdir = @pkgpyexecdir@/ReportBase
pkgpythondir = @pkgpythondir@/ReportBase

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
