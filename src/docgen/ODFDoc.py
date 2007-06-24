#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2005-2006  Serge Noiraud
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
import locale
from cStringIO import StringIO
from math import pi, cos, sin

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
# internationalization
#
#-------------------------------------------------------------------------
from gettext import gettext as _
from xml.sax.saxutils import escape

_apptype = 'application/vnd.oasis.opendocument.text'

_esc_map = {
    '\x1a'           : '',
    '\x0c'           : '',
    '\n'             : '<text:line-break/>',
    '\t'             : '<text:tab-stop/>',
    '&lt;super&gt;'  : '<text:span text:style-name="GSuper">',
    '&lt;/super&gt;' : '</text:span>',
    }

#-------------------------------------------------------------------------
#
# ODFDoc
#
#-------------------------------------------------------------------------
class ODFDoc(BaseDoc.BaseDoc):

    def __init__(self,styles,type,template,orientation=BaseDoc.PAPER_PORTRAIT):
        BaseDoc.BaseDoc.__init__(self,styles,type,template,orientation)
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

        if filename[-4:] != ".odt":
            self.filename = filename + ".odt"
        else:
            self.filename = filename

        self.filename = os.path.normpath(os.path.abspath(self.filename))
        self.cntnt = StringIO()

    def init(self):

        assert (not self.init_called)
        self.init_called = True
        
        current_locale = locale.getlocale()
        self.lang = current_locale[0]
        if self.lang:
            self.lang = self.lang.replace('_','-')
        else:
            self.lang = "en-US"

        self.cntnt.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.cntnt.write('<office:document-content ')
        self.cntnt.write('xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" ')
        self.cntnt.write('xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" ')
        self.cntnt.write('xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" ')
        self.cntnt.write('xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" ')
        self.cntnt.write('xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" ')
        self.cntnt.write('xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" ')
        self.cntnt.write('xmlns:xlink="http://www.w3.org/1999/xlink" ')
        self.cntnt.write('xmlns:dc="http://purl.org/dc/elements/1.1/" ')
        self.cntnt.write('xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" ')
        self.cntnt.write('xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" ')
        self.cntnt.write('xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" ')
        self.cntnt.write('xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" ')
        self.cntnt.write('xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" ')
        self.cntnt.write('xmlns:math="http://www.w3.org/1998/Math/MathML" ')
        self.cntnt.write('xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" ')
        self.cntnt.write('xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" ')
        self.cntnt.write('xmlns:dom="http://www.w3.org/2001/xml-events" ')
        self.cntnt.write('xmlns:xforms="http://www.w3.org/2002/xforms" ')
        self.cntnt.write('office:class="text" office:version="1.0">\n')
        self.cntnt.write('<office:scripts/>\n')
        self.cntnt.write('<office:font-face-decls>\n')
        self.cntnt.write('<style:font-face style:name="Courier" svg:font-family="Courier" ')
        self.cntnt.write('style:font-family-generic="modern" style:font-pitch="fixed"/>\n')
        self.cntnt.write('<style:font-face style:name="Times New Roman" ')
        self.cntnt.write('svg:font-family="&apos;Times New Roman&apos;" ')
        self.cntnt.write('style:font-family-generic="roman" ')
        self.cntnt.write('style:font-pitch="variable"/>\n')
        self.cntnt.write('<style:font-face style:name="Arial" ')
        self.cntnt.write('svg:font-family="Arial" ')
        self.cntnt.write('style:font-family-generic="swiss" ')
        self.cntnt.write('style:font-pitch="variable"/>\n')
        self.cntnt.write('</office:font-face-decls>\n')
        self.cntnt.write('<office:automatic-styles>\n')
        self.cntnt.write('<style:style style:name="docgen_page_break" style:family="paragraph" ')
        self.cntnt.write('style:parent-style-name="Standard">\n')
        self.cntnt.write('<style:paragraph-properties fo:break-before="page"/>\n')
        self.cntnt.write('</style:style>\n')
        self.cntnt.write('<style:style style:name="GSuper" style:family="text">')
        self.cntnt.write('<style:text-properties style:text-position="super 58%"/>')
        self.cntnt.write('</style:style>\n')
        self.cntnt.write('<style:style style:name="GRAMPS-preformat" style:family="text">')
        self.cntnt.write('<style:text-properties style:font-name="Courier"/>')
        self.cntnt.write('</style:style>\n')

        for style_name in self.draw_styles.keys():
            style = self.draw_styles[style_name]
            self.cntnt.write('<style:style style:name="%s"' % style_name)
            self.cntnt.write(' style:family="graphic"')
            self.cntnt.write(' >\n')
            self.cntnt.write('<style:graphic-properties ')
                
            if style.get_line_width():
                self.cntnt.write('svg:stroke-width="%.2f" ' % (style.get_line_width()*10))
                self.cntnt.write('draw:marker-start="" ')
                self.cntnt.write('draw:marker-start-width="0.0" ')
                self.cntnt.write('draw:marker-end-width="0.0" ')
                self.cntnt.write('draw:stroke="solid" ')
                self.cntnt.write('draw:textarea-horizontal-align="center" ')
                self.cntnt.write('draw:textarea-vertical-align="middle" ')
            else:
                self.cntnt.write('draw:stroke="none" ')
                self.cntnt.write('draw:stroke-color="#000000" ')

            if style.get_line_style() == BaseDoc.DASHED:
                self.cntnt.write('svg:fill-color="#cccccc" ')
            else:
                self.cntnt.write('svg:fill-color="#%02x%02x%02x" ' % style.get_color())
            self.cntnt.write('draw:fill-color="#%02x%02x%02x" ' % style.get_fill_color())
            self.cntnt.write('draw:shadow="hidden" ')
            self.cntnt.write('style:run-through="background" ')
            self.cntnt.write('style:vertical-pos="from-top" ')
            self.cntnt.write('style:vertical-rel="paragraph" ')
            self.cntnt.write('style:horizontal-pos="from-left" ')
            self.cntnt.write('style:horizontal-rel="paragraph" ')
            self.cntnt.write('draw:wrap-influence-on-position="once-concurrent" ')
            self.cntnt.write('style:flow-with-text="false" ')
            self.cntnt.write('/>\n')
            self.cntnt.write('</style:style>\n')

            self.cntnt.write('<style:style style:name="%s_shadow"' % style_name)
            self.cntnt.write(' style:family="graphic">\n')
            self.cntnt.write('<style:graphic-properties ')
            self.cntnt.write('draw:stroke="none" ')
            self.cntnt.write('draw:fill="solid" ')
            self.cntnt.write('draw:fill-color="#cccccc" ')
            self.cntnt.write('draw:textarea-horizontal-align="center" ')
            self.cntnt.write('draw:textarea-vertical-align="middle" ')
            self.cntnt.write('draw:shadow="hidden" ')
            self.cntnt.write('style:run-through="background" ')
            self.cntnt.write('style:vertical-pos="from-top" ')
            self.cntnt.write('style:vertical-rel="paragraph" ')
            self.cntnt.write('style:horizontal-pos="from-left" ')
            self.cntnt.write('style:horizontal-rel="paragraph" ')
            self.cntnt.write('draw:wrap-influence-on-position="once-concurrent" ')
            self.cntnt.write('style:flow-with-text="false" ')
            self.cntnt.write('/>\n')
            self.cntnt.write('</style:style>\n')

        # Graphic style for items with a clear background
        self.cntnt.write('<style:style style:name="clear" ')
        self.cntnt.write('style:family="graphic">\n')
        self.cntnt.write('\t<style:graphic-properties draw:stroke="none" ')
        self.cntnt.write('draw:fill="none" draw:shadow="hidden" ')
        self.cntnt.write('style:run-through="background" ')
        self.cntnt.write('style:vertical-pos="from-top" ')
        self.cntnt.write('style:vertical-rel="paragraph" ')
        self.cntnt.write('style:horizontal-pos="from-left" ')
        self.cntnt.write('style:horizontal-rel="paragraph" ')
        self.cntnt.write('draw:wrap-influence-on-position="once-concurrent" ')
        self.cntnt.write('style:flow-with-text="false"/>')
        self.cntnt.write('</style:style>\n')
        
        for style_name in self.style_list.keys():
            style = self.style_list[style_name]

            self.cntnt.write('<style:style style:name="NL%s" ' % style_name)
            self.cntnt.write('style:family="paragraph" ')
            self.cntnt.write('style:parent-style-name="%s">\n' % style_name)
            self.cntnt.write('<style:paragraph-properties fo:break-before="page"/>\n')
            self.cntnt.write('</style:style>\n')

            self.cntnt.write('<style:style style:name="X%s" ' % style_name)
            self.cntnt.write('style:family="paragraph"')
            self.cntnt.write('>\n')
            self.cntnt.write('<style:paragraph-properties ')

            if style.get_padding() != 0.0:
               self.cntnt.write('fo:padding="%.2fcm" ' % style.get_padding())
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
            self.cntnt.write('fo:font-size="%.2fpt" ' % font.get_size())
            self.cntnt.write('style:font-size-asian="%.2fpt" ' % font.get_size())
            color = font.get_color()
            self.cntnt.write('fo:color="#%02x%02x%02x" ' % color)
            if font.get_bold():
                self.cntnt.write('fo:font-weight="bold" ')
            if font.get_italic():
                self.cntnt.write('fo:font-style="italic" ')
            if font.get_underline():
                self.cntnt.write('style:text-underline="single" ')
                self.cntnt.write('style:text-underline-color="font-color" ')
            self.cntnt.write('fo:text-indent="%.2fcm"\n' % style.get_first_indent())
            self.cntnt.write('fo:margin-right="%.2fcm"\n' % style.get_right_margin())
            self.cntnt.write('fo:margin-left="%.2fcm"\n' % style.get_left_margin())
            self.cntnt.write('fo:margin-top="0.00cm"\n')
            self.cntnt.write('fo:margin-bottom="0.212cm" ')
            self.cntnt.write('/>\n')
            self.cntnt.write('</style:style>\n')

            self.cntnt.write('<style:style style:name="F%s" ' % style_name)
            self.cntnt.write('style:family="text">\n')
            self.cntnt.write('<style:text-properties ')
            align = style.get_alignment()
            if align == BaseDoc.PARA_ALIGN_LEFT:
               self.cntnt.write('fo:text-align="start" ')
            elif align == BaseDoc.PARA_ALIGN_RIGHT:
               self.cntnt.write('fo:text-align="end" ')
            elif align == BaseDoc.PARA_ALIGN_CENTER:
               self.cntnt.write('fo:text-align="center" ')
               self.cntnt.write('style:justify-single-word="false" ')
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
            self.cntnt.write('fo:font-size="%.2fpt" ' % font.get_size())
            self.cntnt.write('style:font-size-asian="%.2fpt"/> ' % font.get_size())
            self.cntnt.write('</style:style>\n')

        for style_name in self.table_styles.keys():
            style = self.table_styles[style_name]
            self.cntnt.write('<style:style style:name="%s" ' % style_name)
            self.cntnt.write('style:family="table-properties">\n')
            table_width = float(self.get_usable_width())
            table_width_str = "%.2f" % table_width
            self.cntnt.write('<style:table-properties-properties style:width="%scm" '%table_width_str)
            self.cntnt.write('/>\n')
            self.cntnt.write('</style:style>\n')
            for col in range(0,style.get_columns()):
                self.cntnt.write('<style:style style:name="')
                self.cntnt.write(style_name + '.' + str(chr(ord('A')+col)) +'" ')
                self.cntnt.write('style:family="table-column">')
                width = table_width * float(style.get_column_width(col)/100.0)
                width_str = "%.4f" % width
                self.cntnt.write('<style:table-column-properties ')
                self.cntnt.write('style:column-width="%scm"/>' % width_str)
                self.cntnt.write('</style:style>\n')
                
        for cell in self.cell_styles.keys():
            cell_style = self.cell_styles[cell]
            self.cntnt.write('<style:style style:name="%s" ' % cell)
            self.cntnt.write('style:family="table-cell">\n')
            self.cntnt.write('<style:table-cell-properties')
            self.cntnt.write(' fo:padding="%.2fcm"' % cell_style.get_padding())
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
            
        self.cntnt.write('<style:style style:name="Tbold" style:family="text">\n')
        self.cntnt.write('<style:text-properties fo:font-weight="bold"/>\n')
        self.cntnt.write('</style:style>\n')

        #Begin photo style
        self.cntnt.write('<style:style style:name="Left" style:family="graphic"')
        self.cntnt.write(' style:parent-style-name="photo">')
        self.cntnt.write('<style:graphic-properties style:run-through="foreground"')
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

        self.cntnt.write('<style:style style:name="Right" style:family="graphic"')
        self.cntnt.write(' style:parent-style-name="photo">')
        self.cntnt.write('<style:graphic-properties style:run-through="foreground"')
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

        self.cntnt.write('<style:style style:name="Single" style:family="graphic"')
        self.cntnt.write(' style:parent-style-name="Graphics"> ')
        self.cntnt.write('<style:graphic-properties style:vertical-pos="from-top"')
        self.cntnt.write(' style:mirror="none" fo:clip="rect(0cm 0cm 0cm 0cm)"')
        self.cntnt.write(' draw:luminance="0%" draw:contrast="0" draw:red="0%"')
        self.cntnt.write(' draw:green="0%" draw:blue="0%" draw:gamma="1"')
        self.cntnt.write(' draw:color-inversion="false" draw:transparency="-100%"')
        self.cntnt.write(' draw:color-mode="standard"/> ')
        self.cntnt.write('</style:style>\n')

        self.cntnt.write('<style:style style:name="Row" style:family="graphic"')
        self.cntnt.write(' style:parent-style-name="Graphics">')
        self.cntnt.write('<style:graphic-properties style:vertical-pos="from-top"')
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
        self.cntnt.write(' <office:text>\n')
        self.cntnt.write(' <office:forms ')
        self.cntnt.write('form:automatic-focus="false" ')
        self.cntnt.write('form:apply-design-mode="false"/>\n')

    def close(self):
        self.cntnt.write('</office:text>\n')
        self.cntnt.write('</office:body>\n')
        self.cntnt.write('</office:document-content>\n')
        self._write_styles_file()
        self._write_manifest()
        self._write_meta_file()
        self._write_mimetype_file()
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
            self.cntnt.write('<draw:frame draw:style-name="Left" ')
        elif pos == "right":
            self.cntnt.write('<draw:frame draw:style-name="Right" ')
        elif pos == "single":
            self.cntnt.write('<draw:frame draw:style-name="Single" ')
        else:
            self.cntnt.write('<draw:frame draw:style-name="Row" ')

        self.cntnt.write('draw:name="%s" ' % tag)
        self.cntnt.write('text:anchor-type="paragraph" ')
        self.cntnt.write('svg:width="%.2fcm" ' % act_width)
        self.cntnt.write('svg:height="%.2fcm" ' % act_height)
        self.cntnt.write('draw:z-index="1" >')
        self.cntnt.write('<draw:image xlink:href="Pictures/')
        self.cntnt.write(base)
        self.cntnt.write('" xlink:type="simple" xlink:show="embed" ')
        self.cntnt.write('xlink:actuate="onLoad"/>\n')
        self.cntnt.write('</draw:frame>\n')
        if self.new_cell:
            self.cntnt.write('</text:p>\n')

    def start_table(self,name,style_name):
        self.cntnt.write('<table:table table:name="%s" ' % name)
        self.cntnt.write('table:style-name="%s">\n' % style_name)
        table = self.table_styles[style_name]
        for col in range(0,table.get_columns()):
            self.cntnt.write('<table:table-column table:style-name="')
            self.cntnt.write(style_name + '.' + str(chr(ord('A')+col)) +'"/>\n')

    def end_table(self):
        self.cntnt.write('</table:table>\n')

    def start_row(self):
        self.cntnt.write('<table:table-row>\n')

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
        #for col in range(1,self.span):
        #    self.cntnt.write('<table:covered-table-cell/>\n')
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
        self._add_zip(zfile,"mimetype",self.mimetype.getvalue(),t)

        self.mfile.close()
        self.cntnt.close()
        self.meta.close()
        self.sfile.close()
        self.mimetype.close()
        
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
                                     
        self.sfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.sfile.write('<office:document-styles ')
        self.sfile.write('xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" ')
        self.sfile.write('xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" ')
        self.sfile.write('xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" ')
        self.sfile.write('xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" ')
        self.sfile.write('xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" ')
        self.sfile.write('xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" ')
        self.sfile.write('xmlns:xlink="http://www.w3.org/1999/xlink" ')
        self.sfile.write('xmlns:dc="http://purl.org/dc/elements/1.1/" ')
        self.sfile.write('xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" ')
        self.sfile.write('xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" ')
        self.sfile.write('xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" ')
        self.sfile.write('xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" ')
        self.sfile.write('xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" ')
        self.sfile.write('xmlns:math="http://www.w3.org/1998/Math/MathML" ')
        self.sfile.write('xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" ')
        self.sfile.write('xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" ')
        self.sfile.write('office:version="1.0">\n')
        self.sfile.write('<office:font-face-decls>\n')
        self.sfile.write('<style:font-face style:name="Times New Roman"')
        self.sfile.write(' svg:font-family="&apos;Times New Roman&apos;"')
        self.sfile.write(' style:font-family-generic="roman"')
        self.sfile.write(' style:font-pitch="variable"/>\n')
        self.sfile.write('<style:font-face style:name="Arial"')
        self.sfile.write(' svg:font-family="Arial"')
        self.sfile.write(' style:font-family-generic="swiss"')
        self.sfile.write(' style:font-pitch="variable"/>\n')
        self.sfile.write('</office:font-face-decls>\n')
        self.sfile.write('<office:styles>\n')
        self.sfile.write('<style:default-style ')
        self.sfile.write(' style:family="graphic">\n')
        self.sfile.write('<style:graphic-properties ')
        self.sfile.write(' draw:shadow-offset-x="0.3cm"') 
        self.sfile.write(' draw:shadow-offset-y="0.3cm" ')
        self.sfile.write(' draw:start-line-spacing-horizontal="0.283cm" ')
        self.sfile.write(' draw:start-line-spacing-vertical="0.283cm" ')
        self.sfile.write(' draw:end-line-spacing-horizontal="0.283cm" ')
        self.sfile.write(' draw:end-line-spacing-vertical="0.283cm" ')
        self.sfile.write(' style:flow-with-text="true"/>')
        self.sfile.write('<style:paragraph-properties ')
        self.sfile.write(' style:text-autospace="ideograph-alpha" ')
        self.sfile.write(' style:line-break="strict" ')
        self.sfile.write(' style:writing-mode="lr-tb" ')
        self.sfile.write(' style:font-independent-line-spacing="false">')
        self.sfile.write(' <style:tab-stops/>')
        self.sfile.write(' </style:paragraph-properties>')
        self.sfile.write('<style:text-properties ')
        self.sfile.write(' style:use-window-font-color="true" ')
        self.sfile.write(' fo:font-size="12pt" ')
        self.sfile.write(' style:font-size-asian="12pt" ')
        self.sfile.write(' style:language-asian="none" ')
        self.sfile.write(' style:country-asian="none" ')
        self.sfile.write(' style:font-size-complex="12pt" ')
        self.sfile.write(' style:language-complex="none" ')
        self.sfile.write(' style:country-complex="none"/>')
        self.sfile.write('</style:default-style>\n')
        self.sfile.write('<style:default-style ')
        self.sfile.write(' style:family="paragraph">\n')
        self.sfile.write(' <style:paragraph-properties\n')
        self.sfile.write(' style:text-autospace="ideograph-alpha"\n')
        self.sfile.write(' style:punctuation-wrap="hanging"\n')
        self.sfile.write(' style:line-break="strict"\n')
        self.sfile.write(' style:tab-stop-distance="2.205cm"\n')
        self.sfile.write(' style:writing-mode="page"/>\n')
        self.sfile.write('<style:text-properties \n')
        self.sfile.write('style:font-name="Times New Roman" ')
        self.sfile.write('fo:font-size="12pt" ')
        self.sfile.write('style:font-name-asian="Times New Roman" ')
        self.sfile.write('style:font-size-asian="12pt" ')
        self.sfile.write('style:font-name-complex="Times New Roman" ')
        self.sfile.write('style:font-size-complex="12pt" ')
        self.sfile.write('style:tab-stop-distance="2.205cm"/>\n')
        self.sfile.write('</style:default-style>\n')
        self.sfile.write('<style:default-style ')
        self.sfile.write(' style:family="table"> ')
        self.sfile.write(' <style:table-properties ')
        self.sfile.write('  table:border-model="separating"/> ')
        self.sfile.write('</style:default-style>\n')
        self.sfile.write('<style:default-style ')
        self.sfile.write(' style:family="table-row"> ')
        self.sfile.write(' <style:table-row-properties ')
        self.sfile.write('  fo:keep-together="auto"/> ')
        self.sfile.write('</style:default-style>\n')
        self.sfile.write('<style:style style:name="Standard" ')
        self.sfile.write('style:family="paragraph" style:class="text"/>\n')
        self.sfile.write('<style:style style:name="photo" style:family="graphic">\n')
        self.sfile.write('<style:graphic-properties text:anchor-type="paragraph" ')
        self.sfile.write('svg:x="0cm" svg:y="0cm" style:wrap="none" ')
        self.sfile.write('style:vertical-pos="top" ')
        self.sfile.write('style:vertical-rel="paragraph-content" ')
        self.sfile.write('style:horizontal-pos="center" ')
        self.sfile.write('style:horizontal-rel="paragraph-content"/>\n')
        self.sfile.write('</style:style>\n')
        
        for key in self.style_list.keys():
            style = self.style_list[key]
            self.sfile.write('<style:style style:name="%s" ' % key)
            self.sfile.write('style:family="paragraph" ')
            self.sfile.write('style:parent-style-name="Standard" ')
            self.sfile.write('style:class="text">\n')
            self.sfile.write('<style:paragraph-properties\n')
            self.sfile.write('fo:margin-left="%.2fcm"\n' % style.get_left_margin())
            self.sfile.write('fo:margin-right="%.2fcm"\n' % style.get_right_margin())
            self.sfile.write('fo:margin-top="0.00cm"\n')
            self.sfile.write('fo:margin-bottom="0.212cm"\n')

            if style.get_padding() != 0.0:
               self.sfile.write('fo:padding="%.2fcm" ' % style.get_padding())
            if style.get_header_level() > 0:
                self.sfile.write('fo:keep-with-next="always" ')

            align = style.get_alignment()
            if align == BaseDoc.PARA_ALIGN_LEFT:
               self.sfile.write('fo:text-align="start" ')
               self.sfile.write('style:justify-single-word="false" ')
            elif align == BaseDoc.PARA_ALIGN_RIGHT:
               self.sfile.write('fo:text-align="end" ')
            elif align == BaseDoc.PARA_ALIGN_CENTER:
               self.sfile.write('fo:text-align="center" ')
               self.sfile.write('style:justify-single-word="false" ')
            else:
               self.sfile.write('fo:text-align="justify" ')
               self.sfile.write('style:justify-single-word="false" ')
            self.sfile.write('fo:text-indent="%.2fcm" ' % style.get_first_indent())
            self.sfile.write('style:auto-text-indent="false"/> ')
            self.sfile.write('<style:text-properties ')
            font = style.get_font()
            color = font.get_color()
            self.sfile.write('fo:color="#%02x%02x%02x" ' % color)
            if font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
                self.sfile.write('style:font-name="Arial" ')
            else:
                self.sfile.write('style:font-name="Times New Roman" ')
            self.sfile.write('fo:font-size="%.0fpt" ' % font.get_size())
            if font.get_italic():
                self.sfile.write('fo:font-style="italic" ')
            if font.get_bold():
                self.sfile.write('fo:font-weight="bold" ')
            if font.get_underline():
                self.sfile.write('style:text-underline="single" ')
                self.sfile.write('style:text-underline-color="font-color" ')
                self.sfile.write('fo:text-indent="%.2fcm" ' % style.get_first_indent())
                self.sfile.write('fo:margin-right="%.2fcm" ' % style.get_right_margin())
                self.sfile.write('fo:margin-left="%.2fcm" ' % style.get_left_margin())
                self.sfile.write('fo:margin-top="0cm" ')
                self.sfile.write('fo:margin-bottom="0.212cm"')
            self.sfile.write('/>\n')
            self.sfile.write('</style:style>\n')

        # Current no leading number format for headers

        #self.sfile.write('<text:outline-style>\n')
        #self.sfile.write('<text:outline-level-style text:level="1" style:num-format=""/>\n')
        #self.sfile.write('<text:outline-level-style text:level="2" style:num-format=""/>\n')
        #self.sfile.write('<text:outline-level-style text:level="3" style:num-format=""/>\n')
        #self.sfile.write('<text:outline-level-style text:level="4" style:num-format=""/>\n')
        #self.sfile.write('<text:outline-level-style text:level="5" style:num-format=""/>\n')
        #self.sfile.write('<text:outline-level-style text:level="6" style:num-format=""/>\n')
        #self.sfile.write('<text:outline-level-style text:level="7" style:num-format=""/>\n')
        #self.sfile.write('<text:outline-level-style text:level="8" style:num-format=""/>\n')
        #self.sfile.write('<text:outline-level-style text:level="9" style:num-format=""/>\n')
        #self.sfile.write('<text:outline-level-style text:level="10" style:num-format=""/>\n')
        #self.sfile.write('</text:outline-style>\n')
            
        self.sfile.write('<text:notes-configuration  ')
        self.sfile.write('text:note-class="footnote"  ')
        self.sfile.write('style:num-format="1"  ')
        self.sfile.write('text:start-value="0"  ')
        self.sfile.write('text:footnotes-position="page"  ')
        self.sfile.write('text:start-numbering-at="document"/> ')
        self.sfile.write('<text:notes-configuration  ')
        self.sfile.write('text:note-class="endnote"  ')
        self.sfile.write('style:num-format="i"  ')
        self.sfile.write('text:start-value="0"/> ')
        self.sfile.write('<text:linenumbering-configuration  ')
        self.sfile.write('text:number-lines="false"  ')
        self.sfile.write('text:offset="0.499cm"  ')
        self.sfile.write('style:num-format="1"  ')
        self.sfile.write('text:number-position="left"  ')
        self.sfile.write('text:increment="5"/> ')
        self.sfile.write('</office:styles>\n')
        self.sfile.write('<office:automatic-styles>\n')
        self.sfile.write('<style:style style:name="S-Header" style:family="paragraph" ')
        self.sfile.write('style:parent-style-name="Standard">')
        self.sfile.write('<style:paragraph-properties fo:text-align="center" ')
        self.sfile.write('style:justify-single-word="false"/>')
        self.sfile.write('</style:style>\n')
        self.sfile.write('<style:style style:name="S-Footer" style:family="paragraph" ')
        self.sfile.write('style:parent-style-name="Header">')
        self.sfile.write('<style:paragraph-properties fo:text-align="center" ')
        self.sfile.write('style:justify-single-word="false"/>')
        self.sfile.write('</style:style>\n')
        self.sfile.write('<style:page-layout style:name="pm1">\n')
        self.sfile.write('<style:page-layout-properties fo:page-width="%.2fcm" ' % self.width)
        self.sfile.write('fo:page-height="%.2fcm" ' % self.height)
        self.sfile.write('style:num-format="1" ')
        if self.orientation == BaseDoc.PAPER_PORTRAIT:
            self.sfile.write('style:print-orientation="portrait" ')
        else:
            self.sfile.write('style:print-orientation="landscape" ')
        self.sfile.write('fo:margin-top="%.2fcm" ' % self.tmargin)
        self.sfile.write('fo:margin-bottom="%.2fcm" ' % self.bmargin)
        self.sfile.write('fo:margin-left="%.2fcm" ' % self.lmargin)
        self.sfile.write('fo:margin-right="%.2fcm" ' % self.rmargin)
        self.sfile.write('style:writing-mode="lr-tb" ')
        self.sfile.write('style:footnote-max-height="0cm">\n')
        self.sfile.write('<style:footnote-sep style:width="0.018cm" ')
        self.sfile.write('style:distance-before-sep="0.101cm" ')
        self.sfile.write('style:distance-after-sep="0.101cm" ')
        self.sfile.write('style:adjustment="left" style:rel-width="25%" ')
        self.sfile.write('style:color="#000000"/>\n')
        self.sfile.write('</style:page-layout-properties>\n')
        # header
        self.sfile.write('<style:header-style>\n')
        self.sfile.write('<style:header-footer-properties ')
        self.sfile.write('fo:min-height="0cm" fo:margin-bottom="0.499cm"/>\n')
        self.sfile.write('</style:header-style>\n')
        # footer
        self.sfile.write('<style:footer-style>\n')
        self.sfile.write('<style:header-footer-properties ')
        self.sfile.write('fo:min-height="0cm" fo:margin-bottom="0.499cm"/>\n')
        self.sfile.write('</style:footer-style>\n')
        #
        self.sfile.write('</style:page-layout>\n')
        self.sfile.write('</office:automatic-styles>\n')
        self.sfile.write('<office:master-styles>\n')
        self.sfile.write('<style:master-page style:name="Standard" ')
        self.sfile.write('style:page-layout-name="pm1">\n')
        # header
        #self.sfile.write('<style:header>')
        #self.sfile.write('<text:p text:style-name="S-Header">')
        #self.sfile.write(' TITRE : %s' % self.title) # How to get the document title here ?
        #self.sfile.write('</text:p>')
        #self.sfile.write('</style:header>')
        # footer
        #self.sfile.write('<style:footer>')
        #self.sfile.write('<text:p text:style-name="S-Footer">')
        #self.sfile.write('<text:page-number text:select-page="current">1')
        #self.sfile.write('</text:page-number>/')
        #self.sfile.write('<text:page-count>1')
        #self.sfile.write('</text:page-count>')
        #self.sfile.write('</text:p>')
        #self.sfile.write('</style:footer>')
        #
        self.sfile.write('</style:master-page>')
        self.sfile.write('</office:master-styles>\n')
        self.sfile.write('</office:document-styles>\n')

    def page_break(self):
        self.new_page = 1

    def start_page(self):
        self.cntnt.write('<text:p text:style-name="docgen_page_break">\n')

    def end_page(self):
        self.cntnt.write('</text:p>\n')
        
    def start_paragraph(self,style_name,leader=None):
        style = self.style_list[style_name]
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
            self.cntnt.write('" text:outline-level="' + str(self.level) + '">')
        if leader != None:
            self.cntnt.write(escape(leader))
            self.cntnt.write('<text:tab/>')
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
        self.mfile.write('xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">')
        self.mfile.write('<manifest:file-entry ')
        self.mfile.write('manifest:media-type="%s" ' % _apptype)
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

    def _write_mimetype_file(self):
        self.mimetype = StringIO()
        self.mimetype.write('application/vnd.oasis.opendocument.text')

    def _write_meta_file(self):
        self.meta = StringIO()

        self.meta.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.meta.write('<office:document-meta ')
        self.meta.write('xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" ')
        self.meta.write('xmlns:xlink="http://www.w3.org/1999/xlink" ')
        self.meta.write('xmlns:dc="http://purl.org/dc/elements/1.1/" ')
        self.meta.write('xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" ')
        self.meta.write('office:version="1.0">\n');
        self.meta.write('<office:meta>\n')
        self.meta.write('<meta:generator>')
        self.meta.write(const.program_name + ' ' + const.version)
        self.meta.write('</meta:generator>\n')
        self.meta.write('<dc:title>')
        # It should be reasonable to have a true document title. but how ?
        # self.title ?
        #self.meta.write(_("Summary of %s") % self.name)
        self.meta.write('</dc:title>\n')
        self.meta.write('<dc:subject>')
        #self.meta.write(_("Summary of %s") % name)
        self.meta.write('</dc:subject>\n')
        self.meta.write('<dc:description>')
        self.meta.write('</dc:description>\n')
        self.meta.write('<meta:initial-creator>')
        self.meta.write(self.name)
        self.meta.write('</meta:initial-creator>\n')
        self.meta.write('<meta:creation-date>')
        self.meta.write(self.time)
        self.meta.write('</meta:creation-date>\n')
        self.meta.write('<dc:creator>')
        self.meta.write(self.name)
        self.meta.write('</dc:creator>\n')
        self.meta.write('<dc:date>')
        self.meta.write(self.time)
        self.meta.write('</dc:date>\n')
        self.meta.write('<dc:keyword>')
        self.meta.write('</dc:keyword>\n')
        self.meta.write('<meta:print-date>0-00-00T00:00:00</meta:print-date>\n')
        self.meta.write('<dc:language>%s</dc:language>\n' % self.lang)
        self.meta.write('<meta:editing-cycles>1</meta:editing-cycles>\n')
        self.meta.write('<meta:editing-duration>PT0S</meta:editing-duration>\n')
        self.meta.write('<meta:user-defined meta:name="Genealogical Research and Analysis Management Programming System">http://gramps-project.org')
        self.meta.write('</meta:user-defined>\n')
        self.meta.write('<meta:user-defined meta:name="Info 1"/>\n')
        self.meta.write('<meta:user-defined meta:name="Info 2"/>\n')
        self.meta.write('<meta:user-defined meta:name="Info 3"/>\n')
        self.meta.write('</office:meta>\n')
        self.meta.write('</office:document-meta>\n')

    def rotate_text(self,style,text,x,y,angle):

        stype = self.draw_styles[style]
        pname = stype.get_paragraph_style()
        p = self.style_list[pname]
        font = p.get_font()
        size = font.get_size()

        height = size*(len(text))
        width = 0
        for line in text:
            width = max(width,FontScale.string_width(font,line))
        wcm = ReportUtils.pt2cm(width)
        hcm = ReportUtils.pt2cm(height)

        rangle = (pi/180.0) * angle

        self.cntnt.write('<draw:frame text:anchor-type="paragraph" ')
        self.cntnt.write('draw:z-index="2" ')
        self.cntnt.write('draw:style-name="clear" ')
        self.cntnt.write('svg:height="%.2fcm" ' % hcm)
        self.cntnt.write('svg:width="%.2fcm" ' % wcm)
        self.cntnt.write('draw:transform="')
        self.cntnt.write('rotate (%.8f) ' % -rangle)
        xloc = x-((wcm/2.0)*cos(rangle))+((hcm/2.0)*sin(rangle))
        yloc = y-((hcm/2.0)*cos(rangle))-((wcm/2.0)*sin(rangle))
        self.cntnt.write('translate (%.3fcm %.3fcm)"' % (xloc,yloc))
        self.cntnt.write('>')
        self.cntnt.write('<draw:text-box>')
        self.cntnt.write('<text:p text:style-name="X%s"> ' % pname)

        self.cntnt.write('<text:span text:style-name="F%s">\n' % pname)
        self.write_text('\n'.join(text))    # No escape(): write_text does that.
        self.cntnt.write('</text:span>\n</text:p>\n</draw:text-box>\n')
        self.cntnt.write('</draw:frame>\n')
        
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
        self.cntnt.write('<draw:line text:anchor-type="paragraph" ')
        self.cntnt.write('draw:z-index="3" ')
        self.cntnt.write('draw:text-style-name="%s" ' % style )
        self.cntnt.write('svg:x1="%.2fcm" ' % x1)
        self.cntnt.write('svg:y1="%.2fcm" ' % y1)
        self.cntnt.write('svg:x2="%.2fcm" ' % x2)
        self.cntnt.write('svg:y2="%.2fcm">' % y2)
        self.cntnt.write('<text:p/>\n')
        self.cntnt.write('</draw:line>\n')

    def draw_text(self,style,text,x,y):
        box_style = self.draw_styles[style]
        para_name = box_style.get_paragraph_style()

        pstyle = self.style_list[para_name]
        font = pstyle.get_font()
        if box_style.get_width():
            sw = box_style.get_width()*1.2
        else:
            sw = ReportUtils.pt2cm(FontScale.string_width(font,text))*1.3

        self.cntnt.write('<draw:frame text:anchor-type="paragraph" ')
        self.cntnt.write('draw:z-index="2" ')
        self.cntnt.write('draw:style-name="%s" ' % style)
        self.cntnt.write('svg:width="%.2fcm" ' % sw)
        self.cntnt.write('svg:height="%.2fcm" ' %
                         (ReportUtils.pt2cm(font.get_size()*1.4)))

        self.cntnt.write('svg:x="%.2fcm" ' % float(x))
        self.cntnt.write('svg:y="%.2fcm">' % float(y))
        self.cntnt.write('<draw:text-box> ' )
        self.cntnt.write('<text:p text:style-name="F%s">' % para_name)
        self.cntnt.write('<text:span text:style-name="F%s"' % para_name)
        self.cntnt.write(' fo:max-height="%.2f">' % font.get_size() )
        self.cntnt.write(escape(text,_esc_map))
        self.cntnt.write('</text:span></text:p>')
        self.cntnt.write('</draw:text-box>\n')
        self.cntnt.write('</draw:frame>\n')

    def draw_bar(self,style,x,y,x2,y2):
        box_style = self.draw_styles[style]

        self.cntnt.write('<draw:rect text:anchor-type="paragraph" draw:style-name="')
        self.cntnt.write(style)
        self.cntnt.write('" draw:z-index="0" ')
        self.cntnt.write('svg:width="%.2fcm" ' % float(x2-x))
        self.cntnt.write('svg:height="%.2fcm" ' % float(y2-y))
        self.cntnt.write('svg:x="%.2fcm" ' % float(x))
        self.cntnt.write('svg:y="%.2fcm">' % float(y))
        self.cntnt.write('</draw:rect>\n')

    def draw_box(self,style,text,x,y):
        box_style = self.draw_styles[style]
        para_name = box_style.get_paragraph_style()
        shadow_width = box_style.get_shadow_space()

        if box_style.get_shadow():
            self.cntnt.write('<draw:rect text:anchor-type="paragraph" ')
            self.cntnt.write('draw:style-name="%s_shadow" ' % style)
            self.cntnt.write('draw:z-index="0" ')
            self.cntnt.write('draw:text-style-name="%s" ' % para_name)
            self.cntnt.write('svg:width="%.2fcm" ' % box_style.get_width())
            self.cntnt.write('svg:height="%.2fcm" ' % box_style.get_height())
            self.cntnt.write('svg:x="%.2fcm" ' % (float(x)+shadow_width))
            self.cntnt.write('svg:y="%.2fcm">\n' % (float(y)+shadow_width))
            self.cntnt.write('</draw:rect>\n')

        self.cntnt.write('<draw:rect text:anchor-type="paragraph" ')
        self.cntnt.write('draw:style-name="%s" ' % style)
        self.cntnt.write('draw:text-style-name="%s" ' % para_name)
        self.cntnt.write('draw:z-index="1" ')
        self.cntnt.write('svg:width="%.2fcm" ' % box_style.get_width())
        self.cntnt.write('svg:height="%.2fcm" ' % box_style.get_height())
        self.cntnt.write('svg:x="%.2fcm" ' % float(x))
        self.cntnt.write('svg:y="%.2fcm">\n' % float(y))
        if text != "":
            self.cntnt.write('<text:p text:style-name="%s">' % para_name)
            self.cntnt.write('<text:span text:style-name="F%s">' % para_name)
            self.cntnt.write(escape(text,_esc_map))
            self.cntnt.write('</text:span>')
            self.cntnt.write('</text:p>\n')
        self.cntnt.write('</draw:rect>\n')

    def center_text(self,style,text,x,y):
        box_style = self.draw_styles[style]
        para_name = box_style.get_paragraph_style()
        pstyle = self.style_list[para_name]
        font = pstyle.get_font()

        size = 1.2*(FontScale.string_width(font,text)/72.0) * 2.54

        self.cntnt.write('<draw:frame text:anchor-type="paragraph" ')
        self.cntnt.write('draw:style-name="%s" ' % style)
        self.cntnt.write('draw:z-index="0" ')
        self.cntnt.write('svg:width="%.2fcm" ' % size)
        self.cntnt.write('svg:height="%.2fpt" ' % font.get_size())

        self.cntnt.write('svg:x="%.2fcm" ' % (x-(size/2.0)))
        self.cntnt.write('svg:y="%.2fcm">\n' % float(y))

        if text != "":
            self.cntnt.write('<draw:text-box>')
            self.cntnt.write('<text:p text:style-name="X%s">' % para_name)
            self.cntnt.write('<text:span text:style-name="F%s">' % para_name)
            self.cntnt.write(escape(text,_esc_map))
            self.cntnt.write('</text:span>\n')
            self.cntnt.write('</text:p>\n')
            self.cntnt.write('</draw:text-box>')
        self.cntnt.write('</draw:frame>\n')

#--------------------------------------------------------------------------
#
# Register plugins
#
#--------------------------------------------------------------------------
print_label = None
try:
    mprog = Mime.get_application(_apptype)

    if Utils.search_for(mprog[0]):
        print_label = _("Open in %(program_name)s") % { 'program_name':
                                                        mprog[1]}
    else:
        print_label = None
except:
    print_label = None

register_text_doc(_('Open Document Text'), ODFDoc, 1, 1, 1, ".odt", print_label)
register_book_doc(_("Open Document Text"), ODFDoc, 1, 1, 1, ".odt", print_label)
register_draw_doc(_("Open Document Text"), ODFDoc, 1, 1, ".odt", print_label);
