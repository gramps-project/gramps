# copyright (C) 2000 Sun Microsystems, Inc.

SUBDIRS = src doc omf-install

EXTRA_DIST =  autogen.sh gramps.spec.in 

bin_SCRIPTS = gramps

grampsdocdir = $(datadir)/doc/gramps-$(VERSION)
scrollkeeper_localstate_dir = $(localstatedir)/lib/scrollkeeper

gramps: gramps.sh
	cp gramps.sh gramps

dist-hook: gramps.spec
	cp gramps.spec $(distdir)

# Build/rebuild the catalog
install-data-hook:
	rm -rf $(DESTDIR)$(scrollkeeper_localstate_dir)
	$(mkinstalldirs) $(DESTDIR)$(scrollkeeper_localstate_dir)
	$(mkinstalldirs) $(DESTDIR)$(localstatedir)/log
	scrollkeeper-rebuilddb -p $(DESTDIR)$(scrollkeeper_localstate_dir)

# Remove generated files
uninstall-local:
	-rm -rf $(DESTDIR)$(gramps_localstate_dir)
	-rm -f $(DESTDIR)$(localstatedir)/log/gramps.log
	-rm -f $(DESTDIR)$(localstatedir)/log/gramps.log.1

