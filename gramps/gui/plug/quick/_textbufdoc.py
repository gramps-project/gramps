#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly
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

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gi.repository import Gtk
from gi.repository import Pango, PangoCairo

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.plug.docgen import (BaseDoc, TextDoc, FONT_SERIF, PARA_ALIGN_RIGHT,
                        FONT_SANS_SERIF, FONT_MONOSPACE, PARA_ALIGN_CENTER,
                        PARA_ALIGN_LEFT)
from ...managedwindow import ManagedWindow

RESOLUTION = PangoCairo.font_map_get_default().get_resolution()

def pixels(cm):
    return int (RESOLUTION/2.54 * cm)

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------
LEFT,RIGHT,CENTER = 'LEFT','RIGHT','CENTER'
_WIDTH_IN_CHARS = 72

class DisplayBuf(ManagedWindow):
    def __init__(self, title, document, track=[]):
        self.title = title
        ManagedWindow.__init__(self, document.uistate, track, document)
        dialog = Gtk.Dialog(title="", destroy_with_parent=True)
        dialog.add_button(_('_Close'), Gtk.ResponseType.CLOSE)
        self.set_window(dialog, None, title)
        self.setup_configs('interface.' + title.lower().replace(' ', ''),
                           600, 400)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC,Gtk.PolicyType.AUTOMATIC)
        document.text_view = Gtk.TextView()
        document.text_view.set_buffer(document.buffer)
        self.window.connect('response', self.close)
        scrolled_window.add(document.text_view)
        self.window.vbox.pack_start(scrolled_window, True, True, 0)
        self.show()  # should use ManagedWindow version of show

    def build_menu_names(self, obj):
        return ('View', _('Quick View'))

    def get_title(self):
        return self.title

class DocumentManager:
    def __init__(self, title, document, text_view):
        self.title = title
        self.document = document
        document.text_view = text_view
        text_view.set_buffer(document.buffer)

#------------------------------------------------------------------------
#
# TextBuf
#
#------------------------------------------------------------------------
class TextBufDoc(BaseDoc, TextDoc):

    #--------------------------------------------------------------------
    #
    # Opens the file, resets the text buffer.
    #
    #--------------------------------------------------------------------
    def open(self, filename, container=None):
        self.has_data = True
        self.tag_table = Gtk.TextTagTable()

        sheet = self.get_style_sheet()

        for name in sheet.get_paragraph_style_names():
            tag = Gtk.TextTag(name=name)

            style = sheet.get_paragraph_style(name)
            font = style.get_font()
            if font.get_type_face() == FONT_SERIF:
                tag.set_property("family", "Serif")
            elif font.get_type_face() == FONT_SANS_SERIF:
                tag.set_property("family", "Sans")
            elif font.get_type_face() == FONT_MONOSPACE:
                tag.set_property("family", "MonoSpace")

            tag.set_property("size-points", float(font.get_size()))
            if font.get_bold():
                tag.set_property("weight", Pango.Weight.BOLD)
            if style.get_alignment() == PARA_ALIGN_RIGHT:
                tag.set_property("justification", Gtk.Justification.RIGHT)
            elif style.get_alignment() == PARA_ALIGN_LEFT:
                tag.set_property("justification", Gtk.Justification.LEFT)
            elif style.get_alignment() == PARA_ALIGN_CENTER:
                tag.set_property("justification", Gtk.Justification.CENTER)
            else:
                tag.set_property("justification", Gtk.Justification.FILL)

            if font.get_italic():
                tag.set_property("style", Pango.Style.ITALIC)

            if style.get_first_indent():
                tag.set_property("indent", pixels(style.get_first_indent()))
                #tag.set_property("tabs", [pixels(abs(style.get_first_indent()))])

            tag.set_property("left-margin", pixels(style.get_left_margin()))
            tag.set_property("right-margin", pixels(style.get_right_margin()))
            tag.set_property("pixels-above-lines", pixels(style.get_top_margin()))
            tag.set_property("pixels-below-lines", pixels(style.get_bottom_margin()))
            tag.set_property("wrap-mode", Gtk.WrapMode.WORD)

            new_tabs = style.get_tabs()

            tab_array = Pango.TabArray.new(initial_size=len(new_tabs)+1,
                                            positions_in_pixels=True)
            index = 0
            for tab in map(pixels, new_tabs):
                tab_array.set_tab(index, Pango.TabAlign.LEFT, tab)
                index += 1
            tag.set_property("tabs", tab_array)

            self.tag_table.add(tag)
        self.buffer = Gtk.TextBuffer.new(self.tag_table)
        if container:
            return DocumentManager(_('Quick View'), self, container)
        else:
            DisplayBuf(_('Quick View'), self, track=self.track)
            return

    #--------------------------------------------------------------------
    #
    # Close the file. Call the app if required.
    #
    #--------------------------------------------------------------------
    def close(self):
        pass

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
    def start_table(self, name,style_name):
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
        span -= 1
        while span:
            self.cell_widths[self.cellnum-span] = 0
            span -= 1

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

    def add_media(self, name, align, w_cm, h_cm, alt=''):
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

