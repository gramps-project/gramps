omf_dest_dir=$(datadir)/omf/gramps

install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(omf_dest_dir)
	-for file in $(srcdir)/*.omf; do \
		$(INSTALL_DATA) $(srcdir)/$$file $(DESTDIR)$(omf_dest_dir); \
	done
	-scrollkeeper-update -p $(localstatedir)/scrollkeeper

uninstall-local:
	-for file in $(srcdir)/*.omf; do \
		basefile=`basename $$file`; \
		rm -f $(omf_dest_dir)/$$basefile; \
        done
	-scrollkeeper-update -p $(localstatedir)/scrollkeeper
