# This is the src/data level Makefile for gramps
# $Id$
#
pkgdatadir = $(datadir)/@PACKAGE@/data

dist_pkgdata_DATA = \
	gedcom.xml \
	papersize.xml \
	system_filters.xml \
	tips.xml\
	main1.css\
	main2.css\
	main3.css\
	main4.css\
	main5.css\
	main6.css

# Rules for files with translatable strings
# These are taken care of by the intltool
xml_in_files = tips.xml.in
xml_files = $(xml_in_files:.xml.in=.xml)
@INTLTOOL_XML_RULE@

EXTRA_DIST = $(xml_in_files)
CLEANFILES = $(xml_files)
