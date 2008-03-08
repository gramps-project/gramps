# This is the src/data level Makefile for gramps
# $Id$
#
SUBDIRS = templates

pkgdatadir = $(datadir)/@PACKAGE@/data

dist_pkgdata_DATA = \
	gedcom.xml \
	papersize.xml \
	system_filters.xml \
	tips.xml\
	lds.xml\
	NWeb-Print_Default.css\
	NWeb-Screen_Basic-Ash.css\
	NWeb-Screen_Basic-Cypress.css\
	NWeb-Screen_Basic-Lilac.css\
	NWeb-Screen_Basic-Peach.css\
	NWeb-Screen_Basic-Spruce.css\
	NWeb-Screen_Mainz.css\
	NWeb-Screen_Nebraska.css\
	NWeb-Screen_Sharp.css

# Rules for files with translatable strings
# These are taken care of by the intltool
xml_in_files = tips.xml.in
xml_files = $(xml_in_files:.xml.in=.xml)
@INTLTOOL_XML_RULE@

EXTRA_DIST = $(xml_in_files)
CLEANFILES = $(xml_files)
