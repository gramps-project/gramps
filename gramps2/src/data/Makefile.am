# This is the src/data level Makefile
SUBDIRS = templates
pkgdatadir = $(datadir)/@PACKAGE@/data

pkgdata_DATA = gedcom.xml \
	       papersize.xml \
	       tips.xml \
	       gnome-mime-application-x-gramps.png \
	       gramps.svg

EXTRA_DIST = $(pkgdata_DATA)

install-data-local:
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/pixmaps
	$(INSTALL_DATA) gramps.png $(DESTDIR)$(prefix)/share/pixmaps
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/gnome/apps/Applications
	$(INSTALL_DATA) gramps.desktop $(DESTDIR)$(prefix)/share/gnome/apps/Applications
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/
	$(INSTALL_DATA) gnome-mime-application-x-gramps.png $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/mime/packages
	$(INSTALL_DATA) gramps.xml $(DESTDIR)$(prefix)/share/mime/packages
	update-mime-database $(DESTDIR)$(prefix)/share/mime

uninstall-local:
	-rm $(DESTDIR)$(prefix)/share/pixmaps/gramps.png
	-rm $(DESTDIR)$(prefix)/share/gnome/apps/Applications/gramps.desktop
	-rm $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/gnome-mime-application-x-gramps.png

