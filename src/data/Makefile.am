# This is the src/data level Makefile
SUBDIRS = templates
pkgdatadir = $(datadir)/@PACKAGE@/data

pkgdata_DATA = gedcom.xml \
	       papersize.xml \
	       tips.xml \
	       gnome-mime-application-x-gramps.png \
	       gramps.applications \
	       gramps.svg \
	       gramps.keys \
               gramps.mime

EXTRA_DIST = $(pkgdata_DATA)

install-data-local:
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/pixmaps
	$(INSTALL_DATA) gramps.png $(DESTDIR)$(prefix)/share/pixmaps
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/gnome/apps/Applications
	$(INSTALL_DATA) gramps.desktop $(DESTDIR)$(prefix)/share/applications
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/
	$(INSTALL_DATA) gnome-mime-application-x-gramps.png $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/application-registry
	$(INSTALL_DATA) gramps.applications $(DESTDIR)$(prefix)/share/application-registry
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/mime/packages
	$(INSTALL_DATA) gramps.xml $(DESTDIR)$(prefix)/share/mime/packages
	update-mime-database $(DESTDIR)$(prefix)/share/mime
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/mime-info
	$(INSTALL_DATA) gramps.keys gramps.mime $(DESTDIR)$(prefix)/share/mime-info

uninstall-local:
	-rm $(DESTDIR)$(prefix)/share/pixmaps/gramps.png
	-rm $(DESTDIR)$(prefix)/share/gnome/apps/Applications/gramps.desktop
	-rm $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/gnome-mime-application-x-gramps.png
	-rm $(DESTDIR)$(prefix)/share/mime-info/gramps.keys
	-rm $(DESTDIR)$(prefix)/share/mime-info/gramps.mime
	-rm $(DESTDIR)$(prefix)/share/mime/packages/gramps.xml

