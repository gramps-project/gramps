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

# $Id: TextBufDoc.py 8431 2007-04-30 01:56:34Z pez4brian $

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _
import gtk
import pango

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
import BaseDoc
from PluginUtils import register_text_doc
import const
import Errors
import Utils

try:
    import pangocairo

    RESOLUTION = pangocairo.cairo_font_map_get_default().get_resolution()
except:
    RESOLUTION = 96

def pixels(cm):
    return int (RESOLUTION/2.54 * cm) 

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------
LEFT,RIGHT,CENTER = 'LEFT','RIGHT','CENTER'
_WIDTH_IN_CHARS = 72


class DisplayBuf:

    def __init__(self, title, buffer):
        g = gtk.glade.XML(const.GLADE_FILE,'scrollmsg')
        self.top = g.get_widget('scrollmsg')
        msg = g.get_widget('msg')
        msg.set_buffer(buffer)
        g.get_widget('close').connect('clicked', self.close)
        
    def close(self, obj):
        self.top.destroy()

#------------------------------------------------------------------------
#
# TextBuf
#
#------------------------------------------------------------------------
class TextBufDoc(BaseDoc.BaseDoc, BaseDoc.TextDoc):

    #--------------------------------------------------------------------
    #
    # Opens the file, resets the text buffer.
    #
    #--------------------------------------------------------------------
    def open(self, filename):
        self.tag_table = gtk.TextTagTable()

        sheet = self.get_style_sheet()

        for name in sheet.get_paragraph_style_names():
            tag = gtk.TextTag(name)

            style = sheet.get_paragraph_style(name)
            font = style.get_font()
            if font.get_type_face() == BaseDoc.FONT_SERIF:
                tag.set_property("family", "Serif")
            elif font.get_type_face() == BaseDoc.FONT_SANS_SERIF:
                tag.set_property("family", "Sans")
            elif font.get_type_face() == BaseDoc.FONT_MONOSPACE:
                tag.set_property("family", "MonoSpace")

            tag.set_property("size-points", float(font.get_size()))
            if font.get_bold():
                tag.set_property("weight", pango.WEIGHT_BOLD)
            if style.get_alignment() == BaseDoc.PARA_ALIGN_RIGHT:
                tag.set_property("justification", gtk.JUSTIFY_RIGHT)
            elif style.get_alignment() == BaseDoc.PARA_ALIGN_LEFT:
                tag.set_property("justification", gtk.JUSTIFY_LEFT)
            elif style.get_alignment() == BaseDoc.PARA_ALIGN_CENTER:
                tag.set_property("justification", gtk.JUSTIFY_CENTER)
            else:
                tag.set_property("justification", gtk.JUSTIFY_FILL)

            if font.get_italic():
                tag.set_property("style", pango.STYLE_ITALIC)

            if style.get_first_indent():
                tag.set_property("indent", pixels(style.get_first_indent()))
                #tag.set_property("tabs", [pixels(abs(style.get_first_indent()))])

            tag.set_property("left-margin", pixels(style.get_left_margin()))
            tag.set_property("right-margin", pixels(style.get_right_margin()))
            tag.set_property("pixels-above-lines", pixels(style.get_top_margin()))
            tag.set_property("pixels-below-lines", pixels(style.get_bottom_margin()))
            tag.set_property("wrap-mode", gtk.WRAP_WORD)

            new_tabs = style.get_tabs()

            tab_array = pango.TabArray(len(new_tabs)+1,True)
            index = 0
            for tab in [ pixels(x) for x in new_tabs ]:
                tab_array.set_tab(index, pango.TAB_LEFT, tab)
                index += 1
            tag.set_property("tabs", tab_array)

            self.tag_table.add(tag)
        self.buffer = gtk.TextBuffer(self.tag_table)
        return

    #--------------------------------------------------------------------
    #
    # Close the file. Call the app if required. 
    #
    #--------------------------------------------------------------------
    def close(self):
        DisplayBuf('',self.buffer)

    def get_usable_width(self):
        return _WIDTH_IN_CHARS

    #--------------------------------------------------------------------
    #
    # Force a section page break
    #
    #--------------------------------------------------------------------
    def end_page(self):
        return
        self.f.write('\012')

    def start_bold(self):
        pass

    def end_bold(self):
        pass

    def page_break(self):
        pass

    def start_superscript(self):
        return

    def end_superscript(self):
        return

    #--------------------------------------------------------------------
    #
    # Starts a paragraph. 
    #
    #--------------------------------------------------------------------
    def start_paragraph(self, style_name, leader=None):
        self.style_name = style_name
        if leader:
            self.text = leader + "\t"
        else:
            self.text = ""

    #--------------------------------------------------------------------
    #
    # End a paragraph. First format it to the desired widths. 
    # If not in table cell, write it immediately. If in the cell,
    # add it to the list for this cell after formatting.
    #
    #--------------------------------------------------------------------
    def end_paragraph(self):
        self.buffer.insert_with_tags_by_name(
            self.buffer.get_end_iter(),
            self.text + "\n",
            self.style_name)

    #--------------------------------------------------------------------
    #
    # Start a table. Grab the table style, and store it. 
    #
    #--------------------------------------------------------------------
    def start_table(self,name,style_name):
        return
        styles = self.get_style_sheet()
        self.tbl_style = styles.get_table_style(style_name)
        self.ncols = self.tbl_style.get_columns()

    #--------------------------------------------------------------------
    #
    # End a table. Turn off the self.in_cell flag
    #
    #--------------------------------------------------------------------
    def end_table(self):
        return
        self.in_cell = 0

    #--------------------------------------------------------------------
    #
    # Start a row. Initialize lists for cell contents, number of lines,
    # and the widths. It is necessary to keep a list of cell contents
    # that is to be written after all the cells are defined.
    #
    #--------------------------------------------------------------------
    def start_row(self):
        return

        self.cellpars = [''] * self.ncols
        self.cell_lines = [0] * self.ncols
        self.cell_widths = [0] * self.ncols
        self.cellnum = -1
        self.maxlines = 0
        table_width = self.get_usable_width() * self.tbl_style.get_width() / 100.0
        for cell in range(self.ncols):
            self.cell_widths[cell] = int( table_width * \
                                self.tbl_style.get_column_width(cell) / 100.0 )

    #--------------------------------------------------------------------
    #
    # End a row. Write the cell contents. Write the line of spaces
    # if the cell has fewer lines than the maximum number.
    #
    #--------------------------------------------------------------------
    def end_row(self):
        return

        self.in_cell = 0
        cell_text = [None]*self.ncols
        for cell in range(self.ncols):
            if self.cell_widths[cell]:
                blanks = ' '*self.cell_widths[cell] + '\n'
                if self.cell_lines[cell] < self.maxlines:
                    self.cellpars[cell] = self.cellpars[cell] \
                              + blanks * (self.maxlines-self.cell_lines[cell])
                cell_text[cell] = self.cellpars[cell].split('\n')
        for line in range(self.maxlines):
            for cell in range(self.ncols):
                if self.cell_widths[cell]:
                    self.f.write(cell_text[cell][line])
            self.f.write('\n')

    #--------------------------------------------------------------------
    #
    # Start a cell. Set the self.in_cell flag, increment the curren cell number.
    #
    #--------------------------------------------------------------------
    def start_cell(self,style_name,span=1):
        return

        self.in_cell = 1
        self.cellnum = self.cellnum + span
        span = span - 1
        while span:
            self.cell_widths[self.cellnum-span] = 0
            span = span - 1
            
    #--------------------------------------------------------------------
    #
    # End a cell. Find out the number of lines in this cell, correct
    # the maximum number of lines if necessary.
    #
    #--------------------------------------------------------------------
    def end_cell(self):
        return

        self.in_cell = 0
        self.cell_lines[self.cellnum] = self.cellpars[self.cellnum].count('\n')
        if self.cell_lines[self.cellnum] > self.maxlines:
            self.maxlines = self.cell_lines[self.cellnum]

    def add_media_object(self, name, align, w_cm, h_cm):
        return

        this_text = '(photo)'
        if self.in_cell:
            self.cellpars[self.cellnum] = self.cellpars[self.cellnum] + this_text
        else:
            self.f.write(this_text)

    def write_note(self,text,format,style_name):
        return

        if format == 1:
            for line in text.split('\n'):
                self.start_paragraph(style_name)
                self.write_text(line)
                self.end_paragraph()
        elif format == 0:
            for line in text.split('\n\n'):
                self.start_paragraph(style_name)
                line = line.replace('\n',' ')
                line = ' '.join(line.split())
                self.write_text(line)
                self.end_paragraph()

    #--------------------------------------------------------------------
    #
    # Writes text. 
    #--------------------------------------------------------------------
    def write_text(self,text,mark=None):
        self.text = self.text + text

#------------------------------------------------------------------------
#
# Register the document generator with the GRAMPS plugin system
#
#------------------------------------------------------------------------
print_label = None
register_text_doc(_("TextBuffer"), TextBufDoc, 1, 1, 1, ".xyz", None)

