# This is the src/data level Makefile
SUBDIRS = templates
pkgdatadir = $(datadir)/@PACKAGE@/data

dist_pkgdata_DATA = \
	gedcom.xml \
	papersize.xml \
	tips.xml

dist_data_DATA = \
	gramps.desktop \
	gnome-mime-application-x-gramps.png \
	gnome-mime-application-x-gedcom.png \
	gnome-mime-application-x-gramps-package.png \
	gnome-mime-application-x-gramps-xml.png \
	gnome-mime-application-x-geneweb.png \
	gramps.svg \
	gramps.xml \
	gramps.applications \
	gramps.keys \
	gramps.mime \
	gramps.schemas

install-schemas:
	$(INSTALL) -d $(DESTDIR)$(sysconfdir)/gconf/schemas
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.schemas $(DESTDIR)$(sysconfdir)/gconf/schemas
	-GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		gconftool-2 --makefile-install-rule $(top_srcdir)/src/data/gramps.schemas
	-pkill gconfd

install-data-local:    install-schemas
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/applications
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.desktop $(DESTDIR)$(prefix)/share/applications
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/
	$(INSTALL_DATA) $(top_srcdir)/src/data/gnome-mime-application-x-*.png $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/application-registry
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.applications $(DESTDIR)$(prefix)/share/application-registry
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/mime/packages
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.xml $(DESTDIR)$(prefix)/share/mime/packages
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/mime-info
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.keys $(DESTDIR)$(prefix)/share/mime-info
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.mime $(DESTDIR)$(prefix)/share/mime-info
	update-mime-database $(DESTDIR)$(prefix)/share/mime

uninstall-local:
	-rm $(DESTDIR)$(prefix)/share/applications/gramps.desktop
	-rm $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/gnome-mime-application-x-*.png
	-rm $(DESTDIR)$(prefix)/share/mime-info/gramps.keys
	-rm $(DESTDIR)$(prefix)/share/mime-info/gramps.mime
	-rm $(DESTDIR)$(prefix)/share/application-registry/gramps.applications
	-rm $(DESTDIR)$(prefix)/share/mime/packages/gramps.xml
	-rm $(DESTDIR)$(sysconfdir)/gconf/schemas/gramps.schemas
	update-mime-database $(DESTDIR)$(prefix)/share/mime
	-GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		gconftool-2 --makefile-uninstall-rule $(top_srcdir)/src/data/gramps.schemas
