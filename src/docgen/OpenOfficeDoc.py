#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

# $Id$

#-------------------------------------------------------------------------
#
# Standard Python Modules 
#
#-------------------------------------------------------------------------
import os
import tempfile
import string
import zipfile
import time
from math import pi, cos, sin, fabs

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import Errors
import BaseDoc
import const
import Plugins
import ImgManip
import FontScale

#-------------------------------------------------------------------------
#
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# OpenOfficeDoc
#
#-------------------------------------------------------------------------
class OpenOfficeDoc(BaseDoc.BaseDoc):

    def __init__(self,styles,type,template,orientation=BaseDoc.PAPER_PORTRAIT):
        BaseDoc.BaseDoc.__init__(self,styles,type,template,orientation)
        self.f = None
        self.filename = None
        self.level = 0
        self.time = "0000-00-00T00:00:00"
        self.new_page = 0
        self.new_cell = 0
        self.page = 0
        self.first_page = 1

    def set_mode(self, mode):
        self.mode = mode

    def open(self,filename):
        t = time.localtime(time.time())
        self.time = "%04d-%02d-%02dT%02d:%02d:%02d" % \
                    (t[0],t[1],t[2],t[3],t[4],t[5])

        if filename[-4:] != ".sxw":
            self.filename = filename + ".sxw"
        else:
            self.filename = filename

        self.filename = os.path.normpath(os.path.abspath(filename))
            
        try:
            self.content_xml = tempfile.mktemp()
            self.f = open(self.content_xml,"wb")
        except IOError,msg:
            raise Errors.ReportError(_("Could not create %s") % self.content_xml, msg)
        except:
            raise Errors.ReportError(_("Could not create %s") % self.content_xml)

    def init(self):
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
        self.f.write('<style:font-decl style:name="Courier" fo:font-family="Courier" ')
        self.f.write('style:font-family-generic="modern" style:font-pitch="fixed"/>\n')
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
        self.f.write('<style:style style:name="docgen_page_break" style:family="paragraph">\n')
        self.f.write('<style:properties fo:break-before="page"/>\n')
        self.f.write('</style:style>\n')
        self.f.write('<style:style style:name="GSuper" style:family="text">')
        self.f.write('<style:properties style:text-position="super 58%"/>')
        self.f.write('</style:style>\n')
        self.f.write('<style:style style:name="GRAMPS-preformat" style:family="text">')
        self.f.write('<style:properties style:font-name="Courier"/>')
        self.f.write('</style:style>\n')

	for style_name in self.draw_styles.keys():
            style = self.draw_styles[style_name]
            self.f.write('<style:style style:name="%s"' % style_name)
	    self.f.write(' style:family="graphics">\n')
	    self.f.write('<style:properties ')
            self.f.write('draw:fill="solid" ')
            self.f.write('draw:fill-color="#%02x%02x%02x" ' % style.get_fill_color())

            if style.get_line_style() == BaseDoc.DASHED:
                self.f.write('draw:color="#cccccc" ')
            else:
                self.f.write('draw:color="#%02x%02x%02x" ' % style.get_color())
                
            if style.get_line_width():
                self.f.write('draw:stroke="solid" ')
            else:
                self.f.write('draw:stroke="none" ')
            self.f.write('draw:shadow="hidden" ')
            self.f.write('style:run-through="background" ')
	    self.f.write('/>\n')
  	    self.f.write('</style:style>\n')

            self.f.write('<style:style style:name="%s_shadow"' % style_name)
	    self.f.write(' style:family="graphics">\n')
	    self.f.write('<style:properties ')
            self.f.write('draw:fill="solid" ')
            self.f.write('draw:fill-color="#cccccc" ')
            self.f.write('draw:stroke="none" ')
            self.f.write('style:run-through="background" ')
	    self.f.write('/>\n')
  	    self.f.write('</style:style>\n')

        for style_name in self.style_list.keys():
	    style = self.style_list[style_name]
            self.f.write('<style:style style:name="NL%s" ' % style_name)
            self.f.write('style:family="paragraph" ')
            self.f.write('style:parent-style-name="%s">\n' % style_name)
            self.f.write('<style:properties fo:break-before="page"/>\n')
            self.f.write('</style:style>\n')

            self.f.write('<style:style style:name="X%s" ' % style_name)
            self.f.write('style:family="paragraph" ')
            self.f.write('style:parent-style-name="Standard" ')
            self.f.write('style:class="text">\n')
            self.f.write('<style:properties ')

            if style.get_padding() != 0.0:
	       self.f.write('fo:padding="%.3fcm" ' % style.get_padding())
            if style.get_header_level() > 0:
                self.f.write('fo:keep-with-next="true" ')

            align = style.get_alignment()
	    if align == BaseDoc.PARA_ALIGN_LEFT:
	       self.f.write('fo:text-align="start" ')
            elif align == BaseDoc.PARA_ALIGN_RIGHT:
               self.f.write('fo:text-align="end" ')
            elif align == BaseDoc.PARA_ALIGN_CENTER:
               self.f.write('fo:text-align="center" ')
               self.f.write('style:justify-single-word="false" ')
            else:
               self.f.write('fo:text-align="justify" ')
               self.f.write('style:justify-single-word="false" ')
            font = style.get_font()
            if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
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

            self.f.write('<style:style style:name="F%s" ' % style_name)
            self.f.write('style:family="text">\n')
            self.f.write('<style:properties ')
            align = style.get_alignment()
	    if align == BaseDoc.PARA_ALIGN_LEFT:
	       self.f.write('fo:text-align="start" ')
            elif align == BaseDoc.PARA_ALIGN_RIGHT:
               self.f.write('fo:text-align="end" ')
            elif align == BaseDoc.PARA_ALIGN_CENTER:
               self.f.write('fo:text-align="center" ')
            font = style.get_font()
            if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
                self.f.write('style:font-name="Arial" ')
            else:
                self.f.write('style:font-name="Times New Roman" ')
            color = font.get_color()
	    self.f.write('fo:color="#%02x%02x%02x" ' % color)
            if font.get_bold():
                self.f.write('fo:font-weight="bold" ')
            if font.get_italic():
                self.f.write('fo:font-style="italic" ')
            self.f.write('fo:font-size="%dpt"/>' % font.get_size())
            self.f.write('</style:style>\n')

	for style_name in self.table_styles.keys():
	    style = self.table_styles[style_name]
            self.f.write('<style:style style:name="%s" ' % style_name)
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
            self.f.write('<style:style style:name="%s" ' % cell)
            self.f.write('style:family="table-cell">\n')
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
        self.f.write(' style:horizontal-rel="paragraph-content"')
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
        self.f.write(' style:horizontal-rel="paragraph-content"')
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
        self._write_zip()
        if self.print_req:
            import grampslib

            apptype = 'application/vnd.sun.xml.writer'
            prog = grampslib.default_application_command(apptype)
            os.environ["FILE"] = self.filename
            os.system ('%s "$FILE" &' % prog)

    def add_photo(self,name,pos,x_cm,y_cm):

        # try to open the image. If the open fails, it probably wasn't
        # a valid image (could be a PDF, or a non-image)
        try:
            image = ImgManip.ImgManip(name)
            (x,y) = image.size()
            ratio = float(x_cm)*float(y)/(float(y_cm)*float(x))
        except:
            return
        
        if ratio < 1:
            act_width = x_cm
            act_height = y_cm*ratio
        else:
            act_height = y_cm
            act_width = x_cm/ratio

        photo_list_item = (name,act_width,act_height)
        if not photo_list_item in self.photo_list:
            self.photo_list.append(photo_list_item)

        base = os.path.basename(name)
        tag = string.replace(base,'.','_')
        
        if self.new_cell:
            self.f.write('<text:p>')
        if pos == "left":
            self.f.write('<draw:image draw:style-name="Left" ')
        elif pos == "right":
            self.f.write('<draw:image draw:style-name="Right" ')
        elif pos == "single":
            self.f.write('<draw:image draw:style-name="Single" ')
        else:
            self.f.write('<draw:image draw:style-name="Row" ')

        self.f.write('draw:name="%s" ' % tag)
        self.f.write('text:anchor-type="paragraph" ')
        self.f.write('svg:width="%.3fcm" ' % act_width)
        self.f.write('svg:height="%.3fcm" ' % act_height)
        self.f.write('draw:z-index="0" ')
        self.f.write('xlink:href="#Pictures/')
        self.f.write(base)
        self.f.write('" xlink:type="simple" xlink:show="embed" ')
        self.f.write('xlink:actuate="onLoad"/>\n')
        if self.new_cell:
            self.f.write('</text:p>\n')

    def start_table(self,name,style_name):
        self.f.write('<table:table table:name="%s" ' % name)
	self.f.write('table:style-name="%s">\n' % style_name)
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
	self.f.write('<table:table-cell table:style-name="%s" ' % style_name)
        self.f.write('table:value-type="string"')
        if span > 1:
            self.f.write(' table:number-columns-spanned="%s">\n' % span)
	else:	     
	    self.f.write('>\n')
        self.new_cell = 1

    def end_cell(self):
        self.f.write('</table:table-cell>\n')
        for col in range(1,self.span):
            self.f.write('<table:covered-table-cell/>\n')
        self.new_cell = 0

    def start_bold(self):
        self.f.write('<text:span text:style-name="Tbold">')

    def end_bold(self):
        self.f.write('</text:span>')

    def _write_zip(self):
        file = zipfile.ZipFile(self.filename,"w",zipfile.ZIP_DEFLATED)
        file.write(self.manifest_xml,str("META-INF/manifest.xml"))
        file.write(self.content_xml,str("content.xml"))
        file.write(self.meta_xml,str("meta.xml"))
        file.write(self.styles_xml,str("styles.xml"))
        
        for image in self.photo_list:
            base = os.path.basename(image[0])
            file.write(image[0], str("Pictures/%s" % base))
        file.close()

        os.unlink(self.manifest_xml)
        os.unlink(self.content_xml)
        os.unlink(self.meta_xml)
        os.unlink(self.styles_xml)
        
    def _write_styles_file(self):
        self.styles_xml = tempfile.mktemp()
        
        try:
            self.f = open(self.styles_xml,"wb")
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.styles_xml, msg)
            raise Errors.ReportError(errmsg)
        except:
            pass
            raise Errors.ReportError(_("Could not create %s") % self.styles_xml)
                                     
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
            self.f.write('<style:style style:name="%s" ' % key)
            self.f.write('style:family="paragraph" ')
            self.f.write('style:parent-style-name="Standard" ')
            self.f.write('style:class="text">\n')
            self.f.write('<style:properties ')

            if style.get_padding() != 0.0:
	       self.f.write('fo:padding="%.3fcm" ' % style.get_padding())
            if style.get_header_level() > 0:
                self.f.write('fo:keep-with-next="true" ')

            align = style.get_alignment()
	    if align == BaseDoc.PARA_ALIGN_LEFT:
	       self.f.write('fo:text-align="start" ')
            elif align == BaseDoc.PARA_ALIGN_RIGHT:
               self.f.write('fo:text-align="end" ')
            elif align == BaseDoc.PARA_ALIGN_CENTER:
               self.f.write('fo:text-align="center" ')
               self.f.write('style:justify-single-word="false" ')
            else:
               self.f.write('fo:text-align="justify" ')
               self.f.write('style:justify-single-word="false" ')
            font = style.get_font()
            if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
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
        if self.orientation == BaseDoc.PAPER_PORTRAIT:
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
	self.f.write('<draw:layer-set>\n')
	self.f.write('<draw:layer draw:name="layout" draw:locked="false" ')
	self.f.write('draw:printable="true" draw:visible="true"/>\n')
	self.f.write('<draw:layer draw:name="background" draw:locked="false" ')
	self.f.write('draw:printable="true" draw:visible="true"/>\n')
	self.f.write('<draw:layer draw:name="backgroundobjects" ')
	self.f.write('draw:locked="false" draw:printable="true" draw:visible="true"/>\n')
	self.f.write('<draw:layer draw:name="controls" draw:locked="false" ')
	self.f.write('draw:printable="true" draw:visible="true"/>\n')
	self.f.write('<draw:layer draw:name="measurelines" draw:locked="false" ')
	self.f.write('draw:printable="true" draw:visible="true"/>\n')
	self.f.write('</draw:layer-set>\n')
	self.f.write('<style:master-page style:name="Home" ')
	self.f.write('style:page-master-name="PM0" draw:style-name="dp1"/>\n')
        self.f.write('</office:master-styles>\n')
        self.f.write('</office:document-styles>\n')
	self.f.close()

    def page_break(self):
        self.new_page = 1

    def start_page(self):
        self.f.write('<text:p text:style-name="docgen_page_break">\n')

    def end_page(self):
        self.f.write('</text:p>\n')
        
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
	    self.f.write('" text:level="' + str(self.level) + '">\n')
        if leader != None:
            self.f.write(leader)
            self.f.write('<text:tab-stop/>\n')
        self.new_cell = 0

    def end_paragraph(self):
        if self.level == 0:
            self.f.write('</text:p>\n')
        else:
            self.f.write('</text:h>\n')
        self.new_cell = 1

    def write_note(self,text,format,style_name):
        if format == 1:
            text = text.replace('&','&amp;')       # Must be first
            text = text.replace('<','&lt;')
            text = text.replace('>','&gt;')
            # Replace multiple spaces: have to go from the largest number down
            for n in range(text.count(' '),1,-1):
                text = text.replace(' '*n, ' <text:s text:c="%d"/>' % (n-1) )
            text = text.replace('\n','<text:line-break/>')
            text = text.replace('\t','<text:tab-stop/>')
            text = text.replace('&lt;super&gt;','<text:span text:style-name="GSuper">')
            text = text.replace('&lt;/super&gt;','</text:span>')

            self.start_paragraph(style_name)
            self.f.write('<text:span text:style-name="GRAMPS-preformat">')
            self.f.write(text)
            self.f.write('</text:span>')
            self.end_paragraph()
        elif format == 0:
            for line in text.split('\n\n'):
                self.start_paragraph(style_name)
                line = line.replace('\n',' ')
                line = string.join(string.split(line))
                self.write_text(line)
                self.end_paragraph()

    def write_text(self,text):
        text = text.replace('&','&amp;')       # Must be first
        text = text.replace('<','&lt;')
        text = text.replace('>','&gt;')
        text = text.replace('\n','<text:line-break/>')
        text = text.replace('&lt;super&gt;','<text:span text:style-name="GSuper">')
        text = text.replace('&lt;/super&gt;','</text:span>')
	self.f.write(text)

    def _write_manifest(self):
        self.manifest_xml = tempfile.mktemp()

        try:
            self.f = open(self.manifest_xml,"wb")
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.manifest_xml, msg)
            raise Errors.ReportError(errmsg)
        except:
            pass
            raise Errors.ReportError(_("Could not create %s") % self.manifest_xml)


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
        name = self.name
        self.meta_xml = tempfile.mktemp()

        try:
            self.f = open(self.meta_xml,"wb")
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.meta_xml, msg)
            raise Errors.ReportError(errmsg)
        except:
            pass
            raise Errors.ReportError(_("Could not create %s") % self.meta_xml)

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

    def rotate_text(self,style,text,x,y,angle):

        stype = self.draw_styles[style]
        pname = stype.get_paragraph_style()
        p = self.style_list[pname]
	font = p.get_font()
        size = font.get_size()

        height = size*(len(text))
        oneline = (size/72.0)*2.54
        width = 0
        for line in text:
            width = max(width,FontScale.string_width(font,line))
        wcm = (width/72.0)*2.54
        hcm = (height/72.0)*2.54

        rangle = -((pi/180.0) * angle)

        self.f.write('<draw:text-box draw:style-name="%s" ' % style)
        self.f.write('draw:layer="layout" svg:width="%.3fcm" ' % wcm)
        self.f.write('svg:height="%.3fpt" ' % hcm)
        self.f.write('draw:transform="')
        self.f.write('rotate (%.8f) ' % rangle)
        xloc = x-((wcm/2.0)*cos(-rangle))
        yloc = y-((hcm)*sin(-rangle))-oneline
        self.f.write('translate (%.3fcm %.3fcm)"' % (xloc,yloc))
        self.f.write('>')
        self.f.write('<text:p text:style-name="X%s">' % pname)

        self.f.write('<text:span text:style-name="F%s">\n' % pname)
        self.write_text(string.join(text,'\n'))
        self.f.write('</text:span>\n</text:p>\n</draw:text-box>\n')
        
    def draw_path(self,style,path):
        stype = self.draw_styles[style]

        minx = 9e12
        miny = 9e12
        maxx = 0
        maxy = 0

        for point in path:
            minx = min(point[0],minx)
            miny = min(point[1],miny)
            maxx = max(point[0],maxx)
            maxy = max(point[1],maxy)

        self.f.write('<draw:polygon draw:style-name="%s" draw:layer="layout" ' % style)
	self.f.write('draw:z-index="1" ')
        x = int((minx)*1000)
        y = int((miny)*1000)
        
        self.f.write('svg:x="%d" svg:y="%d" ' % (x,y))
        self.f.write('svg:viewBox="0 0 %d %d" ' % (int(maxx-minx)*1000,int(maxy-miny)*1000))
        self.f.write('svg:width="%.4fcm" ' % (maxx-minx))
        self.f.write('svg:height="%.4fcm" ' % (maxy-miny))
        
        point = path[0]
        x1 = int((point[0]-minx)*1000)
        y1 = int((point[1]-miny)*1000)
        self.f.write('draw:points="%d,%d' % (x1,y1))

        for point in path[1:]:
            x1 = int((point[0]-minx)*1000)
            y1 = int((point[1]-miny)*1000)
            self.f.write(' %d,%d' % (x1,y1))
        self.f.write('"/>\n')

    def draw_line(self,style,x1,y1,x2,y2):
	box_style = self.draw_styles[style]

        self.f.write('<draw:line draw:style="%s" '% style)
        self.f.write('svg:x1="%.3fcm" ' % x1)
        self.f.write('svg:y1="%.3fcm" ' % y1)
        self.f.write('svg:x2="%.3fcm" ' % x2)
        self.f.write('svg:y2="%.3fcm" ' % y2)
        self.f.write('/>\n')

    def draw_text(self,style,text,x,y):
	box_style = self.draw_styles[style]
	para_name = box_style.get_paragraph_style()

        pstyle = self.style_list[para_name]
        font = pstyle.get_font()
        sw = FontScale.string_width(font,text)*1.3

	self.f.write('<draw:text-box draw:style-name="%s" ' % style)
	self.f.write('draw:layer="layout" ')
        # fix this
	self.f.write('draw:z-index="0" ')
	self.f.write('svg:width="%.3fcm" ' % sw)
	self.f.write('svg:height="%.4fpt" ' % (font.get_size()*1.4))

	self.f.write('svg:x="%.3fcm" ' % float(x))
        self.f.write('svg:y="%.3fcm">' % float(y))
        self.f.write('<text:p text:style-name="X%s">' % para_name)
        self.f.write('<text:span text:style-name="F%s">' % para_name)
        self.f.write(text)
        self.f.write('</text:span></text:p>')
        self.f.write('</draw:text-box>\n')

    def draw_bar(self,style,x,y,x2,y2):
	box_style = self.draw_styles[style]
	para_name = box_style.get_paragraph_style()

	self.f.write('<draw:rect text:anchor-type="paragraph" draw:style-name="')
	self.f.write(style)
	self.f.write('" draw:z-index="0" ')
	self.f.write('svg:width="%.3fcm" ' % float(x2-x))
	self.f.write('svg:height="%.3fcm" ' % float(y2-y))
	self.f.write('svg:x="%.3fcm" ' % float(x))
        self.f.write('svg:y="%.3fcm">' % float(y))
        self.f.write('</draw:rect>\n')

    def draw_box(self,style,text,x,y):
	box_style = self.draw_styles[style]
	para_name = box_style.get_paragraph_style()

	self.f.write('<draw:rect text:anchor-type="paragraph" ')
        self.f.write('draw:style-name="%s_shadow" ' % style)
        self.f.write('draw:text-style-name="%s" ' % para_name)
	self.f.write('draw:z-index="0" ')
        self.f.write('svg:width="%.3fcm" ' % box_style.get_width())
	self.f.write('svg:height="%.3fcm" ' % box_style.get_height())
	self.f.write('svg:x="%.3fcm" ' % (float(x)+0.2))
        self.f.write('svg:y="%.3fcm">\n' % (float(y)+0.2))
        self.f.write('</draw:rect>\n')

	self.f.write('<draw:rect text:anchor-type="paragraph" ')
        self.f.write('draw:style-name="%s" ' % style)
        self.f.write('draw:text-style-name="%s" ' % para_name)
	self.f.write('draw:z-index="1" ')
        self.f.write('svg:width="%.3fcm" ' % box_style.get_width())
	self.f.write('svg:height="%.3fcm" ' % box_style.get_height())
	self.f.write('svg:x="%.3fcm" ' % float(x))
        self.f.write('svg:y="%.3fcm">\n' % float(y))
	if text != "":
  	    self.f.write('<text:p text:style-name="%s">' % para_name)
            self.f.write('<text:span text:style-name="F%s">' % para_name)
            text = string.replace(text,'\t','<text:tab-stop/>')
            text = string.replace(text,'\n','<text:line-break/>')
	    self.f.write(text)
            self.f.write('</text:span>')
            self.f.write('</text:p>\n')
        self.f.write('</draw:rect>\n')

    def center_text(self,style,text,x,y):
	box_style = self.draw_styles[style]
	para_name = box_style.get_paragraph_style()
        pstyle = self.style_list[para_name]
        font = pstyle.get_font()

        size = (FontScale.string_width(font,text)/72.0) * 2.54

	self.f.write('<draw:text-box text:anchor-type="paragraph" ')
        self.f.write('draw:style-name="%s" ' % style)
	self.f.write('draw:z-index="0" ')
        self.f.write('svg:width="%.3fcm" ' % self.get_usable_width())
	self.f.write('svg:height="%dpt" ' % (font.get_size()*1.1))

	self.f.write('svg:x="0cm" ')
        self.f.write('svg:y="%.3fcm">\n' % float(y))

	if text != "":
  	    self.f.write('<text:p text:style-name="X%s">' % para_name)
	    self.f.write(text)
            self.f.write('</text:p>\n')
        self.f.write('</draw:text-box>\n')

#--------------------------------------------------------------------------
#
# Register plugins
#
#--------------------------------------------------------------------------
print_label = None
try:
    import grampslib
    import Utils
    
    apptype = 'application/vnd.sun.xml.writer'
    prog = grampslib.default_application_command(apptype)

    if Utils.search_for(prog):
        print_label = _("Open in OpenOffice.org")
except:
    pass
     
Plugins.register_text_doc(_("OpenOffice.org Writer"),OpenOfficeDoc,1,1,1,
                           ".sxw",print_label)
Plugins.register_book_doc(_("OpenOffice.org Writer"),OpenOfficeDoc,1,1,1,".sxw")

Plugins.register_draw_doc(_("OpenOffice.org Draw"),OpenOfficeDoc,1,1,".sxd",
                          print_label);
