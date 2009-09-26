# This is the src/data level Makefile for gramps
# $Id$
#
SUBDIRS = 

pkgdatadir = $(datadir)/@PACKAGE@/data

dist_pkgdata_DATA = \
        authors.xml \
	gedcom.xml \
	papersize.xml \
	tips.xml\
	lds.xml\
	behaviour.css\
	GeoView.css \
	Web_Basic-Ash.css\
	Web_Basic-Cypress.css\
	Web_Basic-Lilac.css\
	Web_Basic-Peach.css\
	Web_Basic-Spruce.css\
	Web_Mainz.css\
	Web_Nebraska.css\
	Web_Print-Default.css\
	Web_Visually.css

# Rules for files with translatable strings
# These are taken care of by the intltool
xml_in_files = tips.xml.in
xml_files = $(xml_in_files:.xml.in=.xml)
@INTLTOOL_XML_RULE@

EXTRA_DIST = $(xml_in_files)
CLEANFILES = $(xml_files)
