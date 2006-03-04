# This is the src/data level Makefile
# $Id$
#
SUBDIRS = templates
pkgdatadir = $(datadir)/@PACKAGE@/data

dist_pkgdata_DATA = \
	gedcom.xml \
	somerights20.gif \
	papersize.xml \
	system_filters.xml \
	tips.xml\
	main1.css\
	main2.css\
	main3.css\
	main4.css\
	main5.css\
	main6.css\
	document.png

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
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		$(GCONFTOOL) --makefile-install-rule $(DESTDIR)$(GCONF_SCHEMA_FILE_DIR)/gramps.schemas ;\
	pkill gconfd ; echo Restarting gconfd

GCONF_SCHEMAS_UNINSTALLATION += \
	GCONF_CONFIG_SOURCE=$(GCONF_SCHEMA_CONFIG_SOURCE) \
		$(GCONFTOOL) --makefile-uninstall-rule $(DESTDIR)$(GCONF_SCHEMA_FILE_DIR)/gramps.schemas
endif
if SHARED_MIME_INSTALL
SHARED_MIME_INSTALLATION += \
	update-mime-database $(DESTDIR)$(SHARED_MIME_DIR)
SHARED_MIME_UNINSTALLATION += \
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
	$(INSTALL) -d $(DESTDIR)$(SHARED_MIME_DIR)/packages
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.xml $(DESTDIR)$(SHARED_MIME_DIR)/packages
	$(INSTALL) -d $(DESTDIR)$(GCONF_SCHEMA_FILE_DIR)
	$(INSTALL_DATA) $(top_srcdir)/src/data/gramps.schemas $(DESTDIR)$(GCONF_SCHEMA_FILE_DIR)
	$(SHARED_MIME_INSTALLATION)
	$(GCONF_SCHEMAS_INSTALLATION)

uninstall-local:
	-rm $(DESTDIR)$(prefix)/share/applications/gramps.desktop
	-rm $(DESTDIR)$(prefix)/share/icons/gnome/48x48/mimetypes/gnome-mime-application-x-*.png
	-rm $(DESTDIR)$(prefix)/share/mime-info/gramps.keys
	-rm $(DESTDIR)$(prefix)/share/mime-info/gramps.mime
	-rm $(DESTDIR)$(prefix)/share/application-registry/gramps.applications
	$(GCONF_SCHEMAS_UNINSTALLATION)
	-rm $(DESTDIR)$(GCONF_SCHEMA_FILE_DIR)/gramps.schemas
	-rm $(DESTDIR)$(SHARED_MIME_DIR)/packages/gramps.xml
	$(SHARED_MIME_UNINSTALLATION)
