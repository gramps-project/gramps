# Process this file with automake to produce Makefile.in

SUBDIRS = C fr

topdocdir=$(datadir)/@PACKAGE@/gnome/help/@PACKAGE@

install-data-local:
	cd $(DESTDIR)$(topdocdir); rm -rf gramps; ln -s . gramps

uninstall-local:
	-rm $(DESTDIR)$(topdocdir)/gramps
