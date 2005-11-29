# Process this file with automake to produce Makefile.in

SUBDIRS = C fr

topdocdir1=$(datadir)/@PACKAGE@/gnome/help/@PACKAGE@
topdocdir2=$(datadir)/@PACKAGE@/gnome/help/@PACKAGE@/@PACKAGE@

install-data-local:
	ln -s $(DESTDIR)$(topdocdir1) $(DESTDIR)$(topdocdir2)

uninstall-local:
	-rm $(DESTDIR)$(topdocdir2)
