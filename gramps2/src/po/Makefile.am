# This is the src/po level Makefile configuration
EXTRA_DIST = $(POFILES) template.po
CLEANFILES = $(MOFILES)

all-local: $(MOFILES)

install-data-local: 
	for lang in $(LANGUAGES); do \
	   $(INSTALL) -d $(DESTDIR)$(prefix)/share/locale/$$lang; \
	   $(INSTALL) -d $(DESTDIR)$(prefix)/share/locale/$$lang/LC_MESSAGES; \
	   $(INSTALL_DATA) $$lang.mo $(DESTDIR)$(prefix)/share/locale/$$lang/LC_MESSAGES/$(PACKAGE).mo; \
	done	

uninstall-local:
	for lang in $(LANGUAGES); do \
	   rm -f $(DESTDIR)$(prefix)/share/locale/$$lang/LC_MESSAGES/gramps.mo; \
	done


SUFFIXES = .po .mo

.po.mo:
	$(MSGCONV) --to-code=UTF-8 $< -o temp.po
	$(MSGFMT) temp.po -o $@
	rm temp.po

