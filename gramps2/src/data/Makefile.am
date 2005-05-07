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

# Conditionally enable/disable gconf schemas or mime types,
# or disable both in a packager mode
GCONF_SCHEMAS_INSTALLATION =
GCONF_SCHEMAS_UNINSTALLATION = 
SHARED_MIME_INSTALLATION =
SHARED_MIME_UNINSTALLATION =

if !PACKAGER_MODE
if GCONF_SCHEMAS_INSTALL
GCONF_SCHEMAS_INSTALLATION += \
	$(INSTALL) -d $(DESTDIR)$(GCONF_SCHEMA_FILE_DIR) ;\
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.schemas $(DESTDIR)$(GCONF_SCHEMA_FILE_DIR) ;\
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		gconftool-2 --makefile-install-rule $(top_srcdir)/src/data/gramps.schemas ;\
	pkill gconfd ; echo Restarting gconfd

GCONF_SCHEMAS_UNINSTALLATION += \
	rm $(DESTDIR)$(GCONF_SCHEMA_FILE_DIR)/gramps.schemas ;\
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		gconftool-2 --makefile-uninstall-rule $(top_srcdir)/src/data/gramps.schemas
endif
if SHARED_MIME_INSTALL
SHARED_MIME_INSTALLATION += \
	$(INSTALL) -d $(DESTDIR)$(SHARED_MIME_DIR)/packages ;\
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.xml $(DESTDIR)$(SHARED_MIME_DIR)/packages ;\
	update-mime-database $(DESTDIR)$(SHARED_MIME_DIR)
SHARED_MIME_UNINSTALLATION += \
	rm $(DESTDIR)$(SHARED_MIME_DIR)/packages/gramps.xml ;\
	update-mime-database $(DESTDIR)$(SHARED_MIME_DIR)
endif
endif

install-data-local:
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/applications
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.desktop $(DESTDIR)$(prefix)/share/applications
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/
	$(INSTALL_DATA) $(top_srcdir)/src/data/gnome-mime-application-x-*.png $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/application-registry
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.applications $(DESTDIR)$(prefix)/share/application-registry
	$(INSTALL) -d $(DESTDIR)$(prefix)/share/mime-info
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.keys $(DESTDIR)$(prefix)/share/mime-info
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.mime $(DESTDIR)$(prefix)/share/mime-info
	$(SHARED_MIME_INSTALLATION)
	$(GCONF_SCHEMAS_INSTALLATION)

uninstall-local:
	-rm $(DESTDIR)$(prefix)/share/applications/gramps.desktop
	-rm $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/gnome-mime-application-x-*.png
	-rm $(DESTDIR)$(prefix)/share/mime-info/gramps.keys
	-rm $(DESTDIR)$(prefix)/share/mime-info/gramps.mime
	-rm $(DESTDIR)$(prefix)/share/application-registry/gramps.applications
	$(SHARED_MIME_UNINSTALLATION)
	$(GCONF_SCHEMAS_UNINSTALLATION)
