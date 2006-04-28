#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
import zipfile
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
import BaseDoc
from SpreadSheetDoc import *

import const

import Errors

#-------------------------------------------------------------------------
#
# OpenSpreadSheet
#
#-------------------------------------------------------------------------
class OpenSpreadSheet(SpreadSheetDoc):

    def __init__(self,type,orientation):
        SpreadSheetDoc.__init__(self,type,orientation)
        self.f = None
        self.filename = None
        self.level = 0
        self.time = "0000-00-00T00:00:00"

    def open(self,filename):
        import time
        
        t = time.localtime(time.time())
        self.time = "%04d-%02d-%02dT%02d:%02d:%02d" % \
                    (t[0],t[1],t[2],t[3],t[4],t[5])

        if filename[-4:] != ".sxc":
            self.filename = filename + ".sxc"
        else:
            self.filename = filename

        try:
            self.content_xml = tempfile.mktemp()
            self.f = open(self.content_xml,"wb")
        except IOError,msg:
            raise Errors.ReportError(_("Could not create %s") % self.content_xml, msg)
        except:
            raise Errors.ReportError(_("Could not create %s") % self.content_xml)

        self.f = open(self.content_xml,"w")
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
        self.f.write('office:class="spreadsheet" office:version="0.9">\n')
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
	for key in self.table_styles.keys():
	    table = self.table_styles[key]
  	    self.f.write('<style:style style:name="')
   	    self.f.write(key)
	    self.f.write('" style:family="table">\n')
	    self.f.write('<style:properties table:display="true" ')
	    self.f.write('table:page-style-name="Default"/>\n')
	    self.f.write('</style:style>\n')
            for index in range(0,table.get_columns()):
                self.f.write('<style:style style:name="')
	        self.f.write(key + '_' + str(index))
                self.f.write('" style:family="table-column">\n')
	        self.f.write('<style:properties fo:break-before="auto" ')
      	        self.f.write('style:column-width="%.3fcm"/>\n' % table.get_column_width(index))
	        self.f.write('</style:style>\n')

	self.f.write('<style:style style:name="ro1" style:family="table-row">\n')
	self.f.write('<style:properties fo:break-before="auto"/>\n')
	self.f.write('</style:style>\n')

	for key in self.style_list.keys():
	    style = self.style_list[key]
            font = style.get_font()
	    self.f.write('<style:style style:name="')
            self.f.write(key)
            self.f.write('" style:family="table-cell" ')
	    self.f.write('style:parent-style-name="Default">\n')
	    self.f.write('<style:properties ')
	    self.f.write('fo:color="#%02x%02x%02x" ' % font.get_color())
	    bgcolor = style.get_background_color()
            self.f.write('fo:background-color="#%02x%02x%02x" ' % bgcolor)
	    self.f.write('fo:padding-bottom="%.3fcm" ' % style.get_padding())
	    self.f.write('fo:padding-top="%.3fcm" ' % style.get_padding())
	    self.f.write('fo:padding-right="%.3fcm" ' % style.get_padding())
	    self.f.write('fo:padding-left="%.3fcm" ' % style.get_padding())
  	    self.f.write('style:text-outline="false" ')
	    self.f.write('style:text-crossing-out="none" ')
            if font.get_type_face() == BaseDoc.FONT_SERIF:
	        self.f.write('style:font-name="Times New Roman" ')
            else:
	        self.f.write('style:font-name="Arial" ')
	    self.f.write('fo:font-size="%dpt" ' % font.get_size())
            if font.get_italic():
	        self.f.write('fo:font-style="italic" ')
            else:
	        self.f.write('fo:font-style="normal" ')
  	    self.f.write('fo:text-shadow="none" ')
	    self.f.write('style:text-underline="none" ')
            if font.get_bold():
	        self.f.write('fo:font-weight="bold"/>\n')
            else:
	        self.f.write('fo:font-weight="normal"/>\n')
	    self.f.write('</style:style>\n')
        self.f.write('</office:automatic-styles>\n')
        self.f.write('<office:body>\n')
	self.f.write('<table:calculation-settings>\n')
	self.f.write('<table:iteration table:maximum-difference="0.001"/>\n')
	self.f.write('</table:calculation-settings>\n')

    def close(self):
        self.f.write('</office:body>\n')
        self.f.write('</office:document-content>\n')
        self.f.close()
        self._write_styles_file()
        self._write_manifest()
        self._write_meta_file()
        self._write_zip()

    def start_row(self):
        self.f.write('<table:table-row table:style-name="')
	self.f.write('ro1')
	self.f.write('">\n')

    def end_row(self):
        self.f.write('</table:table-row>\n')

    def start_cell(self,style_name,span=1):
	self.content = 0
	self.span = span
	self.f.write('<table:table-cell table:style-name="')
        self.f.write(style_name)
        self.f.write('" table:value-type="string"')
        if span > 1:
            self.f.write(' table:number-columns-spanned="' + str(span) + '">\n')
	else:	     
	    self.f.write('>\n')

    def end_cell(self):
	if self.content == 0:
	    self.f.write('<text:p/>\n')
        else:
            self.f.write('</text:p>\n')
        self.f.write('</table:table-cell>\n')
        for col in range(1,self.span):
            self.f.write('<table:covered-table-cell/>\n')

    def _write_zip(self):
        
        file = zipfile.ZipFile(self.filename,"w",zipfile.ZIP_DEFLATED)
        file.write(self.manifest_xml,str("META-INF/manifest.xml"))
        file.write(self.content_xml,str("content.xml"))
        file.write(self.meta_xml,str("meta.xml"))
        file.write(self.styles_xml,str("styles.xml"))
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

	self.f = open(self.styles_xml,"w")
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
	self.f.write('office:class="spreadsheet" office:version="0.9">\n')
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
	self.f.write('<style:default-style style:family="table-cell">\n')
	self.f.write('<style:properties style:decimal-places="2" ')
	self.f.write('style:font-name="Arial" ')
	self.f.write('style:tab-stop-distance="0.2835inch"/>\n')
	self.f.write('</style:default-style>\n')
	self.f.write('<style:style style:name="Default" ')
	self.f.write('style:family="table-cell" ')
	self.f.write('style:data-style-name="N0"/>\n')
	self.f.write('<style:default-style style:family="graphics">\n')
	self.f.write('<style:properties fo:color="#000000" ')
	self.f.write('fo:font-family="&apos;Times New Roman&apos;" ')
	self.f.write('style:font-style-name="" ')
	self.f.write('style:font-family-generic="roman" ')
	self.f.write('style:font-pitch="variable" ')
	self.f.write('fo:font-size="12pt" ')
	self.f.write('fo:language="none" ')
	self.f.write('fo:country="none" ')
	self.f.write('style:text-autospace="ideograph-alpha" ')
	self.f.write('style:punctuation-wrap="simple" ')
	self.f.write('style:line-break="strict"/>\n')
	self.f.write('</style:default-style>\n')
        self.f.write('<style:style style:name="Standard" ')
        self.f.write('style:family="paragraph" style:class="text"/>\n')
	self.f.write('<office:automatic-styles>\n')
	self.f.write('<style:page-master style:name="pm1">\n')
	self.f.write('<style:header-style>\n')
	self.f.write('<style:properties fo:min-height="0.2957inch" ')
	self.f.write('fo:margin-left="0inch" ')
	self.f.write('fo:margin-right="0inch" ')
	self.f.write('fo:margin-bottom="0.0984inch"/>\n')
	self.f.write('</style:header-style>\n')
	self.f.write('<style:footer-style>\n')
	self.f.write('<style:properties fo:min-height="0.2957inch" ')
	self.f.write('fo:margin-left="0inch" ')
	self.f.write('fo:margin-right="0inch" ')
	self.f.write('fo:margin-top="0.0984inch"/>\n')
	self.f.write('</style:footer-style>\n')
	self.f.write('</style:page-master>\n')
	self.f.write('<style:page-master style:name="pm2">\n')
	self.f.write('<style:header-style>\n')
	self.f.write('<style:properties fo:min-height="0.2957inch" ')
	self.f.write('fo:margin-left="0inch" ')
	self.f.write('fo:margin-right="0inch" ')
	self.f.write('fo:margin-bottom="0.0984inch" ')
	self.f.write('fo:border="0.0346inch solid #000000" ')
	self.f.write('fo:border-top="0.0346inch solid #000000" ')
	self.f.write('fo:border-bottom="0.0346inch solid #000000" ')
	self.f.write('fo:border-left="0.0346inch solid #000000" ')
	self.f.write('fo:border-right="0.0346inch solid #000000" ')
	self.f.write('fo:padding="0.0071inch" ')
	self.f.write('fo:padding-top="0.0071inch" ')
	self.f.write('fo:padding-bottom="0.0071inch" ')
	self.f.write('fo:padding-left="0.0071inch" ')
	self.f.write('fo:padding-right="0.0071inch" ')
	self.f.write('fo:background-color="#c0c0c0"/>\n')
	self.f.write('</style:header-style>\n')
	self.f.write('<style:footer-style>\n')
	self.f.write('<style:properties fo:min-height="0.2957inch" ')
	self.f.write('fo:margin-left="0inch" ')
	self.f.write('fo:margin-right="0inch" ')
	self.f.write('fo:margin-top="0.0984inch" ')
	self.f.write('fo:border="0.0346inch solid #000000" ')
	self.f.write('fo:border-top="0.0346inch solid #000000" ')
	self.f.write('fo:border-bottom="0.0346inch solid #000000" ')
	self.f.write('fo:border-left="0.0346inch solid #000000" ')
	self.f.write('fo:border-right="0.0346inch solid #000000" ')
	self.f.write('fo:padding="0.0071inch" ')
	self.f.write('fo:padding-top="0.0071inch" ')
	self.f.write('fo:padding-bottom="0.0071inch" ')
	self.f.write('fo:padding-left="0.0071inch" ')
	self.f.write('fo:padding-right="0.0071inch" ')
	self.f.write('fo:background-color="#c0c0c0"/>\n')
	self.f.write('</style:footer-style>\n')
	self.f.write('</style:page-master>\n')
	self.f.write('</office:automatic-styles>\n')
	self.f.write('<office:master-styles>\n')
	self.f.write('<style:master-page style:name="Default" ')
	self.f.write('style:page-master-name="pm1" ')
	self.f.write('style:next-style-name="">\n')
	self.f.write('<style:header>\n')
	self.f.write('<text:p><text:sheet-name>???</text:sheet-name></text:p>\n')
	self.f.write('</style:header>\n')
	self.f.write('<style:footer>\n')
	self.f.write('<text:p>Page <text:page-number>1</text:page-number></text:p>\n')
	self.f.write('</style:footer>\n')
	self.f.write('</style:master-page>\n')
	self.f.write('<style:master-page style:name="Report" ')
	self.f.write('style:page-master-name="pm2" ')
	self.f.write('style:next-style-name="">\n')
	self.f.write('<style:header>\n')
	self.f.write('<style:region-left>\n')
	self.f.write('<text:p><text:sheet-name>???</text:sheet-name> ')
	self.f.write('(<text:file-name>???</text:file-name>)</text:p>\n')
	self.f.write('</style:region-left>\n')
	self.f.write('<style:region-right>\n')
	self.f.write('<text:p><text:date style:data-style-name="N2" ')
	self.f.write('text:date-value="2001-05-16">05/16/2001</text:date>, ')
	self.f.write('<text:time>10:53:17</text:time></text:p>\n')
	self.f.write('</style:region-right>\n')
	self.f.write('</style:header>\n')
	self.f.write('<style:footer>\n')
	self.f.write('<text:p>Page <text:page-number>1</text:page-number> / ')
	self.f.write('<text:page-count>99</text:page-count></text:p>\n')
	self.f.write('</style:footer>\n')
	self.f.write('</style:master-page>\n')
	self.f.write('</office:master-styles>\n')
	self.f.write('</office:styles>\n')
	self.f.write('</office:document-styles>\n')
	self.f.close()

    def start_page(self,name,style_name):
	table = self.table_styles[style_name]
        self.f.write('<table:table table:name="')
	self.f.write(name)
	self.f.write('" table:style-name="')
	self.f.write(style_name)
	self.f.write('">\n')
	for col in range(0,table.get_columns()):
	    self.f.write('<table:table-column table:style-name="')
  	    self.f.write(style_name + '_' + str(col) +'"/>\n')

    def end_page(self):
        self.f.write('</table:table>\n')
        
    def write_text(self,text):
        if text == "":
	    return
        if self.content == 0:
            self.f.write('<text:p>')
            self.content = 1
        text = text.replace('&','&amp;')       # Must be first
        text = text.replace('<','&lt;')
        text = text.replace('>','&gt;')
        text = text.replace('\t','<text:tab-stop/>')
        text = text.replace('\n','<text:line-break/>')
	self.f.write(unicode(text))

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

	self.f = open(self.manifest_xml,"w")
	self.f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	self.f.write('<manifest:manifest ')
        self.f.write('xmlns:manifest="http://openoffice.org/2001/manifest">')
	self.f.write('<manifest:file-entry ')
        self.f.write('manifest:media-type="application/vnd.sun.xml.calc" ')
	self.f.write('manifest:full-path="/"/>')
        self.f.write('<manifest:file-entry manifest:media-type="" ')
	self.f.write('manifest:full-path="Pictures/"/>')
	self.f.write('<manifest:file-entry manifest:media-type="text/xml" ')
	self.f.write('manifest:full-path="content.xml"/>')
	self.f.write('<manifest:file-entry manifest:media-type="text/xml" ')
	self.f.write('manifest:full-path="styles.xml"/>')
	self.f.write('<manifest:file-entry manifest:media-type="text/xml" ')
	self.f.write('manifest:full-path="meta.xml"/>')
	#self.f.write('<manifest:file-entry manifest:media-type="text/xml" ')
	#self.f.write('manifest:full-path="settings.xml"/>')
	self.f.write('</manifest:manifest>\n')
	self.f.close()

    def _write_meta_file(self):
        self.meta_xml = tempfile.mktemp()

        try:
            self.f = open(self.meta_xml,"wb")
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.meta_xml, msg)
            raise Errors.ReportError(errmsg)
        except:
            pass
            raise Errors.ReportError(_("Could not create %s") % self.meta_xml)

	self.f = open(self.meta_xml,"w")
	self.f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	self.f.write('<office:document-meta ')
	self.f.write('xmlns:office="http://openoffice.org/2000/office" ')
	self.f.write('xmlns:xlink="http://www.w3.org/1999/xlink" ')
	self.f.write('xmlns:dc="http://purl.org/dc/elements/1.1/" ')
	self.f.write('xmlns:meta="http://openoffice.org/2000/meta" ')
	self.f.write('office:class="text" office:version="0.9">\n');
	self.f.write('<office:meta>\n')
	self.f.write('<meta:generator>')
        self.f.write(const.program_name + ' ' + const.version)
        self.f.write('</meta:generator>\n')
	self.f.write('<meta:initial-creator>')
	self.f.write(self.name)
	self.f.write('</meta:initial-creator>\n')
	self.f.write('<meta:creation-date>')
	self.f.write(self.time)
	self.f.write('</meta:creation-date>\n')
	self.f.write('<dc:creator>')
	self.f.write(self.name)
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
