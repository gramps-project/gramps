#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import os
import tempfile
import string

from TextDoc import *
from latin_utf8 import latin_to_utf8
import const
import Plugins
import intl
import ImgManip

_ = intl.gettext

try:
    from codecs import *
except:
    def EncodedFile(a,b,c):
        return a

class OpenOfficeDoc(TextDoc):

    def __init__(self,styles,type,template,orientation):
        TextDoc.__init__(self,styles,type,template,orientation)
        self.f = None
        self.filename = None
        self.level = 0
        self.time = "0000-00-00T00:00:00"
        self.new_page = 0

    def open(self,filename):
        import time

        t = time.localtime(time.time())
        self.time = "%04d-%02d-%02dT%02d:%02d:%02d" % \
                    (t[0],t[1],t[2],t[3],t[4],t[5])

        if filename[-4:] != ".sxw":
            self.filename = filename + ".sxw"
        else:
            self.filename = filename
            
        tempfile.tempdir = "/tmp"
        self.tempdir = tempfile.mktemp()
        os.mkdir(self.tempdir,0700)
        os.mkdir(self.tempdir + os.sep + "Pictures")
        os.mkdir(self.tempdir + os.sep + "META-INF")
            
        fname = self.tempdir + os.sep + "content.xml"
        self.f = EncodedFile(open(fname,"wb"),'latin-1','utf-8')

        self.f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.f.write('<office:document-content ')
        self.f.write('xmlns:office="http://openoffice.org/2000/office" ')
        self.f.write('xmlns:style="http://openoffice.org/2000/style" ')
        self.f.write('xmlns:text="http://openoffice.org/2000/text" ')
        self.f.write('xmlns:table="http://openoffice.org/2000/table" ')
        self.f.write('xmlns:draw="http://openoffice.org/2000/drawing" ')
        self.f.write('xmlns:fo="http://www.w3.org/1999/XSL/Format" ')
        self.f.write('xmlns:xlink="http://www.w3.org/1999/xlink" ')
        self.f.write('xmlns:number="http://openoffice.org/2000/datastyle" ')
        self.f.write('xmlns:svg="http://www.w3.org/2000/svg" ')
        self.f.write('xmlns:chart="http://openoffice.org/2000/chart" ')
        self.f.write('xmlns:dr3d="http://openoffice.org/2000/dr3d" ')
        self.f.write('xmlns:math="http://www.w3.org/1998/Math/MathML" ')
        self.f.write('xmlns:form="http://openoffice.org/2000/form" ')
        self.f.write('xmlns:script="http://openoffice.org/2000/script" ')
        self.f.write('office:class="text" office:version="0.9">\n')
        self.f.write('<office:script/>\n')
        self.f.write('<office:font-decls>\n')
        self.f.write('<style:font-decl style:name="Times New Roman" ')
        self.f.write('fo:font-family="&apos;Times New Roman&apos;" ')
        self.f.write('style:font-family-generic="roman" ')
        self.f.write('style:font-pitch="variable"/>\n')
        self.f.write('<style:font-decl style:name="Arial" ')
        self.f.write('fo:font-family="Arial" ')
        self.f.write('style:font-family-generic="swiss" ')
        self.f.write('style:font-pitch="variable"/>\n')
        self.f.write('</office:font-decls>\n')
        self.f.write('<office:automatic-styles>\n')
        for style_name in self.style_list.keys():
	    style = self.style_list[style_name]
            self.f.write('<style:style style:name="NL')
            self.f.write(style_name)
            self.f.write('" style:family="paragraph" ')
            self.f.write('style:parent-style-name="')
            self.f.write(style_name)
            self.f.write('">\n<style:properties fo:break-before="page"/>\n')
            self.f.write('</style:style>\n')
	for style_name in self.table_styles.keys():
	    style = self.table_styles[style_name]
            self.f.write('<style:style style:name="' + style_name + '" ')
	    self.f.write('style:family="table">\n')
            table_width = float(self.get_usable_width())
            table_width_str = "%.4f" % table_width
	    self.f.write('<style:properties style:width="%scm" '%table_width_str)
            self.f.write('/>\n')
            self.f.write('</style:style>\n')
	    for col in range(0,style.get_columns()):
	        self.f.write('<style:style style:name="')
		self.f.write(style_name + '.' + str(chr(ord('A')+col)) +'" ')
		self.f.write('style:family="table-column">')
                width = table_width * float(style.get_column_width(col)/100.0)
                width_str = "%.4f" % width
		self.f.write('<style:properties ')
                self.f.write('style:column-width="%scm"/>' % width_str)
	        self.f.write('</style:style>\n')
        for cell in self.cell_styles.keys():
            cell_style = self.cell_styles[cell]
            self.f.write('<style:style style:name="')
            self.f.write(cell)
            self.f.write('" style:family="table-cell">\n')
            self.f.write('<style:properties')
            self.f.write(' fo:padding="%.3fcm"' % cell_style.get_padding())
            if cell_style.get_top_border():
                self.f.write(' fo:border-top="0.002cm solid #000000"')
            else:
                self.f.write(' fo:border-top="none"')
            if cell_style.get_bottom_border():
                self.f.write(' fo:border-bottom="0.002cm solid #000000"')
            else:
                self.f.write(' fo:border-bottom="none"')
            if cell_style.get_left_border():
                self.f.write(' fo:border-left="0.002cm solid #000000"')
            else:
                self.f.write(' fo:border-left="none"')
            if cell_style.get_right_border():
                self.f.write(' fo:border-right="0.002cm solid #000000"')
            else:
                self.f.write(' fo:border-right="none"')
            self.f.write('/>\n')
            self.f.write('</style:style>\n')
            
        self.f.write('<style:style style:name="Tbold" style:family="text">\n')
        self.f.write('<style:properties fo:font-weight="bold"/>\n')
        self.f.write('</style:style>\n')

        #Begin photo style
        self.f.write('<style:style style:name="Left" style:family="graphics"')
        self.f.write(' style:parent-name="photo">')
        self.f.write('<style:properties style:run-through="foreground"')
        self.f.write(' style:wrap="parallel"')
        self.f.write(' style:numer-wrapped-paragraphs="no-limit"')
        self.f.write(' style:wrap-contour="false" style:vertical-pos="from-top"')
        self.f.write(' style:vertical-rel="paragraph-content"')
        self.f.write(' style:horizontal-pos="left"')
        self.f.write(' style:horizontal-rel="paragraph-contnet"')
        self.f.write(' style:mirror="none" fo:clip="rect(0cm 0cm 0cm 0cm)"')
        self.f.write(' draw:luminance="0%" draw:contrast="0" draw:red="0%"')
        self.f.write(' draw:green="0%" draw:blue="0%" draw:gamma="1"')
        self.f.write(' draw:color-inversion="false" draw:transparency="-100%"')
        self.f.write(' draw:color-mode="standard"/>')
        self.f.write('</style:style>\n')

        self.f.write('<style:style style:name="Right" style:family="graphics"')
        self.f.write(' style:parent-name="photo">')
        self.f.write('<style:properties style:run-through="foreground"')
        self.f.write(' style:wrap="parallel"')
        self.f.write(' style:numer-wrapped-paragraphs="no-limit"')
        self.f.write(' style:wrap-contour="false" style:vertical-pos="from-top"')
        self.f.write(' style:vertical-rel="paragraph-content"')
        self.f.write(' style:horizontal-pos="right"')
        self.f.write(' style:horizontal-rel="paragraph-contnet"')
        self.f.write(' style:mirror="none" fo:clip="rect(0cm 0cm 0cm 0cm)"')
        self.f.write(' draw:luminance="0%" draw:contrast="0" draw:red="0%"')
        self.f.write(' draw:green="0%" draw:blue="0%" draw:gamma="1"')
        self.f.write(' draw:color-inversion="false" draw:transparency="-100%"')
        self.f.write(' draw:color-mode="standard"/>')
        self.f.write('</style:style>\n')

        self.f.write('<style:style style:name="Single" style:family="graphics"')
        self.f.write(' style:parent-name="Graphics">')
        self.f.write('<style:properties style:vertical-pos="from-top"')
        self.f.write(' style:mirror="none" fo:clip="rect(0cm 0cm 0cm 0cm)"')
        self.f.write(' draw:luminance="0%" draw:contrast="0" draw:red="0%"')
        self.f.write(' draw:green="0%" draw:blue="0%" draw:gamma="1"')
        self.f.write(' draw:color-inversion="false" draw:transparency="-100%"')
        self.f.write(' draw:color-mode="standard"/>')
        self.f.write('</style:style>\n')

        self.f.write('<style:style style:name="Row" style:family="graphics"')
        self.f.write(' style:parent-name="Graphics">')
        self.f.write('<style:properties style:vertical-pos="from-top"')
        self.f.write(' style:vertical-rel="paragraph"')
        self.f.write(' style:horizontal-pos="from-left"')
        self.f.write(' style:horizontal-rel="paragraph"')
        self.f.write(' style:mirror="none" fo:clip="rect(0cm 0cm 0cm 0cm)"')
        self.f.write(' draw:luminance="0%" draw:contrast="0" draw:red="0%"')
        self.f.write(' draw:green="0%" draw:blue="0%" draw:gamma="1"')
        self.f.write(' draw:color-inversion="false" draw:transparency="-100%"')
        self.f.write(' draw:color-mode="standard"/>')
        self.f.write('</style:style>\n')

        #end of Photo style edits

        self.f.write('</office:automatic-styles>\n')
        self.f.write('<office:body>\n')

    def close(self):
        self.f.write('</office:body>\n')
        self.f.write('</office:document-content>\n')
        self.f.close()
        self._write_styles_file()
        self._write_manifest()
        self._write_meta_file()
        self._write_photos()
        self._write_zip()

    def add_photo(self,name,pos,x_cm,y_cm):

        image = ImgManip.ImgManip(name)
        (x,y) = image.size()
        ratio = float(x_cm)*float(y)/(float(y_cm)*float(x))

        if ratio < 1:
            act_width = x_cm
            act_height = y_cm*ratio
        else:
            act_height = y_cm
            act_width = x_cm/ratio

        self.photo_list.append((name,act_width,act_height))

        base = os.path.basename(name)
        tag = string.replace(base,'.','_')
        
        if pos == "left":
            self.f.write('<draw:image draw:style-name="Left" ')
        elif pos == "right":
            self.f.write('<draw:image draw:style-name="Right" ')
        elif pos == "single":
            self.f.write('<draw:image draw:style-name="Single" ')
        else:
            self.f.write('<draw:image draw:style-name="Row" ')

        self.f.write('draw:name="')
        self.f.write(tag)
        self.f.write('" text:anchor-type="paragraph" ')
        self.f.write('svg:width="%.3fcm" ' % act_width)
        self.f.write('svg:height="%.3fcm" ' % act_height)
        self.f.write('draw:z-index="0" ')
        self.f.write('xlink:href="#Pictures/')
        self.f.write(base)
        self.f.write('" xlink:type="simple" xlink:show="embed" ')
        self.f.write('xlink:actuate="onLoad"/>\n')

    def start_table(self,name,style_name):
        self.f.write('<table:table table:name="')
	self.f.write(name)
	self.f.write('" table:style-name="' + style_name + '">\n')
	table = self.table_styles[style_name]
	for col in range(0,table.get_columns()):
	    self.f.write('<table:table-column table:style-name="')
  	    self.f.write(style_name + '.' + str(chr(ord('A')+col)) +'"/>\n')

    def end_table(self):
        self.f.write('</table:table>\n')

    def start_row(self):
        self.f.write('<table:table-row>\n')

    def end_row(self):
        self.f.write('</table:table-row>\n')

    def start_cell(self,style_name,span=1):
	self.span = span
	self.f.write('<table:table-cell table:style-name="')
        self.f.write(style_name)
        self.f.write('" table:value-type="string"')
        if span > 1:
            self.f.write(' table:number-columns-spanned="' + str(span) + '">\n')
	else:	     
	    self.f.write('>\n')

    def end_cell(self):
        self.f.write('</table:table-cell>\n')
        for col in range(1,self.span):
            self.f.write('<table:covered-table-cell/>\n')

    def start_bold(self):
        self.f.write('<text:span text:style-name="Tbold">')

    def end_bold(self):
        self.f.write('</text:span>')

    def _write_zip(self):
        
        if os.path.isfile(self.filename):
            os.unlink(self.filename)

        os.system("cd '%s'; %s '%s' ." % (self.tempdir,const.zipcmd,self.filename))

        os.unlink(self.tempdir + os.sep + "META-INF" + os.sep + "manifest.xml")
        os.unlink(self.tempdir + os.sep + "content.xml")
        os.unlink(self.tempdir + os.sep + "meta.xml")
        os.unlink(self.tempdir + os.sep + "styles.xml")
        for image in self.photo_list:
            base = os.path.basename(image[0])
            os.unlink(self.tempdir + os.sep + "Pictures" + os.sep + base)
        os.rmdir(self.tempdir + os.sep + "Pictures")
        os.rmdir(self.tempdir + os.sep + "META-INF")
        os.rmdir(self.tempdir)
        
    def _write_styles_file(self):
	file = self.tempdir + os.sep + "styles.xml"

	self.f = EncodedFile(open(file,"wb"),'latin-1','utf-8')
        
        self.f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.f.write('<office:document-styles ')
        self.f.write('xmlns:office="http://openoffice.org/2000/office" ')
        self.f.write('xmlns:style="http://openoffice.org/2000/style" ')
        self.f.write('xmlns:text="http://openoffice.org/2000/text" ')
        self.f.write('xmlns:table="http://openoffice.org/2000/table" ')
        self.f.write('xmlns:draw="http://openoffice.org/2000/drawing" ')
        self.f.write('xmlns:fo="http://www.w3.org/1999/XSL/Format" ')
        self.f.write('xmlns:xlink="http://www.w3.org/1999/xlink" ')
        self.f.write('xmlns:number="http://openoffice.org/2000/datastyle" ')
        self.f.write('xmlns:svg="http://www.w3.org/2000/svg" ')
        self.f.write('xmlns:chart="http://openoffice.org/2000/chart" ')
        self.f.write('xmlns:dr3d="http://openoffice.org/2000/dr3d" ')
        self.f.write('xmlns:math="http://www.w3.org/1998/Math/MathML" ')
        self.f.write('xmlns:form="http://openoffice.org/2000/form" ')
        self.f.write('xmlns:script="http://openoffice.org/2000/script" ')
        self.f.write('office:class="text" office:version="0.9">\n')
        self.f.write('<office:font-decls>\n')
        self.f.write('<style:font-decl style:name="Times New Roman" ')
        self.f.write('fo:font-family="&apos;Times New Roman&apos;" ')
        self.f.write('style:font-family-generic="roman" ')
        self.f.write('style:font-pitch="variable"/>\n')
        self.f.write('<style:font-decl style:name="Arial" ')
        self.f.write('fo:font-family="Arial" ')
        self.f.write('style:font-family-generic="swiss" ')
        self.f.write('style:font-pitch="variable"/>\n')
        self.f.write('</office:font-decls>\n')
        self.f.write('<office:styles>\n')
        self.f.write('<style:default-style style:family="paragraph">\n')
        self.f.write('<style:properties style:font-name="Times New Roman" ')
        self.f.write('style:font-pitch-asian="fixed" ')
        self.f.write('style:font-pitch-complex="fixed" ')
        self.f.write('style:tab-stop-distance="2.205cm"/>\n')
        self.f.write('</style:default-style>\n')
        self.f.write('<style:style style:name="Standard" ')
        self.f.write('style:family="paragraph" style:class="text"/>\n')
        self.f.write('<style:style style:name="photo" style:family="graphics">\n')
        self.f.write('<style:properties text:anchor-type="paragraph" ')
        self.f.write('svg:x="0cm" svg:y="0cm" style:wrap="none" ')
        self.f.write('style:vertical-pos="top" ')
        self.f.write('style:vertical-rel="paragraph-content" ')
        self.f.write('style:horizontal-pos="center" ')
        self.f.write('style:horizontal-rel="paragraph-content"/>\n')
        self.f.write('</style:style>\n')
        
        for key in self.style_list.keys():
            style = self.style_list[key]
            self.f.write('<style:style style:name="' + key + '" ')
            self.f.write('style:family="paragraph" ')
            self.f.write('style:parent-style-name="Standard" ')
            self.f.write('style:class="text">\n')
            self.f.write('<style:properties ')

            if style.get_padding() != 0.0:
	       self.f.write('fo:padding="%.3fcm" ' % style.get_padding())

            align = style.get_alignment()
	    if align == PARA_ALIGN_LEFT:
	       self.f.write('fo:text-align="left" ')
            elif align == PARA_ALIGN_RIGHT:
               self.f.write('fo:text-align="right" ')
            elif align == PARA_ALIGN_CENTER:
               self.f.write('fo:text-align="center" ')
               self.f.write('style:justify-single-word="false" ')
            else:
               self.f.write('fo:text-align="justify" ')
               self.f.write('style:justify-single-word="false" ')
            font = style.get_font()
            if font.get_type_face() == FONT_SANS_SERIF:
                self.f.write('style:font-name="Arial" ')
            else:
                self.f.write('style:font-name="Times New Roman" ')
            self.f.write('fo:font-size="' + str(font.get_size()) + 'pt" ')
            color = font.get_color()
	    self.f.write('fo:color="#%02x%02x%02x" ' % color)
            if font.get_bold():
                self.f.write('fo:font-weight="bold" ')
            if font.get_italic():
                self.f.write('fo:font-style="italic" ')
	    if font.get_underline():
		self.f.write('style:text-underline="single" ')
                self.f.write('style:text-underline-color="font-color" ')
            self.f.write('fo:text-indent="%.2fcm" ' % style.get_first_indent())
            self.f.write('fo:margin-right="%.2fcm" ' % style.get_right_margin())
            self.f.write('fo:margin-left="%.2fcm" ' % style.get_left_margin())
            self.f.write('fo:margin-top="0cm" ')
            self.f.write('fo:margin-bottom="0.212cm"')
            self.f.write('/>\n')
            self.f.write('</style:style>\n')

	# Current no leading number format for headers

	self.f.write('<text:outline-style>\n')
	self.f.write('<text:outline-level-style text:level="1" style:num-format=""/>\n')
	self.f.write('<text:outline-level-style text:level="2" style:num-format=""/>\n')
	self.f.write('<text:outline-level-style text:level="3" style:num-format=""/>\n')
	self.f.write('<text:outline-level-style text:level="4" style:num-format=""/>\n')
	self.f.write('<text:outline-level-style text:level="5" style:num-format=""/>\n')
	self.f.write('<text:outline-level-style text:level="6" style:num-format=""/>\n')
	self.f.write('<text:outline-level-style text:level="7" style:num-format=""/>\n')
	self.f.write('<text:outline-level-style text:level="8" style:num-format=""/>\n')
	self.f.write('<text:outline-level-style text:level="9" style:num-format=""/>\n')
	self.f.write('<text:outline-level-style text:level="10" style:num-format=""/>\n')
	self.f.write('</text:outline-style>\n')
            
        self.f.write('</office:styles>\n')
        self.f.write('<office:automatic-styles>\n')
        self.f.write('<style:page-master style:name="pm1">\n')
        self.f.write('<style:properties fo:page-width="%.3fcm" ' % self.width)
        self.f.write('fo:page-height="%.3fcm" ' % self.height)
        self.f.write('style:num-format="1" ')
        if self.orientation == PAPER_PORTRAIT:
            self.f.write('style:print-orientation="portrait" ')
        else:
            self.f.write('style:print-orientation="landscape" ')
        self.f.write('fo:margin-top="%.2fcm" ' % self.tmargin)
        self.f.write('fo:margin-bottom="%.2fcm" ' % self.bmargin)
        self.f.write('fo:margin-left="%.2fcm" ' % self.lmargin)
        self.f.write('fo:margin-right="%.2fcm" ' % self.rmargin)
        self.f.write('style:footnote-max-height="0cm">\n')
        self.f.write('<style:footnote-sep style:width="0.018cm" ')
        self.f.write('style:distance-before-sep="0.101cm" ')
        self.f.write('style:distance-after-sep="0.101cm" ')
        self.f.write('style:adjustment="left" style:rel-width="25%" ')
        self.f.write('style:color="#000000"/>\n')
        self.f.write('</style:properties>\n')
        self.f.write('<style:header-style/>\n')
        self.f.write('<style:footer-style/>\n')
        self.f.write('</style:page-master>\n')
        self.f.write('</office:automatic-styles>\n')
        self.f.write('<office:master-styles>\n')
        self.f.write('<style:master-page style:name="Standard" ')
        self.f.write('style:page-master-name="pm1"/>\n')
        self.f.write('</office:master-styles>\n')
        self.f.write('</office:document-styles>\n')
	self.f.close()

    def page_break(self):
        self.new_page = 1
        
    def start_paragraph(self,style_name,leader=None):
	style = self.style_list[style_name]
	self.level = style.get_header_level()
        if self.new_page == 1:
            self.new_page = 0
            name = "NL%s" % style_name
        else:
            name = style_name
	if self.level == 0:
	    self.f.write('<text:p text:style-name="%s">' % name)
	else:
	    self.f.write('<text:h text:style-name="')
            self.f.write(name)
	    self.f.write('" text:level="' + str(self.level) + '">')
        if leader != None:
            self.f.write(latin_to_utf8(leader))
            self.f.write('<text:tab-stop/>')

    def end_paragraph(self):
        if self.level == 0:
            self.f.write('</text:p>\n')
        else:
            self.f.write('</text:h>\n')

    def write_text(self,text):
        text = string.replace(text,'&','&amp;');       # Must be first
        text = string.replace(text,'<','&lt;');
        text = string.replace(text,'>','&gt;');
        text = string.replace(text,'\n','<text:line-break/>')
	self.f.write(latin_to_utf8(text))

    def _write_photos(self):
        import shutil

        for file_tuple in self.photo_list:
            file = file_tuple[0]
            base = os.path.basename(file)
            image_name = self.tempdir + os.sep + "Pictures" + os.sep + base

            try:
                shutil.copy(file,image_name)
            except IOError,msg:
                import gnome.ui
                gnome.ui.GnomeErrorDialog(_("Error copying %s") + "\n" + msg)

    def _write_manifest(self):
	file = self.tempdir + os.sep + "META-INF" + os.sep + "manifest.xml"
	self.f = EncodedFile(open(file,"wb"),'latin-1','utf-8')
	self.f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	self.f.write('<manifest:manifest ')
        self.f.write('xmlns:manifest="http://openoffice.org/2001/manifest">')
	self.f.write('<manifest:file-entry ')
        self.f.write('manifest:media-type="application/vnd.sun.xml.writer" ')
	self.f.write('manifest:full-path="/"/>')
        for image in self.photo_list:
            i = image[0]
            base = os.path.basename(i)
            self.f.write('<manifest:file-entry manifest:media-type="" ')
            self.f.write('manifest:full-path="Pictures/')
            self.f.write(base)
            self.f.write('"/>')
        self.f.write('<manifest:file-entry manifest:media-type="" ')
	self.f.write('manifest:full-path="Pictures/"/>')
	self.f.write('<manifest:file-entry manifest:media-type="text/xml" ')
	self.f.write('manifest:full-path="content.xml"/>')
	self.f.write('<manifest:file-entry manifest:media-type="text/xml" ')
	self.f.write('manifest:full-path="styles.xml"/>')
	self.f.write('<manifest:file-entry manifest:media-type="text/xml" ')
	self.f.write('manifest:full-path="meta.xml"/>')
	self.f.write('</manifest:manifest>\n')
	self.f.close()

    def _write_meta_file(self):
	file = self.tempdir + os.sep + "meta.xml"
        name = latin_to_utf8(self.name)
	self.f = EncodedFile(open(file,"wb"),'latin-1','utf-8')
	self.f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	self.f.write('<office:document-meta ')
	self.f.write('xmlns:office="http://openoffice.org/2000/office" ')
	self.f.write('xmlns:xlink="http://www.w3.org/1999/xlink" ')
	self.f.write('xmlns:dc="http://purl.org/dc/elements/1.1/" ')
	self.f.write('xmlns:meta="http://openoffice.org/2000/meta" ')
	self.f.write('office:class="text" office:version="0.9">\n');
	self.f.write('<office:meta>\n')
	self.f.write('<meta:generator>')
        self.f.write(const.progName + ' ' + const.version)
        self.f.write('</meta:generator>\n')
	self.f.write('<meta:initial-creator>')
	self.f.write(name)
	self.f.write('</meta:initial-creator>\n')
	self.f.write('<meta:creation-date>')
	self.f.write(self.time)
	self.f.write('</meta:creation-date>\n')
	self.f.write('<dc:creator>')
	self.f.write(name)
	self.f.write('</dc:creator>\n')
	self.f.write('<dc:date>')
	self.f.write(self.time)
	self.f.write('</dc:date>\n')
	self.f.write('<meta:print-date>0-00-00T00:00:00</meta:print-date>\n')
	self.f.write('<dc:language>en-US</dc:language>\n')
	self.f.write('<meta:editing-cycles>1</meta:editing-cycles>\n')
	self.f.write('<meta:editing-duration>PT0S</meta:editing-duration>\n')
	self.f.write('<meta:user-defined meta:name="Info 0"/>\n')
	self.f.write('<meta:user-defined meta:name="Info 1"/>\n')
	self.f.write('<meta:user-defined meta:name="Info 2"/>\n')
	self.f.write('<meta:user-defined meta:name="Info 3"/>\n')
	self.f.write('</office:meta>\n')
	self.f.write('</office:document-meta>\n')
	self.f.close()

Plugins.register_text_doc(_("OpenOffice/StarOffice 6"),OpenOfficeDoc,1,1,1)
