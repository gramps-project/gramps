#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2010       Jakim Friant
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
# Python modules
#
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..docgen import PaperSize
from ...const import PAPERSIZE

# -------------------------------------------------------------------------
#
# Try to abstract SAX1 from SAX2
#
# -------------------------------------------------------------------------
from xml.sax import make_parser, handler, SAXParseException

# -------------------------------------------------------------------------
#
# Constants
#
# -------------------------------------------------------------------------
paper_sizes = []


# -------------------------------------------------------------------------
#
# PageSizeParser
#
# -------------------------------------------------------------------------
class PageSizeParser(handler.ContentHandler):
    """Parses the XML file and builds the list of page sizes"""

    def __init__(self, paper_list):
        handler.ContentHandler.__init__(self)
        self.paper_list = paper_list
        self.locator = None

    def setDocumentLocator(self, locator):
        self.locator = locator

    def startElement(self, tag, attrs):
        if tag == "page":
            name = attrs["name"]
            height = float(attrs["height"])
            width = float(attrs["width"])
            self.paper_list.append(PaperSize(name, height, width))


# -------------------------------------------------------------------------
#
# Parse XML file. If it fails, use the default
#
# -------------------------------------------------------------------------
try:
    parser = make_parser()
    parser.setContentHandler(PageSizeParser(paper_sizes))
    with open(PAPERSIZE) as the_file:
        parser.parse(the_file)
    paper_sizes.append(PaperSize("Custom Size", -1, -1))  # always in English
except (IOError, OSError, SAXParseException):
    paper_sizes = [
        PaperSize("Letter", 27.94, 21.59),
        PaperSize("Legal", 35.56, 21.59),
        PaperSize("A0", 118.9, 84.1),
        PaperSize("A1", 84.1, 59.4),
        PaperSize("A2", 59.4, 42.0),
        PaperSize("A3", 42.0, 29.7),
        PaperSize("A4", 29.7, 21.0),
        PaperSize("A5", 21.0, 14.8),
        PaperSize("B0", 141.4, 100.0),
        PaperSize("B1", 100.0, 70.7),
        PaperSize("B2", 70.7, 50.0),
        PaperSize("B3", 50.0, 35.3),
        PaperSize("B4", 35.3, 25.0),
        PaperSize("B5", 25.0, 17.6),
        PaperSize("B6", 17.6, 12.5),
        PaperSize("B", 43.18, 27.94),
        PaperSize("C", 55.88, 43.18),
        PaperSize("D", 86.36, 55.88),
        PaperSize("E", 111.76, 86.36),
        PaperSize("Custom Size", -1, -1),  # always in English
    ]
