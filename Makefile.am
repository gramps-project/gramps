SUBDIRS = po src doc example

EXTRA_DIST = config.rpath  autogen.sh gramps.spec.in gramps.spec COPYING-DOCS FAQ COPYING intltool-extract.in intltool-merge.in intltool-update.in

bin_SCRIPTS = gramps

dist_pkgdata_DATA = COPYING

distuninstallcheck_listfiles = find . -type -f -print | grep -E -v '/(globs|magic|XMLnamespaces)'

DISTCLEANFILES = intltool-extract intltool-merge intltool-update

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
