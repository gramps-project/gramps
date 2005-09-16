SUBDIRS = src doc example

EXTRA_DIST = autogen.sh gramps.spec.in gramps.spec COPYING-DOCS FAQ COPYING

bin_SCRIPTS = gramps

dist_pkgdata_DATA = COPYING

distuninstallcheck_listfiles = find . -type -f -print | grep -E -v '/(globs|magic|XMLnamespaces)'


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

install:
	@echo "############################################################"
	@echo "This development version is currently broken and not usable."
	@echo "Use CVS branch 'gramps20' to get the current stable version."
	@echo "############################################################"
