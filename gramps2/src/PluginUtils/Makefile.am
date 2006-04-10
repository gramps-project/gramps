# This is the src/PluginUtils level Makefile for Gramps
# We could use GNU make's ':=' syntax for nice wildcard use,
# but that is not necessarily portable.
# If not using GNU make, then list all .py files individually

pkgdatadir = $(datadir)/@PACKAGE@/PluginUtils

pkgdata_PYTHON = \
	__init__.py\
	_Options.py\
	_ReportOptions.py\
	_Report.py\
	_ReportUtils.py\
	_Tool.py\
	_StyleEditor.py\
	_PluginMgr.py\
	_PaperMenu.py\
	_Plugins.py

pkgpyexecdir = @pkgpyexecdir@/PluginUtils
pkgpythondir = @pkgpythondir@/PluginUtils

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(pkgdata_PYTHON));
