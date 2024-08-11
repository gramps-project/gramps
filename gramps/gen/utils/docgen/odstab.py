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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

# -------------------------------------------------------------------------
#
# Standard Python Modules
#
# -------------------------------------------------------------------------
import os
import tempfile
import zipfile
from ...const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .tabbeddoc import *
from ...const import PROGRAM_NAME, VERSION
from ...errors import ReportError

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------

_XMLNS = """\
xmlns:office="%(urn)soffice:1.0"
xmlns:style="%(urn)sstyle:1.0"
xmlns:text="%(urn)stext:1.0"
xmlns:table="%(urn)stable:1.0"
xmlns:draw="%(urn)sdrawing:1.0"
xmlns:fo="%(urn)sxsl-fo-compatible:1.0"
xmlns:xlink="http://www.w3.org/1999/xlink"
xmlns:dc="http://purl.org/dc/elements/1.1/"
xmlns:meta="%(urn)smeta:1.0"
xmlns:number="%(urn)sdatastyle:1.0"
xmlns:svg="%(urn)ssvg-compatible:1.0"
xmlns:chart="%(urn)schart:1.0"
xmlns:dr3d="%(urn)sdr3d:1.0"
xmlns:math="http://www.w3.org/1998/Math/MathML"
xmlns:form="%(urn)sform:1.0"
xmlns:script="%(urn)sscript:1.0"
xmlns:dom="http://www.w3.org/2001/xml-events"
xmlns:xforms="http://www.w3.org/2002/xforms"
xmlns:xsd="http://www.w3.org/2001/XMLSchema"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
""" % {
    "urn": "urn:oasis:names:tc:opendocument:xmlns:"
}

_DOC_FONTS = """\
<office:font-face-decls>
    <style:font-face style:name="Nimbus Sans L"
        svg:font-family="'Nimbus Sans L'"
        style:font-family-generic="swiss"
        style:font-pitch="variable"/>
    <style:font-face style:name="DejaVu Sans"
        svg:font-family="'DejaVu San'"
        style:font-family-generic="system"
        style:font-pitch="variable"/>
</office:font-face-decls>
"""

_DOC_STYLES = """\
<office:automatic-styles>
    <style:style style:name="co1"
        style:family="table-column">
        <style:table-column-properties
            fo:break-before="auto"
            style:column-width="3cm"/>
    </style:style>
    <style:style style:name="ro1"
        style:family="table-row">
        <style:table-row-properties
            style:row-height="0.189in"
            fo:break-before="auto"
            style:use-optimal-row-height="true"/>
    </style:style>
    <style:style style:name="ta1"
        style:family="table"
        style:master-page-name="Default">
        <style:table-properties
            table:display="true"
            style:writing-mode="lr-tb"/>
    </style:style>
</office:automatic-styles>
"""

_STYLES_FONTS = """\
<office:font-face-decls>
    <style:font-face style:name="Times New Roman"
        svg:font-family="'Times New Roman'"
        style:font-family-generic="roman"
        style:font-pitch="variable"/>
    <style:font-face style:name="Arial"
        svg:font-family="Arial"
        style:font-family-generic="swiss"
        style:font-pitch="variable"/>
</office:font-face-decls>
"""

_STYLES_STYLES = """\
<office:styles>
    <style:default-style style:family="table-cell">
        <style:table-cell-properties
            style:decimal-places="2"/>
        <style:paragraph-properties
            style:tab-stop-distance="0.2835inch"/>
        <style:text-properties
            style:font-name="Arial"/>
    </style:default-style>

    <style:style style:name="Default"
        style:family="table-cell"
        style:data-style-name="N0"/>

    <style:default-style style:family="graphic">
        <style:text-properties fo:color="#000000"
            fo:font-family="'Times New Roman'"
            style:font-style-name=""
            style:font-family-generic="roman"
            style:font-pitch="variable"
            fo:font-size="12pt"
            fo:language="none"
            fo:country="none"
            style:text-autospace="ideograph-alpha"
            style:punctuation-wrap="simple"
            style:line-break="strict"/>
    </style:default-style>
</office:styles>
"""
_STYLES_AUTOMATIC = """\
<office:automatic-styles>
    <style:page-layout style:name="pm1">
        <style:header-style>
            <style:header-footer-properties
                fo:min-height="0.2957inch"
                fo:margin-left="0inch"
                fo:margin-right="0inch"
                fo:margin-bottom="0.0984inch"/>
        </style:header-style>
        <style:footer-style>
            <style:header-footer-properties
                fo:min-height="0.2957inch"
                fo:margin-left="0inch"
                fo:margin-right="0inch"
                fo:margin-top="0.0984inch"/>
        </style:footer-style>
    </style:page-layout>
    <style:page-layout style:name="pm2">
        <style:header-style>
            <style:header-footer-properties
                fo:min-height="0.2957inch"
                fo:margin-left="0inch"
                fo:margin-right="0inch"
                fo:margin-bottom="0.0984inch"
                fo:border="0.0346inch solid #000000"
                fo:border-top="0.0346inch solid #000000"
                fo:border-bottom="0.0346inch solid #000000"
                fo:border-left="0.0346inch solid #000000"
                fo:border-right="0.0346inch solid #000000"
                fo:padding="0.0071inch"
                fo:padding-top="0.0071inch"
                fo:padding-bottom="0.0071inch"
                fo:padding-left="0.0071inch"
                fo:padding-right="0.0071inch"
                fo:background-color="#c0c0c0"/>
        </style:header-style>
        <style:footer-style>
            <style:header-footer-properties
                fo:min-height="0.2957inch"
                fo:margin-left="0inch"
                fo:margin-right="0inch"
                fo:margin-top="0.0984inch"
                fo:border="0.0346inch solid #000000"
                fo:border-top="0.0346inch solid #000000"
                fo:border-bottom="0.0346inch solid #000000"
                fo:border-left="0.0346inch solid #000000"
                fo:border-right="0.0346inch solid #000000"
                fo:padding="0.0071inch"
                fo:padding-top="0.0071inch"
                fo:padding-bottom="0.0071inch"
                fo:padding-left="0.0071inch"
                fo:padding-right="0.0071inch"
                fo:background-color="#c0c0c0"/>
        </style:footer-style>
    </style:page-layout>
</office:automatic-styles>
"""

_STYLES_MASTER = """\
<office:master-styles>
    <style:master-page style:name="Default"
        style:page-layout-name="pm1">
        <style:header>
            <text:p>
                <text:sheet-name>???</text:sheet-name>
            </text:p>
        </style:header>
        <style:footer>
            <text:p>Page
                <text:page-number>1</text:page-number>
            </text:p>
        </style:footer>
    </style:master-page>
    <style:master-page style:name="Report"
        style:page-layout-name="pm2">
        <style:header>
            <style:region-left>
                <text:p>
                    <text:sheet-name>???</text:sheet-name>
                    (<text:file-name>???</text:file-name>)
                </text:p>
            </style:region-left>
            <style:region-right>
                <text:p>
                    <text:date style:data-style-name="N2"
                        text:date-value="2001-05-16">05/16/2001
                    </text:date>,
                        <text:time>10:53:17</text:time>
                </text:p>
            </style:region-right>
        </style:header>
        <style:footer>
            <text:p>Page
                <text:page-number>1</text:page-number> /
                <text:page-count>99</text:page-count>
            </text:p>
        </style:footer>
    </style:master-page>
</office:master-styles>
"""

_MANIFEST = """\
<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest
    xmlns:manifest=
        "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
    <manifest:file-entry
        manifest:media-type=
            "application/vnd.oasis.opendocument.spreadsheet"
        manifest:full-path="/"/>
    <manifest:file-entry manifest:media-type=""
        manifest:full-path="Pictures/"/>
    <manifest:file-entry manifest:media-type="text/xml"
        manifest:full-path="content.xml"/>
    <manifest:file-entry manifest:media-type="text/xml"
        manifest:full-path="styles.xml"/>
    <manifest:file-entry manifest:media-type="text/xml"
        manifest:full-path="meta.xml"/>
</manifest:manifest>
"""

_META = """\
<?xml version="1.0" encoding="UTF-8"?>
<office:document-meta
    xmlns:office=
        "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:meta=
        "urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
    office:class="text" office:version="1.0">
    <office:meta>
        <meta:generator>
            %(program)s %(version)s
        </meta:generator>
        <meta:initial-creator>
            %(name)s
        </meta:initial-creator>
        <meta:creation-date>
            %(time)s
        </meta:creation-date>
        <dc:creator>
            %(name)s
        </dc:creator>
        <dc:date>
            %(time)s
        </dc:date>
        <meta:print-date>
            0-00-00T00:00:00
        </meta:print-date>
        <dc:language>en-US</dc:language>
        <meta:editing-cycles>1</meta:editing-cycles>
        <meta:editing-duration>PT0S</meta:editing-duration>
        <meta:user-defined meta:name="Info 0"/>
        <meta:user-defined meta:name="Info 1"/>
        <meta:user-defined meta:name="Info 2"/>
        <meta:user-defined meta:name="Info 3"/>
    </office:meta>
</office:document-meta>
"""


# -------------------------------------------------------------------------
#
# ODSTab
#
# -------------------------------------------------------------------------
class ODSTab(TabbedDoc):
    def __init__(self, columns):
        TabbedDoc.__init__(self, columns)
        self.f = None
        self.filename = None
        self.level = 0
        self.time = "0000-00-00T00:00:00"

    def open(self, filename):
        import time

        t = time.localtime(time.time())
        self.time = "%04d-%02d-%02dT%02d:%02d:%02d" % t[:6]

        self.filename = filename
        if not filename.endswith(".ods"):
            self.filename += ".ods"

        try:
            self.content_xml = tempfile.mktemp()
            self.f = open(self.content_xml, "wb")
        except IOError as msg:
            raise ReportError(_("Could not create %s") % self.content_xml, msg)
        except:
            raise ReportError(_("Could not create %s") % self.content_xml)

        self.f = open(self.content_xml, "w", encoding="utf-8")
        self.f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            + "<office:document-content "
            + _XMLNS
            + 'office:version="1.0"> '
            + "<office:script/>\n"
        )

        self.f.write(_DOC_FONTS)
        self.f.write(_DOC_STYLES)
        self.f.write("<office:body>\n" "<office:spreadsheet>\n")

    def close(self):
        self.f.write(
            "</office:spreadsheet>\n" "</office:body>\n" "</office:document-content>\n"
        )
        self.f.close()
        self._write_styles_file()
        self._write_manifest()
        self._write_meta_file()
        self._write_mimetype_file()
        self._write_zip()

    def start_row(self):
        self.f.write('<table:table-row table:style-name="')
        self.f.write("ro1")
        self.f.write('">\n')

    def end_row(self):
        self.f.write("</table:table-row>\n")

    def write_cell(self, text):
        self.f.write('<table:table-cell office:value-type="string">')
        self.f.write(">\n")

        self.f.write("<text:p>")
        if text is not None:  # it must not be just 'if text'
            text = text.replace("&", "&amp;")  # Must be first
            text = text.replace("<", "&lt;")
            text = text.replace(">", "&gt;")
            text = text.replace("\t", "<text:tab-stop/>")
            text = text.replace("\n", "<text:line-break/>")
            self.f.write(str(text))

        self.f.write("</text:p>\n")
        self.f.write("</table:table-cell>\n")

    #        for col in range(1,self.span):
    #            self.f.write('<table:covered-table-cell/>\n')

    def _write_zip(self):
        try:
            file = zipfile.ZipFile(self.filename, "w", zipfile.ZIP_DEFLATED)
        except IOError as msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.filename, msg)
            raise ReportError(errmsg)
        except:
            raise ReportError(_("Could not create %s") % self.filename)

        file.write(self.manifest_xml, str("META-INF/manifest.xml"))
        file.write(self.content_xml, str("content.xml"))
        file.write(self.meta_xml, str("meta.xml"))
        file.write(self.styles_xml, str("styles.xml"))
        file.write(self.mimetype, str("mimetype"))
        file.close()

        os.unlink(self.manifest_xml)
        os.unlink(self.content_xml)
        os.unlink(self.meta_xml)
        os.unlink(self.styles_xml)

    def _write_styles_file(self):
        self.styles_xml = tempfile.mktemp()

        try:
            self.f = open(self.styles_xml, "wb")
        except IOError as msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.styles_xml, msg)
            raise ReportError(errmsg)
        except:
            raise ReportError(_("Could not create %s") % self.styles_xml)

        self.f = open(self.styles_xml, "w")
        self.f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self.f.write("<office:document-styles " + _XMLNS + 'office:version="1.0"> ')
        self.f.write(_STYLES_FONTS)
        self.f.write(_STYLES_STYLES)
        self.f.write(_STYLES_AUTOMATIC)
        self.f.write(_STYLES_MASTER)

        self.f.write("</office:document-styles>\n")
        self.f.close()

    def start_page(self):
        self.f.write('<table:table table:name="ta1">')
        for col in range(0, self.columns):
            self.f.write('<table:table-column table:style-name="co1"/>\n')

    def end_page(self):
        self.f.write("</table:table>\n")

    def _write_manifest(self):
        self.manifest_xml = tempfile.mktemp()

        try:
            self.f = open(self.manifest_xml, "wb")
        except IOError as msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.manifest_xml, msg)
            raise ReportError(errmsg)
        except:
            raise ReportError(_("Could not create %s") % self.manifest_xml)

        self.f = open(self.manifest_xml, "w")
        self.f.write(_MANIFEST)
        self.f.close()

    def _write_meta_file(self):
        self.meta_xml = tempfile.mktemp()

        try:
            self.f = open(self.meta_xml, "wb")
        except IOError as msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.meta_xml, msg)
            raise ReportError(errmsg)
        except:
            raise ReportError(_("Could not create %s") % self.meta_xml)

        self.f = open(self.meta_xml, "w")

        self.f.write(
            _META
            % {
                "program": PROGRAM_NAME,
                "version": VERSION,
                "name": self.name,
                "time": self.time,
            }
        )
        self.f.close()

    def _write_mimetype_file(self):
        self.mimetype = tempfile.mktemp()

        try:
            self.f = open(self.mimetype, "wb")
        except IOError as msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.mimetype, msg)
            raise ReportError(errmsg)
        except:
            raise ReportError(_("Could not create %s") % self.mimetype)

        self.f = open(self.mimetype, "w")
        self.f.write("application/vnd.oasis.opendocument.spreadsheet")
        self.f.close()


if __name__ == "__main__":
    file = ODSTab(3)
    file.open("test")
    file.start_page()
    for i in [("one", "two", "three"), ('fo"ur', "fi,ve", "six")]:
        file.start_row()
        for j in i:
            file.write_cell(j)
        file.end_row()
    file.end_page()
    file.close()
