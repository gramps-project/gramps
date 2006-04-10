# This is the src/docgen level Makefile for Gramps
# Use GNU make's ':=' syntax for nice wildcard use.
# If not using GNU make, then list all .py files individually

docgendir=$(prefix)/share/gramps/docgen

docgen_PYTHON = \
	AbiWord2Doc.py\
	AsciiDoc.py\
	HtmlDoc.py\
	KwordDoc.py\
	LaTeXDoc.py\
	ODFDoc.py\
	OpenOfficeDoc.py\
	OpenSpreadSheet.py\
	SpreadSheetDoc.py\
	PdfDoc.py\
	PSDrawDoc.py\
	RTFDoc.py\
	SvgDrawDoc.py\
	LPRDoc.py

# Clean up all the byte-compiled files
MOSTLYCLEANFILES = *pyc *pyo

GRAMPS_PY_MODPATH = "../"

pycheck: 
	(export PYTHONPATH=$(GRAMPS_PY_MODPATH); \
	pychecker $(docgen_PYTHON));
