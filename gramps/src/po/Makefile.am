# This is the src/po level Makefile configuration
EXTRA_DIST = ${POFILES}
CLEANFILES = ${MOFILES}

all: ${MOFILES}

install-data-local:
	for lang in ${LANGUAGES}; do \
	   ${INSTALL} -d ${prefix}/share/locale/$$lang; \
	   ${INSTALL} -d ${prefix}/share/locale/$$lang/LC_MESSAGES; \
	   ${INSTALL_DATA} $$lang.mo ${prefix}/share/locale/$$lang/LC_MESSAGES/${PACKAGE}.mo; \
	done	
	
uninstall-local:
	for lang in ${LANGUAGES}; do \
	   rm -f ${prefix}/share/locale/$$lang/LC_MESSAGES/gramps.mo; \
	done


SUFFIXES = .po .mo

.po.mo:
	${MSGFMT} $< -o $@
