# This is the src/data level Makefile
SUBDIRS = templates
pkgdatadir = $(datadir)/@PACKAGE@/data

dist_pkgdata_DATA = \
	gedcom.xml \
	papersize.xml \
	tips.xml

EXTRA_DIST = \
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
	$(INSTALL) -d $(DESTDIR)$(GCONF_SCHEMA_FILE_DIR)
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.schemas $(DESTDIR)$(GCONF_SCHEMA_FILE_DIR)
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
	$(INSTALL) -d $(DESTDIR)$(SHARED_MIME_DIR)/packages
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.xml $(DESTDIR)$(SHARED_MIME_DIR)/packages
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/mime-info
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.keys $(DESTDIR)$(prefix)/share/mime-info
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.mime $(DESTDIR)$(prefix)/share/mime-info
	update-mime-database $(DESTDIR)$(SHARED_MIME_DIR)

uninstall-local:
	-rm $(DESTDIR)$(prefix)/share/applications/gramps.desktop
	-rm $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/gnome-mime-application-x-*.png
	-rm $(DESTDIR)$(prefix)/share/mime-info/gramps.keys
	-rm $(DESTDIR)$(prefix)/share/mime-info/gramps.mime
	-rm $(DESTDIR)$(prefix)/share/application-registry/gramps.applications
	-rm $(DESTDIR)$(SHARED_MIME_DIR)/packages/gramps.xml
	-rm $(DESTDIR)$(GCONF_SCHEMA_FILE_DIR)/gramps.schemas
	update-mime-database $(DESTDIR)$(SHARED_MIME_DIR)
	-GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		gconftool-2 --makefile-uninstall-rule $(top_srcdir)/src/data/gramps.schemas
