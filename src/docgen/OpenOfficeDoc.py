#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2007       Brian G. Matherly
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
import zipfile
import time
from cStringIO import StringIO
from math import pi, cos, sin
from gettext import gettext as _
from xml.sax.saxutils import escape

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import BaseDoc
import const
from PluginUtils import register_text_doc, register_draw_doc, register_book_doc
from ReportBase import ReportUtils
import ImgManip
import FontScale
import Mime
import Utils
import Errors

#-------------------------------------------------------------------------
#
# constants
#
#-------------------------------------------------------------------------
_apptype = 'application/vnd.sun.xml.writer'

_esc_map = {
    '\x1a'           : '',
    '\x0c'           : '',
    '\n'             : '<text:line-break/>',
    '&lt;super&gt;'  :  '<text:span text:style-name="GSuper">',
    '&lt;/super&gt;' : '</text:span>',
    }

#-------------------------------------------------------------------------
#
# OpenOfficeDoc
#
#-------------------------------------------------------------------------
class OpenOfficeDoc(BaseDoc.BaseDoc,BaseDoc.TextDoc,BaseDoc.DrawDoc):

    def __init__(self,styles,type,template):
        BaseDoc.BaseDoc.__init__(self,styles,type,template)
        self.media_list = []
        self.cntnt = None
        self.filename = None
        self.level = 0
        self.time = "0000-00-00T00:00:00"
        self.new_page = 0
        self.new_cell = 0
        self.page = 0
        self.first_page = 1

    def open(self,filename):
        t = time.localtime(time.time())
        self.time = "%04d-%02d-%02dT%02d:%02d:%02d" % \
                    (t[0],t[1],t[2],t[3],t[4],t[5])

        if filename[-4:] != ".sxw":
            self.filename = filename + ".sxw"
        else:
            self.filename = filename

        self.filename = os.path.normpath(os.path.abspath(self.filename))
        self.cntnt = StringIO()

    def init(self):

        assert (not self.init_called)
        self.init_called = True
        
        self.lang = Utils.xml_lang()
        style_sheet = self.get_style_sheet()

        self.cntnt.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.cntnt.write('<office:document-content ')
        self.cntnt.write('xmlns:office="http://openoffice.org/2000/office" ')
        self.cntnt.write('xmlns:style="http://openoffice.org/2000/style" ')
        self.cntnt.write('xmlns:text="http://openoffice.org/2000/text" ')
        self.cntnt.write('xmlns:table="http://openoffice.org/2000/table" ')
        self.cntnt.write('xmlns:draw="http://openoffice.org/2000/drawing" ')
        self.cntnt.write('xmlns:fo="http://www.w3.org/1999/XSL/Format" ')
        self.cntnt.write('xmlns:xlink="http://www.w3.org/1999/xlink" ')
        self.cntnt.write('xmlns:number="http://openoffice.org/2000/datastyle" ')
        self.cntnt.write('xmlns:svg="http://www.w3.org/2000/svg" ')
        self.cntnt.write('xmlns:chart="http://openoffice.org/2000/chart" ')
        self.cntnt.write('xmlns:dr3d="http://openoffice.org/2000/dr3d" ')
        self.cntnt.write('xmlns:math="http://www.w3.org/1998/Math/MathML" ')
        self.cntnt.write('xmlns:form="http://openoffice.org/2000/form" ')
        self.cntnt.write('xmlns:script="http://openoffice.org/2000/script" ')
        self.cntnt.write('office:class="text" office:version="0.9">\n')
        self.cntnt.write('<office:script/>\n')
        self.cntnt.write('<office:font-decls>\n')
        self.cntnt.write('<style:font-decl style:name="Courier" fo:font-family="Courier" ')
        self.cntnt.write('style:font-family-generic="modern" style:font-pitch="fixed"/>\n')
        self.cntnt.write('<style:font-decl style:name="Times New Roman" ')
        self.cntnt.write('fo:font-family="&apos;Times New Roman&apos;" ')
        self.cntnt.write('style:font-family-generic="roman" ')
        self.cntnt.write('style:font-pitch="variable"/>\n')
        self.cntnt.write('<style:font-decl style:name="Arial" ')
        self.cntnt.write('fo:font-family="Arial" ')
        self.cntnt.write('style:font-family-generic="swiss" ')
        self.cntnt.write('style:font-pitch="variable"/>\n')
        self.cntnt.write('</office:font-decls>\n')
        self.cntnt.write('<office:automatic-styles>\n')
        self.cntnt.write('<style:style style:name="docgen_page_break" style:family="paragraph">\n')
        self.cntnt.write('<style:properties fo:break-before="page"/>\n')
        self.cntnt.write('</style:style>\n')
        self.cntnt.write('<style:style style:name="GSuper" style:family="text">')
        self.cntnt.write('<style:properties style:text-position="super 58%"/>')
        self.cntnt.write('</style:style>\n')
        self.cntnt.write('<style:style style:name="GRAMPS-preformat" style:family="text">')
        self.cntnt.write('<style:properties style:font-name="Courier"/>')
        self.cntnt.write('</style:style>\n')

        for style_name in style_sheet.get_draw_style_names():
            style = style_sheet.get_draw_style(style_name)
            self.cntnt.write('<style:style style:name="%s"' % style_name)
            self.cntnt.write(' style:family="graphics">\n')
            self.cntnt.write('<style:properties ')
            self.cntnt.write('draw:fill="solid" ')
            self.cntnt.write('draw:fill-color="#%02x%02x%02x" ' % style.get_fill_color())

            if style.get_line_style() == BaseDoc.DASHED:
                self.cntnt.write('svg:stroke-color="#cccccc" ')
            else:
                self.cntnt.write('svg:stroke-color="#%02x%02x%02x" ' % style.get_color())
                
            if style.get_line_width():
                self.cntnt.write('draw:stroke="solid" ')
            else:
                self.cntnt.write('draw:stroke="none" ')
            self.cntnt.write('draw:shadow="hidden" ')
            self.cntnt.write('style:run-through="background" ')
            self.cntnt.write('/>\n')
            self.cntnt.write('</style:style>\n')

            self.cntnt.write('<style:style style:name="%s_shadow"' % style_name)
            self.cntnt.write(' style:family="graphics">\n')
            self.cntnt.write('<style:properties ')
            self.cntnt.write('draw:fill="solid" ')
            self.cntnt.write('draw:fill-color="#cccccc" ')
            self.cntnt.write('draw:stroke="none" ')
            self.cntnt.write('style:run-through="background" ')
            self.cntnt.write('/>\n')
            self.cntnt.write('</style:style>\n')
            
        self.cntnt.write('<style:style style:name="nofill" ')
        self.cntnt.write('style:family="graphics">\n')
        self.cntnt.write('\t<style:properties draw:stroke="none" ')
        self.cntnt.write('svg:stroke-color="#000000" draw:fill="none" ')
        self.cntnt.write('draw:fill-color="#ff3f00" draw:shadow="hidden" ')
        self.cntnt.write('style:run-through="background"/>\n')
        self.cntnt.write('</style:style>\n')

        for style_name in style_sheet.get_paragraph_style_names():
            style = style_sheet.get_paragraph_style(style_name)
            self.cntnt.write('<style:style style:name="NL%s" ' % style_name)
            self.cntnt.write('style:family="paragraph" ')
            self.cntnt.write('style:parent-style-name="%s">\n' % style_name)
            self.cntnt.write('<style:properties fo:break-before="page"/>\n')
            self.cntnt.write('</style:style>\n')

            self.cntnt.write('<style:style style:name="X%s" ' % style_name)
            self.cntnt.write('style:family="paragraph" ')
            self.cntnt.write('style:parent-style-name="Standard" ')
            self.cntnt.write('style:class="text">\n')
            self.cntnt.write('<style:properties ')

            if style.get_padding() != 0.0:
               self.cntnt.write('fo:padding="%.3fcm" ' % style.get_padding())
            if style.get_header_level() > 0:
                self.cntnt.write('fo:keep-with-next="true" ')

            align = style.get_alignment()
            if align == BaseDoc.PARA_ALIGN_LEFT:
               self.cntnt.write('fo:text-align="start" ')
            elif align == BaseDoc.PARA_ALIGN_RIGHT:
               self.cntnt.write('fo:text-align="end" ')
            elif align == BaseDoc.PARA_ALIGN_CENTER:
               self.cntnt.write('fo:text-align="center" ')
               self.cntnt.write('style:justify-single-word="false" ')
            else:
               self.cntnt.write('fo:text-align="justify" ')
               self.cntnt.write('style:justify-single-word="false" ')
            font = style.get_font()
            if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
                self.cntnt.write('style:font-name="Arial" ')
            else:
                self.cntnt.write('style:font-name="Times New Roman" ')
            self.cntnt.write('fo:font-size="%.3fpt" ' % font.get_size())
            self.cntnt.write('style:font-size-asian="%.3fpt" '
                             % font.get_size())
            color = font.get_color()
            self.cntnt.write('fo:color="#%02x%02x%02x" ' % color)
            if font.get_bold():
                self.cntnt.write('fo:font-weight="bold" ')
            if font.get_italic():
                self.cntnt.write('fo:font-style="italic" ')
            if font.get_underline():
                self.cntnt.write('style:text-underline="single" ')
                self.cntnt.write('style:text-underline-color="font-color" ')
            self.cntnt.write('fo:text-indent="%.2fcm" '
                             % style.get_first_indent())
            self.cntnt.write('fo:margin-right="%.2fcm" '
                             % style.get_right_margin())
            self.cntnt.write('fo:margin-left="%.2fcm" '
                             % style.get_left_margin())
            self.cntnt.write('fo:margin-top="%.2fcm" '
                             % style.get_top_margin())
            self.cntnt.write('fo:margin-bottom="%.2fcm"'
                             % style.get_bottom_margin())
            self.cntnt.write('/>\n')
            self.cntnt.write('</style:style>\n')

            self.cntnt.write('<style:style style:name="F%s" ' % style_name)
            self.cntnt.write('style:family="text">\n')
            self.cntnt.write('<style:properties ')
            align = style.get_alignment()
            if align == BaseDoc.PARA_ALIGN_LEFT:
               self.cntnt.write('fo:text-align="start" ')
            elif align == BaseDoc.PARA_ALIGN_RIGHT:
               self.cntnt.write('fo:text-align="end" ')
            elif align == BaseDoc.PARA_ALIGN_CENTER:
               self.cntnt.write('fo:text-align="center" ')
            font = style.get_font()
            if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
                self.cntnt.write('style:font-name="Arial" ')
            else:
                self.cntnt.write('style:font-name="Times New Roman" ')
            color = font.get_color()
            self.cntnt.write('fo:color="#%02x%02x%02x" ' % color)
            if font.get_bold():
                self.cntnt.write('fo:font-weight="bold" ')
            if font.get_italic():
                self.cntnt.write('fo:font-style="italic" ')
            self.cntnt.write('fo:font-size="%.3fpt" ' % font.get_size())
            self.cntnt.write('style:font-size-asian="%.3fpt"/> ' % font.get_size())
            self.cntnt.write('</style:style>\n')

        for style_name in style_sheet.get_table_style_names():
            style = style_sheet.get_table_style(style_name)
            self.cntnt.write('<style:style style:name="%s" ' % style_name)
            self.cntnt.write('style:family="table">\n')
            table_width = float(self.get_usable_width())
            table_width_str = "%.4f" % table_width
            self.cntnt.write('<style:properties style:width="%scm" '%table_width_str)
            self.cntnt.write('/>\n')
            self.cntnt.write('</style:style>\n')
            for col in range(0,style.get_columns()):
                self.cntnt.write('<style:style style:name="')
                self.cntnt.write(style_name + '.' + str(chr(ord('A')+col)) +'" ')
                self.cntnt.write('style:family="table-column">')
                width = table_width * float(style.get_column_width(col)/100.0)
                width_str = "%.4f" % width
                self.cntnt.write('<style:properties ')
                self.cntnt.write('style:column-width="%scm"/>' % width_str)
                self.cntnt.write('</style:style>\n')
                
        for cell in style_sheet.get_cell_style_names():
            cell_style = style_sheet.get_cell_style(cell)
            self.cntnt.write('<style:style style:name="%s" ' % cell)
            self.cntnt.write('style:family="table-cell">\n')
            self.cntnt.write('<style:properties')
            self.cntnt.write(' fo:padding="%.3fcm"' % cell_style.get_padding())
            if cell_style.get_top_border():
                self.cntnt.write(' fo:border-top="0.002cm solid #000000"')
            else:
                self.cntnt.write(' fo:border-top="none"')
            if cell_style.get_bottom_border():
                self.cntnt.write(' fo:border-bottom="0.002cm solid #000000"')
            else:
                self.cntnt.write(' fo:border-bottom="none"')
            if cell_style.get_left_border():
                self.cntnt.write(' fo:border-left="0.002cm solid #000000"')
            else:
                self.cntnt.write(' fo:border-left="none"')
            if cell_style.get_right_border():
                self.cntnt.write(' fo:border-right="0.002cm solid #000000"')
            else:
                self.cntnt.write(' fo:border-right="none"')
            self.cntnt.write('/>\n')
            self.cntnt.write('</style:style>\n')
            
        self.cntnt.write('<style:style style:name="wraprow" style:family="table-row">\n')
        self.cntnt.write('<style:properties style:keep-together="true" />\n')
        self.cntnt.write('</style:style>\n')
        self.cntnt.write('<style:style style:name="Tbold" style:family="text">\n')
        self.cntnt.write('<style:properties fo:font-weight="bold"/>\n')
        self.cntnt.write('</style:style>\n')

        #Begin photo style
        self.cntnt.write('<style:style style:name="Left" style:family="graphics"')
        self.cntnt.write(' style:parent-style-name="photo">')
        self.cntnt.write('<style:properties style:run-through="foreground"')
        self.cntnt.write(' style:wrap="dynamic"')
        self.cntnt.write(' style:number-wrapped-paragraphs="no-limit"')
        self.cntnt.write(' style:wrap-contour="false" style:vertical-pos="from-top"')
        self.cntnt.write(' style:vertical-rel="paragraph-content"')
        self.cntnt.write(' style:horizontal-pos="left"')
        self.cntnt.write(' style:horizontal-rel="paragraph-content"')
        self.cntnt.write(' style:mirror="none" fo:clip="rect(0cm 0cm 0cm 0cm)"')
        self.cntnt.write(' draw:luminance="0%" draw:contrast="0" draw:red="0%"')
        self.cntnt.write(' draw:green="0%" draw:blue="0%" draw:gamma="1"')
        self.cntnt.write(' draw:color-inversion="false" draw:transparency="-100%"')
        self.cntnt.write(' draw:color-mode="standard"/>')
        self.cntnt.write('</style:style>\n')

        self.cntnt.write('<style:style style:name="Right" style:family="graphics"')
        self.cntnt.write(' style:parent-style-name="photo">')
        self.cntnt.write('<style:properties style:run-through="foreground"')
        self.cntnt.write(' style:wrap="dynamic"')
        self.cntnt.write(' style:number-wrapped-paragraphs="no-limit"')
        self.cntnt.write(' style:wrap-contour="false" style:vertical-pos="from-top"')
        self.cntnt.write(' style:vertical-rel="paragraph-content"')
        self.cntnt.write(' style:horizontal-pos="right"')
        self.cntnt.write(' style:horizontal-rel="paragraph-content"')
        self.cntnt.write(' style:mirror="none" fo:clip="rect(0cm 0cm 0cm 0cm)"')
        self.cntnt.write(' draw:luminance="0%" draw:contrast="0" draw:red="0%"')
        self.cntnt.write(' draw:green="0%" draw:blue="0%" draw:gamma="1"')
        self.cntnt.write(' draw:color-inversion="false" draw:transparency="-100%"')
        self.cntnt.write(' draw:color-mode="standard"/>')
        self.cntnt.write('</style:style>\n')

        self.cntnt.write('<style:style style:name="Single" style:family="graphics"')
        self.cntnt.write(' style:parent-style-name="Graphics">')
        self.cntnt.write('<style:properties style:vertical-pos="from-top"')
        self.cntnt.write(' style:mirror="none" fo:clip="rect(0cm 0cm 0cm 0cm)"')
        self.cntnt.write(' draw:luminance="0%" draw:contrast="0" draw:red="0%"')
        self.cntnt.write(' draw:green="0%" draw:blue="0%" draw:gamma="1"')
        self.cntnt.write(' draw:color-inversion="false" draw:transparency="-100%"')
        self.cntnt.write(' draw:color-mode="standard"/>')
        self.cntnt.write('</style:style>\n')

        self.cntnt.write('<style:style style:name="Row" style:family="graphics"')
        self.cntnt.write(' style:parent-style-name="Graphics">')
        self.cntnt.write('<style:properties style:vertical-pos="from-top"')
        self.cntnt.write(' style:vertical-rel="paragraph"')
        self.cntnt.write(' style:horizontal-pos="from-left"')
        self.cntnt.write(' style:horizontal-rel="paragraph"')
        self.cntnt.write(' style:mirror="none" fo:clip="rect(0cm 0cm 0cm 0cm)"')
        self.cntnt.write(' draw:luminance="0%" draw:contrast="0" draw:red="0%"')
        self.cntnt.write(' draw:green="0%" draw:blue="0%" draw:gamma="1"')
        self.cntnt.write(' draw:color-inversion="false" draw:transparency="-100%"')
        self.cntnt.write(' draw:color-mode="standard"/>')
        self.cntnt.write('</style:style>\n')

        #end of Photo style edits

        self.cntnt.write('</office:automatic-styles>\n')
        self.cntnt.write('<office:body>\n')

    def close(self):
        self.cntnt.write('</office:body>\n')
        self.cntnt.write('</office:document-content>\n')
        self._write_styles_file()
        self._write_manifest()
        self._write_meta_file()
        self._write_zip()
        if self.print_req:
            app = Mime.get_application(_apptype)
            Utils.launch(app[0],self.filename)

    def add_media_object(self,name,pos,x_cm,y_cm):

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

        media_list_item = (name,act_width,act_height)
        if not media_list_item in self.media_list:
            self.media_list.append(media_list_item)

        base = os.path.basename(name)
        tag = base.replace('.','_')
        
        if self.new_cell:
            self.cntnt.write('<text:p>')
        if pos == "left":
            self.cntnt.write('<draw:image draw:style-name="Left" ')
        elif pos == "right":
            self.cntnt.write('<draw:image draw:style-name="Right" ')
        elif pos == "single":
            self.cntnt.write('<draw:image draw:style-name="Single" ')
        else:
            self.cntnt.write('<draw:image draw:style-name="Row" ')

        self.cntnt.write('draw:name="%s" ' % tag)
        self.cntnt.write('text:anchor-type="paragraph" ')
        self.cntnt.write('svg:width="%.3fcm" ' % act_width)
        self.cntnt.write('svg:height="%.3fcm" ' % act_height)
        self.cntnt.write('draw:z-index="0" ')
        self.cntnt.write('xlink:href="#Pictures/')
        self.cntnt.write(base)
        self.cntnt.write('" xlink:type="simple" xlink:show="embed" ')
        self.cntnt.write('xlink:actuate="onLoad"/>\n')
        if self.new_cell:
            self.cntnt.write('</text:p>\n')

    def start_table(self,name,style_name):
        self.cntnt.write('<table:table table:name="%s" ' % name)
        self.cntnt.write('table:style-name="%s">\n' % style_name)
        styles = self.get_style_sheet()
        table = styles.get_table_style(style_name)
        for col in range(0,table.get_columns()):
            self.cntnt.write('<table:table-column table:style-name="')
            self.cntnt.write(style_name + '.' + str(chr(ord('A')+col)) +'"/>\n')

    def end_table(self):
        self.cntnt.write('</table:table>\n')

    def start_row(self):
        self.cntnt.write('<table:table-row table:style-name="wraprow">\n')

    def end_row(self):
        self.cntnt.write('</table:table-row>\n')

    def start_cell(self,style_name,span=1):
        self.span = span
        self.cntnt.write('<table:table-cell table:style-name="%s" ' % style_name)
        self.cntnt.write('table:value-type="string"')
        if span > 1:
            self.cntnt.write(' table:number-columns-spanned="%s">\n' % span)
        else:             
            self.cntnt.write('>\n')
        self.new_cell = 1

    def end_cell(self):
        self.cntnt.write('</table:table-cell>\n')
        for col in range(1,self.span):
            self.cntnt.write('<table:covered-table-cell/>\n')
        self.new_cell = 0

    def start_bold(self):
        self.cntnt.write('<text:span text:style-name="Tbold">')

    def end_bold(self):
        self.cntnt.write('</text:span>')
        
    def start_superscript(self):
        self.cntnt.write('<text:span text:style-name="GSuper">')

    def end_superscript(self):
        self.cntnt.write('</text:span>')

    def _add_zip(self,zfile,name,data,t):
        zipinfo = zipfile.ZipInfo(name.encode('latin-1'))
        zipinfo.date_time = t
        zipinfo.compress_type = zipfile.ZIP_DEFLATED
        zfile.writestr(zipinfo,data)

    def _write_zip(self):
        try:
            zfile = zipfile.ZipFile(self.filename,"w",zipfile.ZIP_DEFLATED)    
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.filename, msg)
            raise Errors.ReportError(errmsg)
        except:
            raise Errors.ReportError(_("Could not create %s") % self.filename)

        t = time.localtime(time.time())[:6]

        self._add_zip(zfile,"META-INF/manifest.xml",self.mfile.getvalue(),t)
        self._add_zip(zfile,"content.xml",self.cntnt.getvalue(),t)
        self._add_zip(zfile,"meta.xml",self.meta.getvalue(),t)
        self._add_zip(zfile,"styles.xml",self.sfile.getvalue(),t)

        self.mfile.close()
        self.cntnt.close()
        self.meta.close()
        self.sfile.close()
        
        for image in self.media_list:
            try:
                ifile = open(image[0],mode='rb')
                base = os.path.basename(image[0])
                self._add_zip(zfile,"Pictures/%s" % base, ifile.read(),t)
                ifile.close()
            except:
                print "Could not open %s" % image[0]
        zfile.close()

    def _write_styles_file(self):
        self.sfile = StringIO()
        style_sheet = self.get_style_sheet()
                                     
        self.sfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.sfile.write('<office:document-styles ')
        self.sfile.write('xmlns:office="http://openoffice.org/2000/office" ')
        self.sfile.write('xmlns:style="http://openoffice.org/2000/style" ')
        self.sfile.write('xmlns:text="http://openoffice.org/2000/text" ')
        self.sfile.write('xmlns:table="http://openoffice.org/2000/table" ')
        self.sfile.write('xmlns:draw="http://openoffice.org/2000/drawing" ')
        self.sfile.write('xmlns:fo="http://www.w3.org/1999/XSL/Format" ')
        self.sfile.write('xmlns:xlink="http://www.w3.org/1999/xlink" ')
        self.sfile.write('xmlns:number="http://openoffice.org/2000/datastyle" ')
        self.sfile.write('xmlns:svg="http://www.w3.org/2000/svg" ')
        self.sfile.write('xmlns:chart="http://openoffice.org/2000/chart" ')
        self.sfile.write('xmlns:dr3d="http://openoffice.org/2000/dr3d" ')
        self.sfile.write('xmlns:math="http://www.w3.org/1998/Math/MathML" ')
        self.sfile.write('xmlns:form="http://openoffice.org/2000/form" ')
        self.sfile.write('xmlns:script="http://openoffice.org/2000/script" ')
        self.sfile.write('office:version="0.9">\n')
        self.sfile.write('<office:font-decls>\n')
        self.sfile.write('<style:font-decl style:name="Times New Roman" ')
        self.sfile.write('fo:font-family="&apos;Times New Roman&apos;" ')
        self.sfile.write('style:font-family-generic="roman" ')
        self.sfile.write('style:font-pitch="variable"/>\n')
        self.sfile.write('<style:font-decl style:name="Arial" ')
        self.sfile.write('fo:font-family="Arial" ')
        self.sfile.write('style:font-family-generic="swiss" ')
        self.sfile.write('style:font-pitch="variable"/>\n')
        self.sfile.write('</office:font-decls>\n')
        self.sfile.write('<office:styles>\n')
        self.sfile.write('<style:default-style style:family="paragraph">\n')
        self.sfile.write('<style:properties style:font-name="Times New Roman" ')
        self.sfile.write('style:font-pitch-asian="fixed" ')
        self.sfile.write('style:font-pitch-complex="fixed" ')
        self.sfile.write('style:tab-stop-distance="2.205cm"/>\n')
        self.sfile.write('</style:default-style>\n')
        self.sfile.write('<style:style style:name="Standard" ')
        self.sfile.write('style:family="paragraph" style:class="text"/>\n')
        self.sfile.write('<style:style style:name="photo" style:family="graphics">\n')
        self.sfile.write('<style:properties text:anchor-type="paragraph" ')
        self.sfile.write('svg:x="0cm" svg:y="0cm" style:wrap="none" ')
        self.sfile.write('style:vertical-pos="top" ')
        self.sfile.write('style:vertical-rel="paragraph-content" ')
        self.sfile.write('style:horizontal-pos="center" ')
        self.sfile.write('style:horizontal-rel="paragraph-content"/>\n')
        self.sfile.write('</style:style>\n')
        
        for name in style_sheet.get_paragraph_style_names():
            style = style_sheet.get_paragraph_style(name)
            self.sfile.write('<style:style style:name="%s" ' % name)
            self.sfile.write('style:family="paragraph" ')
            self.sfile.write('style:parent-style-name="Standard" ')
            self.sfile.write('style:class="text">\n')
            self.sfile.write('<style:properties ')

            if style.get_padding() != 0.0:
               self.sfile.write('fo:padding="%.3fcm" ' % style.get_padding())
            if style.get_top_border():
               self.sfile.write('fo:border-top="0.002cm solid #000000" ')
            if style.get_bottom_border():
               self.sfile.write('fo:border-bottom="0.002cm solid #000000" ')
            if style.get_right_border():
               self.sfile.write('fo:border-right="0.002cm solid #000000" ')
            if style.get_left_border():
               self.sfile.write('fo:border-left="0.002cm solid #000000" ')
            if style.get_header_level() > 0:
                self.sfile.write('fo:keep-with-next="true" ')

            align = style.get_alignment()
            if align == BaseDoc.PARA_ALIGN_LEFT:
               self.sfile.write('fo:text-align="start" ')
            elif align == BaseDoc.PARA_ALIGN_RIGHT:
               self.sfile.write('fo:text-align="end" ')
            elif align == BaseDoc.PARA_ALIGN_CENTER:
               self.sfile.write('fo:text-align="center" ')
               self.sfile.write('style:justify-single-word="false" ')
            else:
               self.sfile.write('fo:text-align="justify" ')
               self.sfile.write('style:justify-single-word="false" ')
            font = style.get_font()
            if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
                self.sfile.write('style:font-name="Arial" ')
            else:
                self.sfile.write('style:font-name="Times New Roman" ')
            self.sfile.write('fo:font-size="%.3fpt" ' % font.get_size())
            color = font.get_color()
            self.sfile.write('fo:color="#%02x%02x%02x" ' % color)
            if font.get_bold():
                self.sfile.write('fo:font-weight="bold" ')
            if font.get_italic():
                self.sfile.write('fo:font-style="italic" ')
            if font.get_underline():
                self.sfile.write('style:text-underline="single" ')
                self.sfile.write('style:text-underline-color="font-color" ')
            self.sfile.write('fo:text-indent="%.2fcm" '
                             % style.get_first_indent())
            self.sfile.write('fo:margin-right="%.2fcm" '
                             % style.get_right_margin())
            self.sfile.write('fo:margin-left="%.2fcm" '
                             % style.get_left_margin())
            self.sfile.write('fo:margin-top="%.2fcm" '
                             % style.get_top_margin())
            self.sfile.write('fo:margin-bottom="%.2fcm"'
                             % style.get_bottom_margin())
            self.sfile.write('/>\n')
            self.sfile.write('</style:style>\n')

        # Current no leading number format for headers

        self.sfile.write('<text:outline-style>\n')
        self.sfile.write('<text:outline-level-style text:level="1" style:num-format=""/>\n')
        self.sfile.write('<text:outline-level-style text:level="2" style:num-format=""/>\n')
        self.sfile.write('<text:outline-level-style text:level="3" style:num-format=""/>\n')
        self.sfile.write('<text:outline-level-style text:level="4" style:num-format=""/>\n')
        self.sfile.write('<text:outline-level-style text:level="5" style:num-format=""/>\n')
        self.sfile.write('<text:outline-level-style text:level="6" style:num-format=""/>\n')
        self.sfile.write('<text:outline-level-style text:level="7" style:num-format=""/>\n')
        self.sfile.write('<text:outline-level-style text:level="8" style:num-format=""/>\n')
        self.sfile.write('<text:outline-level-style text:level="9" style:num-format=""/>\n')
        self.sfile.write('<text:outline-level-style text:level="10" style:num-format=""/>\n')
        self.sfile.write('</text:outline-style>\n')
            
        self.sfile.write('</office:styles>\n')
        self.sfile.write('<office:automatic-styles>\n')
        self.sfile.write('<style:page-master style:name="pm1">\n')
        self.sfile.write('<style:properties fo:page-width="%.3fcm" ' % self.paper.get_size().get_width())
        self.sfile.write('fo:page-height="%.3fcm" ' % self.paper.get_size().get_height())
        self.sfile.write('style:num-format="1" ')
        if self.paper.get_orientation() == BaseDoc.PAPER_PORTRAIT:
            self.sfile.write('style:print-orientation="portrait" ')
        else:
            self.sfile.write('style:print-orientation="landscape" ')
        self.sfile.write('fo:margin-top="%.2fcm" ' % self.paper.get_top_margin())
        self.sfile.write('fo:margin-bottom="%.2fcm" ' % self.paper.get_bottom_margin())
        self.sfile.write('fo:margin-left="%.2fcm" ' % self.paper.get_left_margin())
        self.sfile.write('fo:margin-right="%.2fcm" ' % self.paper.get_right_margin())
        self.sfile.write('style:footnote-max-height="0cm">\n')
        self.sfile.write('<style:footnote-sep style:width="0.018cm" ')
        self.sfile.write('style:distance-before-sep="0.101cm" ')
        self.sfile.write('style:distance-after-sep="0.101cm" ')
        self.sfile.write('style:adjustment="left" style:rel-width="25%" ')
        self.sfile.write('style:color="#000000"/>\n')
        self.sfile.write('</style:properties>\n')
        self.sfile.write('<style:header-style/>\n')
        self.sfile.write('<style:footer-style/>\n')
        self.sfile.write('</style:page-master>\n')
        self.sfile.write('</office:automatic-styles>\n')
        self.sfile.write('<office:master-styles>\n')
        self.sfile.write('<draw:layer-set>\n')
        self.sfile.write('<draw:layer draw:name="layout"/>\n')
        self.sfile.write('<draw:layer draw:name="background"/>\n')
        self.sfile.write('<draw:layer draw:name="backgroundobjects"/>\n')
        self.sfile.write('<draw:layer draw:name="controls"/>\n')
        self.sfile.write('<draw:layer draw:name="measurelines"/>\n')
        self.sfile.write('</draw:layer-set>\n')
        self.sfile.write('<style:master-page style:name="Standard" ')
        self.sfile.write('style:page-master-name="pm1"/>\n')
        self.sfile.write('</office:master-styles>\n')
        self.sfile.write('</office:document-styles>\n')

    def page_break(self):
        self.new_page = 1

    def start_page(self):
        self.cntnt.write('<text:p text:style-name="docgen_page_break">\n')

    def end_page(self):
        self.cntnt.write('</text:p>\n')
        
    def start_paragraph(self,style_name,leader=None):
        style_sheet = self.get_style_sheet()
        style = style_sheet.get_paragraph_style(style_name)
        self.level = style.get_header_level()
        if self.new_page == 1:
            self.new_page = 0 
            name = "NL%s" % style_name
        else:
            name = style_name
        if self.level == 0:
            self.cntnt.write('<text:p text:style-name="%s">' % name)
        else:
            self.cntnt.write('<text:h text:style-name="')
            self.cntnt.write(name)
            self.cntnt.write('" text:level="%d">' % self.level)
        if leader != None:
            self.cntnt.write(leader)
            self.cntnt.write('<text:tab-stop/>')
        self.new_cell = 0

    def end_paragraph(self):
        if self.level == 0:
            self.cntnt.write('</text:p>\n')
        else:
            self.cntnt.write('</text:h>\n')
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
            text = text.replace('&lt;super&gt;',
                                '<text:span text:style-name="GSuper">')
            text = text.replace('&lt;/super&gt;','</text:span>')

            self.start_paragraph(style_name)
            self.cntnt.write('<text:span text:style-name="GRAMPS-preformat">')
            self.cntnt.write(text)
            self.cntnt.write('</text:span>')
            self.end_paragraph()
        elif format == 0:
            for line in text.split('\n\n'):
                self.start_paragraph(style_name)
                line = line.replace('\n',' ')
                line = ' '.join(line.split())
                self.write_text(line)
                self.end_paragraph()

    def write_text(self,text,mark=None):
        """
        Uses the xml.sax.saxutils.escape function to convert XML
        entities. The _esc_map dictionary allows us to add our own
        mappings.
        """
        if mark:
            key = escape(mark.key,_esc_map)
            key = key.replace('"','&quot;')
            if mark.type == BaseDoc.INDEX_TYPE_ALP:
                self.cntnt.write('<text:alphabetical-index-mark ')
                self.cntnt.write('text:string-value="%s" />' % key)
            elif mark.type == BaseDoc.INDEX_TYPE_TOC:
                self.cntnt.write('<text:toc-mark ')
                self.cntnt.write('text:string-value="%s" ' % key)
                self.cntnt.write('text:outline-level="%d" />' % mark.level)
        self.cntnt.write(escape(text,_esc_map))

    def _write_manifest(self):
        self.mfile = StringIO()

        self.mfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.mfile.write('<manifest:manifest ')
        self.mfile.write('xmlns:manifest="http://openoffice.org/2001/manifest">')
        self.mfile.write('<manifest:file-entry ')
        self.mfile.write('manifest:media-type="application/vnd.sun.xml.writer" ')
        self.mfile.write('manifest:full-path="/"/>')
        for image in self.media_list:
            i = image[0]
            base = os.path.basename(i)
            self.mfile.write('<manifest:file-entry manifest:media-type="" ')
            self.mfile.write('manifest:full-path="Pictures/')
            self.mfile.write(base)
            self.mfile.write('"/>')
        self.mfile.write('<manifest:file-entry manifest:media-type="" ')
        self.mfile.write('manifest:full-path="Pictures/"/>')
        self.mfile.write('<manifest:file-entry manifest:media-type="text/xml" ')
        self.mfile.write('manifest:full-path="content.xml"/>')
        self.mfile.write('<manifest:file-entry manifest:media-type="text/xml" ')
        self.mfile.write('manifest:full-path="styles.xml"/>')
        self.mfile.write('<manifest:file-entry manifest:media-type="text/xml" ')
        self.mfile.write('manifest:full-path="meta.xml"/>')
        self.mfile.write('</manifest:manifest>\n')

    def _write_meta_file(self):
        self.meta = StringIO()

        self.meta.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.meta.write('<office:document-meta ')
        self.meta.write('xmlns:office="http://openoffice.org/2000/office" ')
        self.meta.write('xmlns:xlink="http://www.w3.org/1999/xlink" ')
        self.meta.write('xmlns:dc="http://purl.org/dc/elements/1.1/" ')
        self.meta.write('xmlns:meta="http://openoffice.org/2000/meta" ')
        self.meta.write('office:version="0.9">\n');
        self.meta.write('<office:meta>\n')
        self.meta.write('<meta:generator>')
        self.meta.write(const.PROGRAM_NAME + ' ' + const.VERSION)
        self.meta.write('</meta:generator>\n')
        self.meta.write('<meta:initial-creator>')
        self.meta.write(self.get_creator())
        self.meta.write('</meta:initial-creator>\n')
        self.meta.write('<meta:creation-date>')
        self.meta.write(self.time)
        self.meta.write('</meta:creation-date>\n')
        self.meta.write('<dc:creator>')
        self.meta.write(self.get_creator())
        self.meta.write('</dc:creator>\n')
        self.meta.write('<dc:date>')
        self.meta.write(self.time)
        self.meta.write('</dc:date>\n')
        self.meta.write('<meta:print-date>0-00-00T00:00:00</meta:print-date>\n')
        self.meta.write('<dc:language>%s</dc:language>\n' % self.lang)
        self.meta.write('<meta:editing-cycles>1</meta:editing-cycles>\n')
        self.meta.write('<meta:editing-duration>PT0S</meta:editing-duration>\n')
        self.meta.write('<meta:user-defined meta:name="Info 0"/>\n')
        self.meta.write('<meta:user-defined meta:name="Info 1"/>\n')
        self.meta.write('<meta:user-defined meta:name="Info 2"/>\n')
        self.meta.write('<meta:user-defined meta:name="Info 3"/>\n')
        self.meta.write('</office:meta>\n')
        self.meta.write('</office:document-meta>\n')

    def rotate_text(self,style,text,x,y,angle):
        style_sheet = self.get_style_sheet()
        stype = style_sheet.get_draw_style(style)
        pname = stype.get_paragraph_style()
        p = style_sheet.get_paragraph_style(pname)
        font = p.get_font()
        size = font.get_size()

        height = size*(len(text))
        oneline = (size/72.0)*2.54
        width = 0
        for line in text:
            width = max(width,FontScale.string_width(font,line))
        wcm = (width/72.0)*2.54
        hcm = (height/72.0)*2.54

        rangle = (pi/180.0) * angle

        self.cntnt.write('<draw:text-box draw:style-name="nofill" ')
        self.cntnt.write('draw:z-index="1" ')
        self.cntnt.write('draw:layer="layout" svg:width="%.3fcm" ' % wcm)
        self.cntnt.write('svg:height="%.3fpt" ' % hcm)
        self.cntnt.write('draw:transform="')
        self.cntnt.write('rotate (%.8f) ' % -rangle)
        xloc = x-((wcm/2.0)*cos(rangle))+((hcm/2.0)*sin(rangle))
        yloc = y-((hcm/2.0)*cos(rangle))-((wcm/2.0)*sin(rangle))
        self.cntnt.write('translate (%.3fcm %.3fcm)"' % (xloc,yloc))
        self.cntnt.write('>')
        self.cntnt.write('<text:p text:style-name="X%s">' % pname)

        self.cntnt.write('<text:span text:style-name="F%s">\n' % pname)
        self.write_text('\n'.join(text))
        self.cntnt.write('</text:span>\n</text:p>\n</draw:text-box>\n')
        
    def draw_path(self,style,path):
        minx = 9e12
        miny = 9e12
        maxx = 0
        maxy = 0

        for point in path:
            minx = min(point[0],minx)
            miny = min(point[1],miny)
            maxx = max(point[0],maxx)
            maxy = max(point[1],maxy)

        self.cntnt.write('<draw:polygon draw:style-name="%s" draw:layer="layout" ' % style)
        self.cntnt.write('draw:z-index="1" ')
        x = int((minx)*1000)
        y = int((miny)*1000)
        
        self.cntnt.write('svg:x="%d" svg:y="%d" ' % (x,y))
        self.cntnt.write('svg:viewBox="0 0 %d %d" ' % (int((maxx-minx)*1000),int((maxy-miny)*1000)))
        self.cntnt.write('svg:width="%.4fcm" ' % (maxx-minx))
        self.cntnt.write('svg:height="%.4fcm" ' % (maxy-miny))
        
        point = path[0]
        x1 = int((point[0]-minx)*1000)
        y1 = int((point[1]-miny)*1000)
        self.cntnt.write('draw:points="%d,%d' % (x1,y1))

        for point in path[1:]:
            x1 = int((point[0]-minx)*1000)
            y1 = int((point[1]-miny)*1000)
            self.cntnt.write(' %d,%d' % (x1,y1))
        self.cntnt.write('"/>\n')

    def draw_line(self,style,x1,y1,x2,y2):
        self.cntnt.write('<draw:line draw:style-name="%s" '% style)
        self.cntnt.write('svg:x1="%.3fcm" ' % x1)
        self.cntnt.write('svg:y1="%.3fcm" ' % y1)
        self.cntnt.write('svg:x2="%.3fcm" ' % x2)
        self.cntnt.write('svg:y2="%.3fcm" ' % y2)
        self.cntnt.write('/>\n')

    def draw_text(self,style,text,x,y):
        style_sheet = self.get_style_sheet()
        box_style = style_sheet.get_draw_style(style)
        para_name = box_style.get_paragraph_style()
        pstyle = style_sheet.get_paragraph_style(para_name)
        font = pstyle.get_font()
        sw = ReportUtils.pt2cm(FontScale.string_width(font,text))*1.3

        self.cntnt.write('<draw:text-box draw:style-name="%s" ' % style)
        self.cntnt.write('draw:layer="layout" ')
        # fix this
        self.cntnt.write('draw:z-index="0" ')
        self.cntnt.write('svg:width="%.3fcm" ' % sw)
        self.cntnt.write('svg:height="%.4fpt" ' % (font.get_size()*1.4))

        self.cntnt.write('svg:x="%.3fcm" ' % float(x))
        self.cntnt.write('svg:y="%.3fcm">' % float(y))
        self.cntnt.write('<text:p text:style-name="X%s">' % para_name)
        self.cntnt.write('<text:span text:style-name="F%s">' % para_name)
        self.cntnt.write(text)
        self.cntnt.write('</text:span></text:p>')
        self.cntnt.write('</draw:text-box>\n')

    def draw_box(self,style,text,x,y, w, h):
        style_sheet = self.get_style_sheet()
        box_style = style_sheet.get_draw_style(style)
        para_name = box_style.get_paragraph_style()
        shadow_width = box_style.get_shadow_space()

        if box_style.get_shadow():
            self.cntnt.write('<draw:rect text:anchor-type="paragraph" ')
            self.cntnt.write('draw:style-name="%s_shadow" ' % style)
            self.cntnt.write('draw:text-style-name="%s" ' % para_name)
            self.cntnt.write('draw:z-index="0" ')
            self.cntnt.write('svg:width="%.3fcm" ' % w)
            self.cntnt.write('svg:height="%.3fcm" ' % h)
            self.cntnt.write('svg:x="%.3fcm" ' % (float(x)+shadow_width))
            self.cntnt.write('svg:y="%.3fcm">\n' % (float(y)+shadow_width))
            self.cntnt.write('</draw:rect>\n')

        self.cntnt.write('<draw:rect text:anchor-type="paragraph" ')
        self.cntnt.write('draw:style-name="%s" ' % style)
        self.cntnt.write('draw:text-style-name="%s" ' % para_name)
        self.cntnt.write('draw:z-index="1" ')
        self.cntnt.write('svg:width="%.3fcm" ' % w)
        self.cntnt.write('svg:height="%.3fcm" ' % h)
        self.cntnt.write('svg:x="%.3fcm" ' % float(x))
        self.cntnt.write('svg:y="%.3fcm">\n' % float(y))
        if text != "":
            self.cntnt.write('<text:p text:style-name="%s">' % para_name)
            self.cntnt.write('<text:span text:style-name="F%s">' % para_name)
            text = text.replace('\t','<text:tab-stop/>')
            text = text.replace('\n','<text:line-break/>')
            self.cntnt.write(text)
            self.cntnt.write('</text:span>')
            self.cntnt.write('</text:p>\n')
        self.cntnt.write('</draw:rect>\n')

    def center_text(self,style,text,x,y):
        style_sheet = self.get_style_sheet()
        box_style = style_sheet.get_draw_style(style)
        para_name = box_style.get_paragraph_style()
        pstyle = style_sheet.get_paragraph_style(para_name)
        font = pstyle.get_font()

        size = (FontScale.string_width(font,text)/72.0) * 2.54

        self.cntnt.write('<draw:text-box text:anchor-type="paragraph" ')
        self.cntnt.write('draw:style-name="%s" ' % style)
        self.cntnt.write('draw:z-index="2" ')
        self.cntnt.write('svg:width="%.3fcm" ' % size)
        self.cntnt.write('svg:height="%.3fpt" ' % (font.get_size()*1.1))

        self.cntnt.write('svg:x="%.3fcm" ' % (x-(size/2.0)))
        self.cntnt.write('svg:y="%.3fcm">\n' % float(y))

        if text != "":
            self.cntnt.write('<text:p text:style-name="X%s">' % para_name)
            self.cntnt.write(text)
            self.cntnt.write('</text:p>\n')
        self.cntnt.write('</draw:text-box>\n')

#--------------------------------------------------------------------------
#
# Register plugins
#
#--------------------------------------------------------------------------
print_label = None
try:
    
    mprog = Mime.get_application(_apptype)
    mtype = Mime.get_description(_apptype)

    if Utils.search_for(mprog[0]):
        print_label = _("Open in OpenOffice.org")
    else:
        print_label = None

    register_text_doc(mtype,OpenOfficeDoc,1,1,1,".sxw",print_label)
    register_book_doc(mtype,OpenOfficeDoc,1,1,1,".sxw", print_label)
    register_draw_doc(mtype,OpenOfficeDoc,1,1,  ".sxw",print_label);
except:
    register_text_doc(_('OpenOffice.org Writer'),
                      OpenOfficeDoc,1,1,1,".sxw", None)
    register_book_doc(_("OpenOffice.org Writer"), OpenOfficeDoc,1,1,1,".sxw")
    register_draw_doc(_("OpenOffice.org Writer"),
                      OpenOfficeDoc,1,1,".sxw",None);
