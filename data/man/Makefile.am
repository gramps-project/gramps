# This is the data/man level Makefile for Gramps
# $Id$

SUBDIRS = fr

man_IN_FILES = gramps.1.in
man_MANS = $(man_IN_FILES:.1.in=.1)

EXTRA_DIST = $(man_MANS) $(man_IN_FILES)

gramps.1: $(top_builddir)/config.status gramps.1.in
	cd $(top_builddir) && CONFIG_FILES=data/man/$@ $(SHELL) ./config.status

CLEANFILES=$(man_MANS)
