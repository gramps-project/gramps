# This is the data/man/pl level Makefile for Gramps
# $Id: Makefile.am 6189 2006-03-21 19:05:46Z rshura $

man_IN_FILES = gramps.1.in
man_MANS = $(man_IN_FILES:.1.in=.1)

mandir = @mandir@/pl

EXTRA_DIST = $(man_MANS) $(man_IN_FILES)

gramps.1: $(top_builddir)/config.status gramps.1.in
	cd $(top_builddir) && CONFIG_FILES=data/man/pl/$@ $(SHELL) ./config.status

CLEANFILES=$(man_MANS)
