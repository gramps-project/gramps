# This is the help/output level Makefile for gramps
# $Id$

BRANCH = 2.2
HELP_LINGUAS = C fr sk nl #nb

# admon images to copy
ADMON_IMAGES = note.png tip.png warning.png

# Docbook stuff
chunkxsl = /usr/share/xml/docbook/stylesheet/nwalsh/html/chunk.xsl
admonimgdir = /usr/share/xml/docbook/stylesheet/nwalsh/images/
docbookxsl = /usr/share/xml/docbook/stylesheet/nwalsh/fo/docbook.xsl

html:
	rm -rf gramps-manual 	# Clean up the output dir
	for lang in $(HELP_LINGUAS) ; do \
		xsltproc -o gramps-manual/$(BRANCH)/$$lang/index.html \
			--stringparam chunker.output.encoding UTF-8 \
			--stringparam html.stylesheet \
				../../gramps-help-screen.css \
			--stringparam admon.graphics 1 \
			--stringparam admon.graphics.path ../../images/ \
			--stringparam navig.graphics 1 \
			--stringparam navig.graphics.extension .png \
			--stringparam navig.graphics.path ../../images/ \
			$(chunkxsl) ../$$lang/gramps.xml ; \
		mkdir gramps-manual/$(BRANCH)/$$lang/figures ; \
		cp ../$$lang/figures/*.png \
			gramps-manual/$(BRANCH)/$$lang/figures/ ; \
		echo "	Done with html for $$lang" ; \
		echo "	" ; \
	done

	mv gramps-manual/$(BRANCH)/C gramps-manual/$(BRANCH)/en

	mkdir gramps-manual/images
	cp htmlpic/* gramps-manual/images/
	for img in $(ADMON_IMAGES) ; do \
		cp $(admonimgdir)/$$img gramps-manual/images/ ; \
	done

	cp gramps-help-screen.css gramps-manual/

pdf:	fo

fo:
	rm -rf gramps-pdf 	# Clean up the output dir
	for lang in $(HELP_LINGUAS) ; do \
		if test $$lang = C ; then \
			papers="USletter A4"; \
		else \
			papers=A4 ; \
		fi ; \
		for paper in $$papers ; do \
			xsltproc  \
				--output gramps-pdf/$$lang/gramps-$$paper.fo \
				--stringparam  paper.type $$paper \
				--stringparam  double.sided 1 \
				--stringparam  admon.graphics 1 \
				--stringparam  admon.graphics.path ./admonpdf \
				--stringparam  section.autolabel 1 \
				--stringparam  section.autolabel.max.depth 3 \
				--stringparam  \
				    section.label.includes.component.label 1 \
				--stringparam  body.start.indent 0pt \
				--stringparam  fop.extensions  1 \
				$(docbookxsl) ../$$lang/gramps.xml ; \
		done ; \
	done
