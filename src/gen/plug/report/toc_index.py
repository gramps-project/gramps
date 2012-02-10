#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2011  Nick Hall
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

"""
Provide utilities for generating a table of contents and alphabetical index in 
text reports.
"""
from gen.plug.docgen import (FontStyle, ParagraphStyle, TableStyle, 
                            TableCellStyle, FONT_SANS_SERIF)
from gen.ggettext import gettext as _

def add_toc_index_styles(style_sheet):
    """
    Add paragraph styles to a style sheet to be used for displaying a table of 
    contents and alphabetical index.
    """
    font = FontStyle()
    font.set(face=FONT_SANS_SERIF, size=14)
    para = ParagraphStyle()
    para.set_font(font)
    para.set_bottom_margin(0.25)
    para.set_description(_('The style used for the TOC title.'))
    style_sheet.add_paragraph_style("TOC-Title", para)
    
    font = FontStyle()
    font.set(face=FONT_SANS_SERIF, size=14)
    para = ParagraphStyle()
    para.set_font(font)
    para.set_bottom_margin(0.25)
    para.set_description(_('The style used for the Index title.'))
    style_sheet.add_paragraph_style("Index-Title", para)
    
    table = TableStyle()
    table.set_width(100)
    table.set_columns(2)
    table.set_column_width(0, 80)
    table.set_column_width(1, 20)
    style_sheet.add_table_style("TOC-Table", table)
    
    cell = TableCellStyle()
    style_sheet.add_cell_style("TOC-Cell", cell)
    
    font = FontStyle()
    font.set(face=FONT_SANS_SERIF, size=10)
    para = ParagraphStyle()
    para.set_font(font)
    para.set_description(_('The style used for the TOC page numbers.'))
    style_sheet.add_paragraph_style("TOC-Number", para)

    font = FontStyle()
    font.set(face=FONT_SANS_SERIF, size=10)
    para = ParagraphStyle()
    para.set_font(font)
    para.set_description(_('The style used for the Index page numbers.'))
    style_sheet.add_paragraph_style("Index-Number", para)

    para = ParagraphStyle()
    para.set_font(font)
    para.set_description(_('The style used for the TOC first level heading.'))
    style_sheet.add_paragraph_style("TOC-Heading1", para)

    para = ParagraphStyle()
    para.set_font(font)
    para.set_first_indent(0.5)
    para.set_description(_('The style used for the TOC second level heading.'))
    style_sheet.add_paragraph_style("TOC-Heading2", para)

    para = ParagraphStyle()
    para.set_font(font)
    para.set_first_indent(1)
    para.set_description(_('The style used for the TOC third level heading.'))
    style_sheet.add_paragraph_style("TOC-Heading3", para)

def write_toc(toc, doc, offset):
    """
    Write the table of contents.
    """
    if not toc:
        return

    doc.start_paragraph('TOC-Title')
    doc.write_text(_('Contents'))
    doc.end_paragraph()
    
    doc.start_table('toc', 'TOC-Table')
    for mark, page_nr in toc:
        doc.start_row()
        doc.start_cell('TOC-Cell')
        if mark.level == 1:
            style_name = "TOC-Heading1"
        elif mark.level == 2:
            style_name = "TOC-Heading2"
        else:
            style_name = "TOC-Heading3"
        doc.start_paragraph(style_name)
        doc.write_text(mark.key)
        doc.end_paragraph()
        doc.end_cell()
        doc.start_cell('TOC-Cell')
        doc.start_paragraph('TOC-Number')
        doc.write_text(str(page_nr + offset + 1))
        doc.end_paragraph()
        doc.end_cell()
        doc.end_row()
    doc.end_table()
    
def write_index(index, doc, offset):
    """
    Write the alphabetical index.
    """
    if not index:
        return

    doc.start_paragraph('Index-Title')
    doc.write_text(_('Index'))
    doc.end_paragraph()
    
    doc.start_table('index', 'TOC-Table')
    for key in sorted(index.iterkeys()):
        doc.start_row()
        doc.start_cell('TOC-Cell')
        doc.start_paragraph('Index-Number')
        doc.write_text(key)
        doc.end_paragraph()
        doc.end_cell()
        doc.start_cell('TOC-Cell')
        doc.start_paragraph('Index-Number')
        pages = [str(page_nr + offset + 1) for page_nr in index[key]]
        doc.write_text(', '.join(pages))
        doc.end_paragraph()
        doc.end_cell()
        doc.end_row()
    doc.end_table()
