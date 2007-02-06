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

# $Id: 

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
from TabbedDoc import *

import const

import Errors

#-------------------------------------------------------------------------
#
# OpenSpreadSheet
#
#-------------------------------------------------------------------------
class ODSTab(TabbedDoc):

    def __init__(self, columns):
        TabbedDoc.__init__(self, columns)
        self.f = None
        self.filename = None
        self.level = 0
        self.time = "0000-00-00T00:00:00"

    def open(self,filename):
        import time
        
        t = time.localtime(time.time())
        self.time = "%04d-%02d-%02dT%02d:%02d:%02d" % \
                    (t[0],t[1],t[2],t[3],t[4],t[5])

        if filename[-4:] != ".ods":
            self.filename = filename + ".ods"
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
        self.f.write('xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"  ')
        self.f.write('xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" ')
        self.f.write('xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" ')
        self.f.write('xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" ')
        self.f.write('xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" ')
        self.f.write('xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" ')
        self.f.write('xmlns:xlink="http://www.w3.org/1999/xlink" ')
        self.f.write('xmlns:dc="http://purl.org/dc/elements/1.1/" ')
        self.f.write('xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" ')
        self.f.write('xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"  ')
        self.f.write('xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" ')
        self.f.write('xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" ')
        self.f.write('xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" ')
        self.f.write('xmlns:math="http://www.w3.org/1998/Math/MathML" ')
        self.f.write('xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" ')
        self.f.write('xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" ')
        self.f.write('xmlns:dom="http://www.w3.org/2001/xml-events" ')
        self.f.write('xmlns:xforms="http://www.w3.org/2002/xforms" ')
        self.f.write('xmlns:xsd="http://www.w3.org/2001/XMLSchema" ')
        self.f.write('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ')
        self.f.write('office:version="1.0"> ')
        self.f.write('<office:script/>\n')
        self.f.write('<office:font-face-decls>\n')
        self.f.write('<style:font-face style:name="Nimbus Sans L" ')
        self.f.write('svg:font-family="\'Nimbus Sans L\'" style:font-family-generic="swiss" ')
        self.f.write('style:font-pitch="variable"/>\n')
        self.f.write('<style:font-face style:name="DejaVu Sans" ')
        self.f.write('svg:font-family="\'DejaVu Sans\'" style:font-family-generic="system" ')
        self.f.write('style:font-pitch="variable"/>\n')
        self.f.write('</office:font-face-decls>\n')

        self.f.write('<office:automatic-styles>\n')
        self.f.write('<style:style style:name="co1" style:family="table-column">\n')
        self.f.write('<style:table-column-properties fo:break-before="auto" style:column-width="3cm"/>\n')
        self.f.write('</style:style>\n')
        self.f.write('<style:style style:name="ro1" style:family="table-row">\n')
        self.f.write('<style:table-row-properties style:row-height="0.189in" ')
        self.f.write('fo:break-before="auto" style:use-optimal-row-height="true"/>\n')
        self.f.write('</style:style>\n')
        self.f.write('<style:style style:name="ta1" style:family="table" ')
        self.f.write('style:master-page-name="Default">\n')
        self.f.write('<style:table-properties table:display="true" style:writing-mode="lr-tb"/>\n')
        self.f.write('</style:style>\n')
        self.f.write('</office:automatic-styles>\n')
        self.f.write('<office:body>\n')
        self.f.write('<office:spreadsheet>\n')

    def close(self):
        self.f.write('</office:spreadsheet>\n')
        self.f.write('</office:body>\n')
        self.f.write('</office:document-content>\n')
        self.f.close()
        self._write_styles_file()
        self._write_manifest()
        self._write_meta_file()
        self._write_mimetype_file()
        self._write_zip()

    def start_row(self):
        self.f.write('<table:table-row table:style-name="')
        self.f.write('ro1')
        self.f.write('">\n')

    def end_row(self):
        self.f.write('</table:table-row>\n')

    def write_cell(self, text):
    	self.f.write('<table:table-cell office:value-type="string">')
        self.f.write('>\n')

        self.f.write('<text:p>')
        text = text.replace('&','&amp;')       # Must be first
        text = text.replace('<','&lt;')
        text = text.replace('>','&gt;')
        text = text.replace('\t','<text:tab-stop/>')
        text = text.replace('\n','<text:line-break/>')
	self.f.write(unicode(text))

        self.f.write('</text:p>\n')
        self.f.write('</table:table-cell>\n')
#        for col in range(1,self.span):
#            self.f.write('<table:covered-table-cell/>\n')

    def _write_zip(self):
        try:
            file = zipfile.ZipFile(self.filename,"w",zipfile.ZIP_DEFLATED)    
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.filename, msg)
            raise Errors.ReportError(errmsg)
        except:
            raise Errors.ReportError(_("Could not create %s") % self.filename)

        file.write(self.manifest_xml,str("META-INF/manifest.xml"))
        file.write(self.content_xml,str("content.xml"))
        file.write(self.meta_xml,str("meta.xml"))
        file.write(self.styles_xml,str("styles.xml"))
        file.write(self.mimetype,str("mimetype"))
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
        self.f.write('xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" ')
        self.f.write('xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" ')
        self.f.write('xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" ')
        self.f.write('xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" ')
        self.f.write('xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" ')
        self.f.write('xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" ')
        self.f.write('xmlns:xlink="http://www.w3.org/1999/xlink" ')
        self.f.write('xmlns:dc="http://purl.org/dc/elements/1.1/" ')
        self.f.write('xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" ')
        self.f.write('xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" ')
        self.f.write('xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" ')
        self.f.write('xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" ')
        self.f.write('xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" ')
        self.f.write('xmlns:math="http://www.w3.org/1998/Math/MathML" ')
        self.f.write('xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" ')
        self.f.write('xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" ')
        self.f.write('xmlns:dom="http://www.w3.org/2001/xml-events" ')
        self.f.write('office:version="1.0">')

        self.f.write('<office:font-face-decls>\n')
        self.f.write('<style:font-face style:name="Times New Roman" ')
        self.f.write('svg:font-family="&apos;Times New Roman&apos;" ')
        self.f.write('style:font-family-generic="roman" ')
        self.f.write('style:font-pitch="variable"/>\n')
        self.f.write('<style:font-face style:name="Arial" ')
        self.f.write('svg:font-family="Arial" ')
        self.f.write('style:font-family-generic="swiss" ')
        self.f.write('style:font-pitch="variable"/>\n')
        self.f.write('</office:font-face-decls>\n')
    
        self.f.write('<office:styles>\n')
   
        self.f.write('<style:default-style style:family="table-cell">\n')
        self.f.write('<style:table-cell-properties style:decimal-places="2" />\n')
        self.f.write('<style:paragraph-properties style:tab-stop-distance="0.2835inch"/>\n')
        self.f.write('<style:text-properties style:font-name="Arial" />\n')
        self.f.write('</style:default-style>\n')

        self.f.write('<style:style style:name="Default" ')
        self.f.write('style:family="table-cell" ')
        self.f.write('style:data-style-name="N0"/>\n')
        
        self.f.write('<style:default-style style:family="graphic">\n')
        self.f.write('<style:text-properties fo:color="#000000" ')
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
        self.f.write('</office:styles>\n')
        
        self.f.write('<office:automatic-styles>\n')
        self.f.write('<style:page-layout style:name="pm1">\n')
        self.f.write('<style:header-style>\n')
        self.f.write('<style:header-footer-properties fo:min-height="0.2957inch" ')
        self.f.write('fo:margin-left="0inch" ')
        self.f.write('fo:margin-right="0inch" ')
        self.f.write('fo:margin-bottom="0.0984inch"/>\n')
        self.f.write('</style:header-style>\n')
        self.f.write('<style:footer-style>\n')
        self.f.write('<style:header-footer-properties fo:min-height="0.2957inch" ')
        self.f.write('fo:margin-left="0inch" ')
        self.f.write('fo:margin-right="0inch" ')
        self.f.write('fo:margin-top="0.0984inch"/>\n')
        self.f.write('</style:footer-style>\n')
        self.f.write('</style:page-layout>\n')
        self.f.write('<style:page-layout style:name="pm2">\n')
        self.f.write('<style:header-style>\n')
        self.f.write('<style:header-footer-properties fo:min-height="0.2957inch" ')
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
        self.f.write('<style:header-footer-properties fo:min-height="0.2957inch" ')
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
        self.f.write('</style:page-layout>\n')
        self.f.write('</office:automatic-styles>\n')
        
        self.f.write('<office:master-styles>\n')
        self.f.write('<style:master-page style:name="Default" ')
        self.f.write('style:page-layout-name="pm1" >\n')
        self.f.write('<style:header>\n')
        self.f.write('<text:p><text:sheet-name>???</text:sheet-name></text:p>\n')
        self.f.write('</style:header>\n')
        self.f.write('<style:footer>\n')
        self.f.write('<text:p>Page <text:page-number>1</text:page-number></text:p>\n')
        self.f.write('</style:footer>\n')
        self.f.write('</style:master-page>\n')
        self.f.write('<style:master-page style:name="Report" ')
        self.f.write('style:page-layout-name="pm2" >\n')
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
        
        self.f.write('</office:document-styles>\n')
        self.f.close()

    def start_page(self):
        self.f.write('<table:table table:name="ta1">')
	for col in range(0,self.columns):
	    self.f.write('<table:table-column table:style-name="co1"/>\n')

    def end_page(self):
        self.f.write('</table:table>\n')
        
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
        self.f.write('xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">')
        self.f.write('<manifest:file-entry ')
        self.f.write('manifest:media-type="application/vnd.oasis.opendocument.spreadsheet" ')
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
        self.f.write('xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" ')
        self.f.write('xmlns:xlink="http://www.w3.org/1999/xlink" ')
        self.f.write('xmlns:dc="http://purl.org/dc/elements/1.1/" ')
        self.f.write('xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" ')
        self.f.write('office:class="text" office:version="1.0">\n');
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

    def _write_mimetype_file(self):
        self.mimetype = tempfile.mktemp()

        try:
            self.f = open(self.mimetype,"wb")
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.mimetype, msg)
            raise Errors.ReportError(errmsg)
        except:
            pass
            raise Errors.ReportError(_("Could not create %s") % self.mimetype)

        self.f = open(self.mimetype,"w")
        self.f.write('application/vnd.oasis.opendocument.spreadsheet')
        self.f.close()

if __name__ == "__main__":


    file = ODSTab(3)
    file.open("test")
    file.start_page()
    for i in [ ('one', 'two', 'three'), ('fo"ur', 'fi,ve', 'six') ]:
        file.start_row()
        for j in i:
            file.write_cell(j)
        file.end_row()
    file.end_page()
    file.close()
