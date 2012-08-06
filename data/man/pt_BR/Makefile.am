# This is the data/pt_BR level Makefile for Gramps
# $Id: Makefile.am 16377 2011-01-13 18:32:42Z matlas $

man_IN_FILES = gramps.1.in
man_MANS = $(man_IN_FILES:.1.in=.1)

mandir = @mandir@/pt_BR

EXTRA_DIST = $(man_MANS) $(man_IN_FILES)

gramps.1: $(top_builddir)/config.status gramps.1.in
	cd $(top_builddir) && CONFIG_FILES=data/man/pt_BR/$@ $(SHELL) ./config.status

CLEANFILES=$(man_MANS)
