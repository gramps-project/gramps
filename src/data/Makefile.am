# This is the src/data level Makefile for gramps
# $Id$
#
SUBDIRS = 

pkgdatadir = $(datadir)/@PACKAGE@/data

dist_pkgdata_DATA = \
        authors.xml \
	papersize.xml \
	tips.xml\
	lds.xml

# Rules for files with translatable strings
# These are taken care of by the intltool
xml_in_files = tips.xml.in
xml_files = $(xml_in_files:.xml.in=.xml)
@INTLTOOL_XML_NOMERGE_RULE@

EXTRA_DIST = $(xml_in_files)
CLEANFILES = $(xml_files)
