# copyright (C) 2000 Sun Microsystems, Inc.

SUBDIRS = src doc omf-install example

EXTRA_DIST = autogen.sh gramps.spec.in COPYING-DOCS

bin_SCRIPTS = gramps

gramps: gramps.sh
	cp gramps.sh gramps

dist-hook: gramps.spec
	cp gramps.spec $(distdir)

# Build/rebuild the catalog
install-data-hook:
	$(mkinstalldirs) $(DESTDIR)$(localstatedir)/log

# Remove generated files
uninstall-local:
	-rm -rf $(DESTDIR)$(gramps_localstate_dir)
	-rm -f $(DESTDIR)$(localstatedir)/log/gramps.log
	-rm -f $(DESTDIR)$(localstatedir)/log/gramps.log.1

