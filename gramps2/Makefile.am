SUBDIRS = src doc example

EXTRA_DIST = autogen.sh gramps.spec.in gramps.spec COPYING-DOCS FAQ

bin_SCRIPTS = gramps
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
