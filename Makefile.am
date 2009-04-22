# This is the top level Makefile for Gramps
# $Id$

SUBDIRS = m4 po src data example

EXTRA_DIST = \
	config.rpath autogen.sh \
	FAQ COPYING \
	intltool-extract.in intltool-merge.in intltool-update.in

bin_SCRIPTS = gramps

dist_pkgdata_DATA = COPYING

distuninstallcheck_listfiles = find . -type -f -print | grep -E -v '/(globs|magic|XMLnamespaces)'

DISTCLEANFILES = intltool-extract intltool-merge intltool-update \
	gnome-doc-utils.make

gramps: gramps.sh
	cp gramps.sh gramps

.PHONY: pycheck trans

pycheck:
	(cd src; make pycheck) 
trans:
	(cd src; make trans) 

distuninstallcheck:
	@:

CLEANFILES = gramps

ACLOCAL_AMFLAGS = -I m4
