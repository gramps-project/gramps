# This is the src/data level Makefile
SUBDIRS = templates
pkgdatadir = $(datadir)/@PACKAGE@/data

dist_pkgdata_DATA = \
	gedcom.xml \
	papersize.xml \
	tips.xml \
	gnome-mime-application-x-gramps.png \
	gnome-mime-application-x-gedcom.png \
	gnome-mime-application-x-gramps-package.png \
	gramps.applications \
	gramps.desktop \
	gramps.svg \
	gramps.keys \
	gramps.mime

EXTRA_DIST = $(dist_pkgdata_DATA)

install-schemas:
	$(INSTALL_DATA) gramps.schemas $(DESTDIR)/etc/gconf/schemas
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		gconftool-2 --makefile-install-rule gramps.schemas
	pkill -HUP gconfd

install-data-local:    install-schemas
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/gnome/apps/Applications
	$(INSTALL_DATA) gramps.desktop $(DESTDIR)$(prefix)/share/applications
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/
	$(INSTALL_DATA) gnome-mime-application-x-*.png $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/application-registry
	$(INSTALL_DATA) gramps.applications $(DESTDIR)$(prefix)/share/application-registry
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/mime/packages
	$(INSTALL_DATA) gramps.xml $(DESTDIR)$(prefix)/share/mime/packages
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/mime-info
	$(INSTALL_DATA) gramps.keys gramps.mime $(DESTDIR)$(prefix)/share/mime-info
	update-mime-database $(DESTDIR)$(prefix)/share/mime

uninstall-local:
	-rm $(DESTDIR)$(prefix)/share/gnome/apps/Applications/gramps.desktop
	-rm $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/gnome-mime-application-x-*.png
	-rm $(DESTDIR)$(prefix)/share/mime-info/gramps.keys
	-rm $(DESTDIR)$(prefix)/share/mime-info/gramps.mime
	-rm $(DESTDIR)$(prefix)/share/application-registry/gramps.applications
	-rm $(DESTDIR)$(prefix)/share/mime/packages/gramps.xml
	-rm $(DESTDIR)/etc/gconf/schemas/gramps.schemas
	update-mime-database $(DESTDIR)$(prefix)/share/mime
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		gconftool-2 --makefile-uninstall-rule gramps.schemas
