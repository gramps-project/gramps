# This is the src/data level Makefile for gramps
# $Id$
#
SUBDIRS = templates

pkgdatadir = $(datadir)/@PACKAGE@/data

dist_pkgdata_DATA = \
        authors.xml \
	gedcom.xml \
	papersize.xml \
	system_filters.xml \
	tips.xml\
	lds.xml\
	Web_Basic-Ash.css\
	Web_Basic-Cypress.css\
	Web_Basic-Lilac.css\
	Web_Basic-Peach.css\
	Web_Basic-Spruce.css\
	Web_Mainz.css\
	Web_Evergreen.css\
	Web_Nebraska.css\
	Web_Print-Default.css\
	Web_Simply-Red.css\
	Web_Visually.css\
	Web_styleswitcher.js\
	Web_styleswitcherMenu.js

# Rules for files with translatable strings
# These are taken care of by the intltool
xml_in_files = tips.xml.in
xml_files = $(xml_in_files:.xml.in=.xml)
@INTLTOOL_XML_RULE@

EXTRA_DIST = $(xml_in_files)
CLEANFILES = $(xml_files)
