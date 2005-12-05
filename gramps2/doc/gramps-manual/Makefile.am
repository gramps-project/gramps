# Process this file with automake to produce Makefile.in

SUBDIRS = C fr

topdocdir=$(datadir)/@PACKAGE@/gnome/help/@PACKAGE@

install-data-local:
	cd $(DESTDIR)$(topdocdir); ln -s . gramps

uninstall-local:
	-rm $(DESTDIR)$(topdocdir)/gramps
