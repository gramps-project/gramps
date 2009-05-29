#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2009 B. Malengier
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

# $Id: __init__.py 10055 2008-02-18 20:07:09Z acraphae $

"""
The docgen package providing the API the document generating plugins can use.
A docgen plugin should fully implement this api for TextDoc or DrawDoc
"""

from basedoc import BaseDoc, PaperSize, PaperStyle, FontStyle, ParagraphStyle,\
                TableStyle, TableCellStyle, StyleSheetList, StyleSheet,\
                SheetParser, GraphicsStyle, TextDoc, IndexMark, DrawDoc, GVDoc
