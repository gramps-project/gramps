#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 B. Malengier
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Adam Stein <adam@csh.rit.edu>
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

"""
The docgen package providing the API the document generating plugins can use.
A docgen plugin should fully implement this api for TextDoc or DrawDoc
"""

from .basedoc import BaseDoc
from .paperstyle import PaperSize, PaperStyle, PAPER_PORTRAIT, PAPER_LANDSCAPE
from .fontstyle import FontStyle, FONT_SANS_SERIF, FONT_SERIF, FONT_MONOSPACE
from .paragraphstyle import (
    ParagraphStyle,
    PARA_ALIGN_CENTER,
    PARA_ALIGN_LEFT,
    PARA_ALIGN_RIGHT,
    PARA_ALIGN_JUSTIFY,
)
from .tablestyle import TableStyle, TableCellStyle
from .stylesheet import StyleSheetList, StyleSheet, SheetParser
from .graphicstyle import GraphicsStyle, SOLID, DASHED, DOTTED
from .textdoc import (
    TextDoc,
    IndexMark,
    INDEX_TYPE_ALP,
    INDEX_TYPE_TOC,
    URL_PATTERN,
    LOCAL_HYPERLINK,
    LOCAL_TARGET,
)
from .drawdoc import DrawDoc
from .graphdoc import GVDoc
from .treedoc import TreeDoc
