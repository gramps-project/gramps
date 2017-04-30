#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2007-2009  Brian G. Matherly
# Copyright (C) 2009-2010  Benny Malengier <benny.malengier@gramps-project.org>
# Copyright (C) 2010       Peter Landgren
# Copyright (C) 2011       Adam Stein <adam@csh.rit.edu>
# Copyright (C) 2012,2017  Paul Franklin
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
ACSII document generator.
"""

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import DOCGEN_OPTIONS
from gramps.gen.errors import ReportError
from gramps.gen.plug.docgen import (BaseDoc, TextDoc,
                                    PARA_ALIGN_RIGHT, PARA_ALIGN_CENTER)
from gramps.gen.plug.menu import NumberOption
from gramps.gen.plug.report import DocOptions
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------
LEFT, RIGHT, CENTER = 'LEFT', 'RIGHT', 'CENTER'

#------------------------------------------------------------------------
#
# This routine was written by David Mertz and placed into the public
# domain. It is sample code from his book, "Text Processing in Python"
#
# Modified by Alex Roitman: right-pad with spaces, if right_pad==1;
#                           return empty string if no text was given
# Another argument: "first" is the first line indent in characters
#                   _relative_ to the "left" margin. It can be negative!
#
#------------------------------------------------------------------------
def reformat_para(para='', left=0, right=72, just=LEFT, right_pad=0, first=0):
    if not para.strip():
        return "\n"

    lines = []
    real_left = left+first
    alllines = para.split('\n')
    for realline in alllines:
        words = realline.split()
        line = ''
        word = 0
        end_words = 0
        while not end_words:
            if not words:
                lines.append("\n")
                break
            if len(words[word]) > right-real_left: # Handle very long words
                line = words[word]
                word += 1
                if word >= len(words):
                    end_words = 1
            else:                             # Compose line of words
                while len(line)+len(words[word]) <= right-real_left:
                    line += words[word]
                    word += 1
                    if word >= len(words):
                        end_words = 1
                        break
                    elif len(line) < right-real_left:
                        line += ' ' # add a space since there is still room
            lines.append(line)
            #first line finished, discard first
            real_left = left
            line = ''
    if just == CENTER:
        if right_pad:
            return '\n'.join(
                [' '*(left+first) + ln.center(right-left-first)
                 for ln in lines[0:1]] +
                [' '*left + ln.center(right-left) for ln in lines[1:]]
                )
        else:
            return '\n'.join(
                [' '*(left+first) + ln.center(right-left-first).rstrip()
                 for ln in lines[0:1]] +
                [' '*left + ln.center(right-left).rstrip()
                 for ln in lines[1:]]
                )
    elif just == RIGHT:
        if right_pad:
            return '\n'.join([line.rjust(right) for line in lines])
        else:
            return '\n'.join([line.rjust(right).rstrip() for line in lines])
    else: # left justify
        if right_pad:
            return '\n'.join(
                [' '*(left+first) + line.ljust(right-left-first)
                 for line in lines[0:1]] +
                [' '*left + line.ljust(right-left) for line in lines[1:]]
                )
        else:
            return '\n'.join(
                [' '*(left+first) + line for line in lines[0:1]] +
                [' '*left + line for line in lines[1:]]
                )

#------------------------------------------------------------------------
#
# Ascii
#
#------------------------------------------------------------------------
class AsciiDoc(BaseDoc, TextDoc):
    """
    ASCII document generator.
    """
    def __init__(self, styles, paper_style, options=None, uistate=None):
        BaseDoc.__init__(self, styles, paper_style, uistate=uistate)
        self.__note_format = False

        self._cpl = 72 # characters per line, in case the options are ignored
        if options:
            menu = options.menu
            self._cpl = menu.get_option_by_name('linechars').get_value()

        self.file = None
        self.filename = ''

        self.text = ''
        self.para = None
        self.leader = None

        self.tbl_style = None
        self.in_cell = None
        self.ncols = 0
        self.column_order = []
        self.cellpars = []
        self.cell_lines = []
        self.cell_widths = []
        self.cellnum = -1
        self.maxlines = 0

    #--------------------------------------------------------------------
    #
    # Opens the file, resets the text buffer.
    #
    #--------------------------------------------------------------------
    def open(self, filename):
        if filename[-4:] != ".txt":
            self.filename = filename + ".txt"
        else:
            self.filename = filename

        try:
            self.file = open(self.filename, "w", errors='backslashreplace')
        except Exception as msg:
            raise ReportError(_("Could not create %s") % self.filename, msg)

        self.in_cell = 0
        self.text = ""

    #--------------------------------------------------------------------
    #
    # Close the file. Call the app if required.
    #
    #--------------------------------------------------------------------
    def close(self):
        self.file.close()

    def get_usable_width(self):
        """
        Return the usable width of the document in characters.
        """
        return self._cpl

    #--------------------------------------------------------------------
    #
    # Force a section page break
    #
    #--------------------------------------------------------------------
    def page_break(self):
        self.file.write('\012')

    def start_bold(self):
        pass

    def end_bold(self):
        pass

    def start_superscript(self):
        self.text = self.text + '['

    def end_superscript(self):
        self.text = self.text + ']'

    #--------------------------------------------------------------------
    #
    # Starts a paragraph.
    #
    #--------------------------------------------------------------------
    def start_paragraph(self, style_name, leader=None):
        styles = self.get_style_sheet()
        self.para = styles.get_paragraph_style(style_name)
        self.leader = leader

    #--------------------------------------------------------------------
    #
    # End a paragraph. First format it to the desired widths.
    # If not in table cell, write it immediately. If in the cell,
    # add it to the list for this cell after formatting.
    #
    #--------------------------------------------------------------------
    def end_paragraph(self):
        if self.para.get_alignment() == PARA_ALIGN_RIGHT:
            fmt = RIGHT
        elif self.para.get_alignment() == PARA_ALIGN_CENTER:
            fmt = CENTER
        else:
            fmt = LEFT

        if self.in_cell:
            right = self.cell_widths[self.cellnum]
        else:
            right = self.get_usable_width()

        # Compute indents in characters. Keep first_indent relative!
        regular_indent = 0
        first_indent = 0
        if self.para.get_left_margin():
            regular_indent = int(4*self.para.get_left_margin())
        if self.para.get_first_indent():
            first_indent = int(4*self.para.get_first_indent())

        if self.in_cell and self.cellnum < self.ncols - 1:
            right_pad = 1
            the_pad = ' ' * right
        else:
            right_pad = 0
            the_pad = ''

        # Depending on the leader's presence, treat the first line differently
        if self.leader:
            # If we have a leader then we need to reformat the text
            # as if there's no special treatment for the first line.
            # Then add leader and eat up the beginning of the first line pad.
            # Do not reformat if preformatted notes
            if not self.__note_format:
                self.leader += ' '
                start_at = regular_indent + min(len(self.leader)+first_indent,
                                                0)
                this_text = reformat_para(self.text, regular_indent, right, fmt,
                                          right_pad)
                this_text = (' ' * (regular_indent+first_indent) +
                             self.leader +
                             this_text[start_at:]
                            )
            else:
                this_text = self.text
        else:
            # If no leader then reformat the text according to the first
            # line indent, as specified by style.
            # Do not reformat if preformatted notes
            if not self.__note_format:
                this_text = reformat_para(self.text, regular_indent, right, fmt,
                                          right_pad, first_indent)
            else:
                this_text = ' ' * (regular_indent + first_indent) + self.text

        if self.__note_format:
            # don't add an extra LF before the_pad if preformatted notes.
            if this_text != '\n':
                # don't add LF if there is this_text is a LF
                this_text += the_pad + '\n'
        else:
            this_text += '\n' + the_pad + '\n'

        if self.in_cell:
            self.cellpars[self.cellnum] += this_text
        else:
            self.file.write(this_text)

        self.text = ""

    #--------------------------------------------------------------------
    #
    # Start a table. Grab the table style, and store it.
    #
    #--------------------------------------------------------------------
    def start_table(self, name, style_name):
        styles = self.get_style_sheet()
        self.tbl_style = styles.get_table_style(style_name)
        self.ncols = self.tbl_style.get_columns()
        self.column_order = []
        for cell in range(self.ncols):
            self.column_order.append(cell)
        if self.get_rtl_doc():
            self.column_order.reverse()

    #--------------------------------------------------------------------
    #
    # End a table. Turn off the self.in_cell flag
    #
    #--------------------------------------------------------------------
    def end_table(self):
        self.in_cell = 0

    #--------------------------------------------------------------------
    #
    # Start a row. Initialize lists for cell contents, number of lines,
    # and the widths. It is necessary to keep a list of cell contents
    # that is to be written after all the cells are defined.
    #
    #--------------------------------------------------------------------
    def start_row(self):
        self.cellpars = [''] * self.ncols
        self.cell_lines = [0] * self.ncols
        self.cell_widths = [0] * self.ncols
        self.cellnum = -1
        self.maxlines = 0
        table_width = (self.get_usable_width() *
                       self.tbl_style.get_width() / 100.0)
        for cell in self.column_order:
            self.cell_widths[cell] = int(
                table_width * self.tbl_style.get_column_width(cell) / 100.0)

    #--------------------------------------------------------------------
    #
    # End a row. Write the cell contents. Write the line of spaces
    # if the cell has fewer lines than the maximum number.
    #
    #--------------------------------------------------------------------
    def end_row(self):
        self.in_cell = 0
        cell_text = [None]*self.ncols
        for cell in self.column_order:
            if self.cell_widths[cell]:
                blanks = ' '*self.cell_widths[cell] + '\n'
                if self.cell_lines[cell] < self.maxlines:
                    self.cellpars[cell] += blanks * (
                        self.maxlines - self.cell_lines[cell]
                        )
                cell_text[cell] = self.cellpars[cell].split('\n')
        for line in range(self.maxlines):
            for cell in self.column_order:
                if self.cell_widths[cell]:
                    self.file.write(cell_text[cell][line])
            self.file.write('\n')

    #--------------------------------------------------------------------
    #
    # Start a cell. Set the self.in_cell flag,
    # increment the current cell number.
    #
    #--------------------------------------------------------------------
    def start_cell(self, style_name, span=1):
        self.in_cell = 1
        self.cellnum = self.cellnum + span
        span -= 1
        while span:
            self.cell_widths[self.cellnum] += (
                self.cell_widths[self.cellnum-span]
                )
            self.cell_widths[self.cellnum-span] = 0
            span -= 1


    #--------------------------------------------------------------------
    #
    # End a cell. Find out the number of lines in this cell, correct
    # the maximum number of lines if necessary.
    #
    #--------------------------------------------------------------------
    def end_cell(self):
        self.in_cell = 0
        self.cell_lines[self.cellnum] = self.cellpars[self.cellnum].count('\n')
        if self.cell_lines[self.cellnum] > self.maxlines:
            self.maxlines = self.cell_lines[self.cellnum]

    def add_media(self, name, align, w_cm, h_cm, alt='', style_name=None,
                  crop=None):
        this_text = '(photo)'
        if self.in_cell:
            self.cellpars[self.cellnum] += this_text
        else:
            self.file.write(this_text)

    def write_styled_note(self, styledtext, format, style_name,
                          contains_html=False, links=False):
        """
        Convenience function to write a styledtext to the ASCII doc.
        styledtext : assumed a StyledText object to write
        format : = 0 : Flowed, = 1 : Preformatted
        style_name : name of the style to use for default presentation
        contains_html: bool, the backend should not check if html is present.
            If contains_html=True, then the textdoc is free to handle that in
            some way. Eg, a textdoc could remove all tags, or could make sure
            a link is clickable. AsciiDoc prints the html without handling it
        links: bool, make the URL in the text clickable (if supported)
        """
        if contains_html:
            return
        text = str(styledtext)
        if format:
            #Preformatted note, keep all white spaces, tabs, LF's
            self.__note_format = True
            for line in text.split('\n'):
                self.start_paragraph(style_name)
                self.write_text(line)
                self.end_paragraph()
            # Add an extra empty para all lines in each preformatted note
            self.start_paragraph(style_name)
            self.end_paragraph()
            self.__note_format = False
        else:
            for line in text.split('\n\n'):
                self.start_paragraph(style_name)
                #line = line.replace('\n',' ')
                #line = ' '.join(line.split())
                self.write_text(line)
                self.end_paragraph()

    #--------------------------------------------------------------------
    #
    # Writes text.
    #--------------------------------------------------------------------
    def write_text(self, text, mark=None, links=False):
        self.text = self.text + text

#------------------------------------------------------------------------
#
# AsciiDocOptions class
#
#------------------------------------------------------------------------
class AsciiDocOptions(DocOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        DocOptions.__init__(self, name)

    def add_menu_options(self, menu):
        """
        Add options to the document menu for the AsciiDoc docgen.
        """

        category_name = DOCGEN_OPTIONS

        linechars = NumberOption(_('Characters per line'), 72, 20, 9999)
        linechars.set_help(_("The number of characters per line"))
        menu.add_option(category_name, 'linechars', linechars)
