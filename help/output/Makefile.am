# This is the help/output level Makefile for gramps
# $Id$

BRANCH = 2.2
HELP_LINGUAS = C fr nb sk nl

# admon images to copy
ADMON_IMAGES = note.png tip.png warning.png

# Docbook stuff
chunkxsl = /usr/share/xml/docbook/stylesheet/nwalsh/html/chunk.xsl
admonimgdir = /usr/share/xml/docbook/stylesheet/nwalsh/images/

html:
	rm -rf gramps-manual 	# Clean up the output dir
	for lang in $(HELP_LINGUAS) ; do \
	  xsltproc -o gramps-manual/$(BRANCH)/$$lang/index.html \
	    --stringparam chunker.output.encoding UTF-8 \
	    --stringparam html.stylesheet ../../gramps-help-screen.css \
	    --stringparam admon.graphics 1 \
	    --stringparam admon.graphics.path ../../images/ \
	    --stringparam navig.graphics 1 \
	    --stringparam navig.graphics.extension .png \
	    --stringparam navig.graphics.path ../../images/ \
	    $(chunkxsl) ../$$lang/gramps.xml ; \
	  mkdir gramps-manual/$(BRANCH)/$$lang/figures ; \
	  cp -R ../$$lang/figures/*.png \
		gramps-manual/$(BRANCH)/$$lang/figures/ ; \
	  echo "Done with html for $$lang" ; \
	done

	mv gramps-manual/$(BRANCH)/C gramps-manual/$(BRANCH)/en

	mkdir gramps-manual/images
	cp htmlpic/* gramps-manual/images/
	for img in $(ADMON_IMAGES) ; do \
	  cp $(admonimgdir)/$$img gramps-manual/images/ ; \
	done

	cp gramps-help-screen.css gramps-manual/

pdf:
	echo "This is a placeholder for making PDF"
