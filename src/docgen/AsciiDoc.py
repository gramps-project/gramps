#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
import BaseDoc
from PluginUtils import register_text_doc
import Errors
import Mime

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------
LEFT,RIGHT,CENTER = 'LEFT','RIGHT','CENTER'
_WIDTH_IN_CHARS = 72

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
def reformat_para(para='',left=0,right=72,just=LEFT,right_pad=0,first=0):
    if not para.strip():
        return "\n"
    words = para.split()
    lines = []
    line  = ''
    word = 0
    end_words = 0
    real_left = left+first
    while not end_words:
        if len(words[word]) > right-real_left: # Handle very long words
            line = words[word]
            word +=1
            if word >= len(words):
                end_words = 1
        else:                             # Compose line of words
            while len(line)+len(words[word]) <= right-real_left:
                line += words[word]+' '
                word += 1
                if word >= len(words):
                    end_words = 1
                    break
        lines.append(line)
        real_left = left
        line = ''
    if just==CENTER:
        if right_pad:
            return '\n'.join(
                [' '*(left+first) + ln.center(right-left-first)
                 for ln in lines[0:1] ] +
                [ ' '*left + ln.center(right-left) for ln in lines[1:] ]
                )
        else:
            return '\n'.join(
                [' '*(left+first) + ln.center(right-left-first).rstrip()
                 for ln in lines[0:1] ] +
                [' '*left + ln.center(right-left).rstrip()
                 for ln in lines[1:] ]
                )
    elif just==RIGHT:
        if right_pad:
            return '\n'.join([line.rjust(right) for line in lines])
        else:
            return '\n'.join([line.rjust(right).rstrip() for line in lines])
    else: # left justify 
        if right_pad:
            return '\n'.join(
                [' '*(left+first) + line.ljust(right-left-first)
                 for line in lines[0:1] ] +
                [' '*left + line.ljust(right-left) for line in lines[1:] ]
                )
        else:
            return '\n'.join(
                [' '*(left+first) + line for line in lines[0:1] ] +
                [' '*left + line for line in lines[1:] ]
                )

#------------------------------------------------------------------------
#
# Ascii
#
#------------------------------------------------------------------------
class AsciiDoc(BaseDoc.BaseDoc):

    #--------------------------------------------------------------------
    #
    # Opens the file, resets the text buffer.
    #
    #--------------------------------------------------------------------
    def open(self,filename):
        if filename[-4:] != ".txt":
            self.filename = filename + ".txt"
        else:
            self.filename = filename

        try:
            self.f = open(self.filename,"w")
        except IOError,msg:
            errmsg = "%s\n%s" % (_("Could not create %s") % self.filename, msg)
            raise Errors.ReportError(errmsg)
        except:
            raise Errors.ReportError(_("Could not create %s") % self.filename)

        self.in_cell = 0
        self.text = ""

    #--------------------------------------------------------------------
    #
    # Close the file. Call the app if required. 
    #
    #--------------------------------------------------------------------
    def close(self):
        self.f.close()

        if self.print_req:
            apptype = 'text/plain'
            prog = Mime.get_application(apptype)
            os.environ["FILE"] = self.filename
            os.system ('%s "$FILE" &' % prog[0])

    def get_usable_width(self):
        return _WIDTH_IN_CHARS

    #--------------------------------------------------------------------
    #
    # Force a section page break
    #
    #--------------------------------------------------------------------
    def end_page(self):
        self.f.write('\012')

    #--------------------------------------------------------------------
    #
    # Force a line break
    #
    #--------------------------------------------------------------------
    def line_break(self):
        if self.in_cell:
            self.cellpars[self.cellnum] = self.cellpars[self.cellnum] + '\n'
        else:
            self.f.write('\n')

    def start_superscript(self):
        if self.in_cell:
            self.cellpars[self.cellnum] = self.cellpars[self.cellnum] + '['
        else:
            self.f.write('[')

    def end_superscript(self):
        if self.in_cell:
            self.cellpars[self.cellnum] = self.cellpars[self.cellnum] + ']'
        else:
            self.f.write(']')

    #--------------------------------------------------------------------
    #
    # Starts a paragraph. 
    #
    #--------------------------------------------------------------------
    def start_paragraph(self,style_name,leader=None):
        self.p = self.style_list[style_name]
        self.leader = leader

    #--------------------------------------------------------------------
    #
    # End a paragraph. First format it to the desired widths. 
    # If not in table cell, write it immediately. If in the cell,
    # add it to the list for this cell after formatting.
    #
    #--------------------------------------------------------------------
    def end_paragraph(self):
        if self.p.get_alignment() == BaseDoc.PARA_ALIGN_RIGHT:
            fmt = RIGHT
        elif self.p.get_alignment() == BaseDoc.PARA_ALIGN_CENTER:
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
        if self.p.get_left_margin():
            regular_indent = int(4*self.p.get_left_margin())
        if self.p.get_first_indent():
            first_indent = int(4*self.p.get_first_indent())

        if self.in_cell and self.cellnum < self.ncols - 1:
            right_pad = 1
            the_pad = ' '*right
        else:
            right_pad = 0
            the_pad = ''

        # Depending on the leader's presence, treat the first line differently
        if self.leader:
            # If we have a leader then we need to reformat the text
            # as if there's no special treatment for the first line.
            # Then add leader and eat up the beginning of the first line pad.
            start_at = regular_indent + min(len(self.leader)+first_indent,0)
            this_text = reformat_para(self.text,regular_indent,right,fmt,
                                      right_pad)
            this_text = ' '*(regular_indent+first_indent) + \
                        self.leader + this_text[start_at:]
        else:
            # If no leader then reformat the text according to the first
            # line indent, as specified by style.
            this_text = reformat_para(self.text,regular_indent,right,fmt,
                                      right_pad,first_indent)
        
        this_text += '\n' + the_pad + '\n' 
        
        if self.in_cell:
            self.cellpars[self.cellnum] = self.cellpars[self.cellnum] + \
                                          this_text
        else:
            self.f.write(this_text)
            
        self.text = ""

    #--------------------------------------------------------------------
    #
    # Start a table. Grab the table style, and store it. 
    #
    #--------------------------------------------------------------------
    def start_table(self,name,style_name):
        self.tbl_style = self.table_styles[style_name]
        self.ncols = self.tbl_style.get_columns()

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
        self.in_cell = 0
        self.cell_lines[self.cellnum] = self.cellpars[self.cellnum].count('\n')
        if self.cell_lines[self.cellnum] > self.maxlines:
            self.maxlines = self.cell_lines[self.cellnum]

    def add_photo(self,name,pos,x,y):
        this_text = '(photo)'
        if self.in_cell:
            self.cellpars[self.cellnum] = self.cellpars[self.cellnum] + this_text
        else:
            self.f.write(this_text)

    def write_note(self,text,format,style_name):
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
    def write_text(self,text):
        text = text.replace('<super>','[')
        text = text.replace('</super>',']')
        self.text = self.text + text

#------------------------------------------------------------------------
#
# Register the document generator with the GRAMPS plugin system
#
#------------------------------------------------------------------------
print_label = None
try:
    import Utils

    mprog = Mime.get_application("text/plain")
    mtype = Mime.get_description('text/plain')

    if Utils.search_for(mprog[0]):
        print_label=_("Open in %s") % mprog[1]
    else:
        print_label=None

    register_text_doc(mtype,AsciiDoc,1,1,1,".txt", print_label)
except:
    register_text_doc(_("Plain Text"),AsciiDoc,1,1,1,".txt", None)

