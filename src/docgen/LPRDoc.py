#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
#
# Modifications and feature additions:
#               2002  Donald A. Peterson
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

# Written by Billy C. Earney, 2003-2004
# Modified by Alex Roitman, 2004

# $Id$

"""LPR document generator"""

#------------------------------------------------------------------------
#
# python modules 
#
#------------------------------------------------------------------------
import string

import pygtk
 
import gnomeprint, gnomeprint.ui, gtk
#------------------------------------------------------------------------
#
# gramps modules 
#
#------------------------------------------------------------------------
import BaseDoc
import Plugins
import ImgManip
from gettext import gettext as _

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------

# Spacing in points (distance between the bottoms of two adjacent lines)
_LINE_SPACING = 20  

# Font constants -- specific for gnome-print
_FONT_SANS_SERIF    = "Arial"
_FONT_SERIF         = "Times New Roman"
_FONT_MONOSPACE     = "Courier New"
_FONT_BOLD          = "Bold"
_FONT_ITALIC        = "Italic"
_FONT_BOLD_ITALIC   = "Bold Italic"
_FONT_REGULAR       = "Regular"

# Formatting directive constants
_LINE_BREAK = "Break"
_BOLD       = "Bold"
_SUPER      = "Super"

#------------------------------------------------------------------------
#
# Units conversion
#
#------------------------------------------------------------------------
def cm2u(cm):
    """
    Convert cm to gnome-print units
    """
    return cm * 72.0 / 2.54 

#------------------------------------------------------------------------
#
# font lookup function
#
#------------------------------------------------------------------------
def find_font_from_fontstyle(fontstyle):
    """
    This function returns the gnomeprint.Font() object instance
    corresponding to the parameters of BaseDoc.FontStyle() object.
    
    fontstyle       - a BaseDoc.FontStyle() instance
    """

    if fontstyle.get_type_face() == BaseDoc.FONT_SANS_SERIF:
        face = _FONT_SANS_SERIF
    elif fontstyle.get_type_face() == BaseDoc.FONT_SERIF:
        face = _FONT_SERIF
    elif fontstyle.get_type_face() == BaseDoc.FONT_MONOSPACE:
        face = _FONT_MONOSPACE
        
    if fontstyle.get_bold():
        modifier = _FONT_BOLD
        if fontstyle.get_italic():
            modifier = _FONT_BOLD_ITALIC
    elif fontstyle.get_italic():
        modifier = _FONT_ITALIC
    else:
        modifier = _FONT_REGULAR

    size = fontstyle.get_size()
    
    return gnomeprint.font_find_closest("%s %s" % (face, modifier),size)

#------------------------------------------------------------------------
#
# basic font-specific text formatting functions
#
#------------------------------------------------------------------------
def get_text_width(text,fontstyle):
    """
    This function returns the width of text using given fontstyle 
    when not formatted.
    
    text            - a text whose width to find
    fontstyle       - a BaseDoc.FontStyle() instance
    """
    font = find_font_from_fontstyle(fontstyle)
    return font.get_width_utf8(text)

def get_text_height(text, width, fontstyle):
    """
    This function returns the height of text using given fontstyle 
    when formatted to specified width.
    
    text            - a text whose height to find
    width           - formatting width
    fontstyle       - a BaseDoc.FontStyle() instance
    """

    nlines = 0

    if text and width > get_text_width(text,fontstyle):
        nlines += 1
    elif width <= get_text_width(text,fontstyle):
        #divide up text and print
        textlist = string.split(text)
        the_text = ""
        for element in textlist:
            if get_text_width(the_text + element + " ",fontstyle) < width:
                the_text = the_text + element + " "
            else:
                #__text contains as many words as this __width allows
                nlines = nlines + 1
                the_text = element + " "

    return nlines * _LINE_SPACING

def get_min_width(text,fontstyle):
    """
    This function returns the minimal width of text using given fontstyle. 
    This is actually determined by the width of the longest word.
    
    text            - a text whose width to find
    fontstyle       - a BaseDoc.FontStyle() instance
    """
    max_word_size = 0
    for word in text.split():
        length = get_text_width(word,fontstyle)
        if length > max_word_size:
           max_word_size = length

    return max_word_size

#------------------------------------------------------------------------
#
# add to paragraph taking care of the newline characters
#
#------------------------------------------------------------------------
def append_to_paragraph(paragraph,directive,text):
    """
    Add a piece to the paragraph while 
    taking care of the newline characters.

    paragraph       - a GnomePrintParagraph() instance
    directive       - what to do with this piece
    text            - the text of the corresponding piece
    """
    if not directive and not text:
        return
    text_list = text.split('\n')
    for the_text in text_list[:-1]:
        paragraph.add_piece(directive,the_text)
        paragraph.add_piece(_LINE_BREAK,"")
    paragraph.add_piece(directive,text_list[-1:][0])

#------------------------------------------------------------------------
#
# Paragraph class
#
#------------------------------------------------------------------------
class GnomePrintParagraph:
    """
    A paragraph abstraction which provides the means for in-paragraph
    formatting.
    """
    
    def __init__(self,paragraph_style):
        """
        Creates a GnomePrintParapgrah instance. 
        
        paragraph_style - an instance of BaseDoc paragraph style object
        """
        self.style = paragraph_style
        self.fontstyle = self.style.get_font()
        self.piece_list = []
        self.lines = []
        self.height = None

    def add_piece(self,directive,text):
        """
        Add a piece to the paragraph.
        
        directive   - what to do with this piece
        text        - the text of the corresponding piece
        """
        self.piece_list.append((directive,text))
    
    def get_piece_list(self):
        """
        Return a list of pieces for the paragraph.
        """
        return self.piece_list

    def get_fontstyle(self):
        """
        Return fontstyle for the paragraph
        """
        return self.fontstyle

    def get_alignment(self):
        """
        Return requested alignment of the paragraph
        """
        return self.style.get_alignment()

    def get_width(self):
        """
        Determine the width of the paragraph if not formatted.
        """
        width = 0
        
        for (directive,text) in self.piece_list:
            fontstyle = BaseDoc.FontStyle(self.fontstyle)
            if directive == _BOLD:
                fontstyle.set_bold(1)
            elif directive == _SUPER:
                size = fontstyle.get_size()
                fontstyle.set_size(size-2)
            
            font = find_font_from_fontstyle(fontstyle)
            width += font.get_width_utf8(text)
        
        return width

    def get_min_width(self):
        """
        Determine the minimal width of the paragraph (longest word)
        """
        max_word_size = 0
        
        for (directive,text) in self.piece_list:
            fontstyle = BaseDoc.FontStyle(self.fontstyle)
            if directive == _BOLD:
                fontstyle.set_bold(1)
            elif directive == _SUPER:
                size = fontstyle.get_size()
                fontstyle.set_size(size-2)

            for word in text.split():
                length = get_text_width(word,fontstyle)
                if length > max_word_size:
                    max_word_size = length

        return max_word_size

    def get_height(self,width):
        """
        Determine the height the paragraph would have
        if formatted for a given width.
        
        width       - required formatting width
        """
        if not self.lines:
            self.format(width)
        return self.height

    def format(self,width):
        """
        Format the paragraph for a given width.
        This is a complex procedure. It assembles lines from the paragraph's
        pieces. It also sets the height of the whole paragraph and
        the widths available after the lines are assembled.
        
        width       - required formatting width
        """

        if self.lines:
            return

        nlines = 1
        avail_width = width

        start_piece = end_piece = start_word = end_word = 0
        
        for piece_num in range(len(self.piece_list)):
            end_piece = piece_num

            (directive,text) = self.piece_list[piece_num]

            fontstyle = BaseDoc.FontStyle(self.fontstyle)
            if directive == _BOLD:
                fontstyle.set_bold(1)
            elif directive == _SUPER:
                size = fontstyle.get_size()
                fontstyle.set_size(size-2)
            
            if text and avail_width > get_text_width(text,fontstyle):
                avail_width -= get_text_width(text,fontstyle)
                end_word = len(text.split())
            elif directive == _LINE_BREAK:
                nlines += 1
                end_word = 0
                self.lines.append((start_piece,start_word,end_piece,end_word,avail_width))
                avail_width = width
                start_piece = end_piece
                start_word = 0
            elif text and avail_width <= get_text_width(text,fontstyle):
                # divide up text
                textlist = text.split()
                the_text = ""
                for word_num in range(len(textlist)):
                    word = textlist[word_num]
                    if get_text_width(the_text + word + " ",fontstyle) <= avail_width:
                        the_text = the_text + word + " "
                    else:
                        # the_text contains as much as avail_width allows
                        nlines += 1
                        end_word = word_num
                        avail_width -= get_text_width(the_text,fontstyle)
                        self.lines.append((start_piece,start_word,end_piece,end_word,avail_width))
                        avail_width = width
                        the_text = word + " "
                        start_piece = end_piece
                        start_word = word_num
                        
                # if the_text still contains data, we will want to print it out
                if the_text:
                    avail_width = width - get_text_width(the_text,fontstyle)
                    end_word = len(textlist)

        self.lines.append((start_piece,start_word,end_piece,end_word,avail_width))
        self.height = nlines * _LINE_SPACING
    

#------------------------------------------------------------------------
#
# LPRDoc class
#
#------------------------------------------------------------------------
class LPRDoc(BaseDoc.BaseDoc):
    """Gnome-print document interface class. Derived from BaseDoc"""
    
    def open(self,filename):
        """Sets up initialization"""
        #set up variables needed to keep track of which state we are in
        self.__in_table = 0
        self.__in_cell = 0
        self.__page_count = 0
        self.__page_open = 0
        
        self.paragraph = None
        self.__cell_data = []
        self.__table_data = []

        #create main variables for this print job
        self.__job = gnomeprint.Job(gnomeprint.config_default())
        self.__pc = self.__job.get_context()

        #find out what the width and height of the page is
        width, height = gnomeprint.job_get_page_size_from_config(self.__job.get_config())

        self.left_margin = cm2u(self.get_left_margin()) 
        self.right_margin = width - cm2u(self.get_right_margin()) 
        self.top_margin = height - cm2u(self.get_top_margin()) 
        self.bottom_margin = cm2u(self.get_bottom_margin()) 

        self.start_page(self)
 

    def close(self):
        """Clean up and close the document"""
        #gracefully end page before we close the doc if a page is open
        if self.__page_open:
           self.end_page()

        self.__job.close()
        self.__show_print_dialog()

    def line_break(self):
        "Forces a line break within a paragraph"
        # Add previously held text to the paragraph, 
        # then add line break directive, 
        # then start accumulating further text 
        append_to_paragraph(self.paragraph,self.__paragraph_directive,self.__paragraph_text)
        self.paragraph.add_piece(_LINE_BREAK,"")
        self.__paragraph_text = ""

    def page_break(self):
        "Forces a page break, creating a new page"
        # If we're already at the very top, relax and do nothing
        if self.__y != self.top_margin:
            self.end_page()
            self.start_page()
                                                                                
    def start_page(self,orientation=None):
        """Create a new page"""
        #reset variables dealing with opening a page
        if (self.__page_open):
            self.end_page()

        self.__page_open = 1
        self.__page_count += 1
        self.__x = self.left_margin
        self.__y = self.top_margin
        
        self.__pc.beginpage(str(self.__page_count))
        self.__pc.moveto(self.__x, self.__y)

    def end_page(self):
        """Close the current page"""
        if (self.__page_open):
            self.__page_open = 0
            self.__pc.showpage()

    def start_paragraph(self,style_name,leader=None):
        """Paragraphs handling - A Gramps paragraph is any 
        single body of text, from a single word, to several sentences.
        We assume a linebreak at the end of each paragraph."""
        # Instantiate paragraph object and initialize buffers
        self.paragraph = GnomePrintParagraph(self.style_list[style_name])
        self.__paragraph_directive = ""
        self.__paragraph_text = ""
        if leader:
            self.__paragraph_text += leader + " "
    
    def end_paragraph(self):
        """End the current paragraph"""
        # Add current text/directive to paragraoh,
        # then either add paragrah to the list of cell's paragraphs
        # or print it right away if not in cell
        append_to_paragraph(self.paragraph,self.__paragraph_directive,self.__paragraph_text)
        if self.__in_cell:
            # We're inside cell. Add paragrah to celldata
            self.__cell_data.append(self.paragraph)
        else:
            # paragraph not in table: write it right away
            self.__x, self.__y = self.write_paragraph(self.paragraph,
                                        self.__x, self.__y, 
                                        self.right_margin - self.left_margin)
            self.__y = self.__advance_line(self.__y)
        self.paragraph = None
            
    def start_bold(self):
        """Bold face"""
        append_to_paragraph(self.paragraph,self.__paragraph_directive,self.__paragraph_text)
        self.__paragraph_directive = _BOLD
        self.__paragraph_text = ""
        
    def end_bold(self):
        """End bold face"""
        append_to_paragraph(self.paragraph,self.__paragraph_directive,self.__paragraph_text)
        self.__paragraph_directive = ""
        self.__paragraph_text = ""

    def start_superscript(self):
        append_to_paragraph(self.paragraph,self.__paragraph_directive,self.__paragraph_text)
        self.__paragraph_directive = _SUPER
        self.__paragraph_text = ""
                                                                                
    def end_superscript(self):
        append_to_paragraph(self.paragraph,self.__paragraph_directive,self.__paragraph_text)
        self.__paragraph_directive = ""
        self.__paragraph_text = ""
                                                                                
    def start_listing(self,style_name):
        """
        Starts a new listing block, using the specified style name.
                                                                                
        style_name - name of the ParagraphStyle to use for the block.
        """
        pass
                                                                                
    def end_listing(self):
        pass
                                                                                
    def start_table(self,name,style_name):
        """Begin new table"""
        # initialize table, compute its width, find number of columns
        self.__table_data = []
        self.__in_table = 1
        self.__tbl_style = self.table_styles[style_name]
        self.__ncols = self.__tbl_style.get_columns()
        self.rownum = -1
        self.__table_width = (self.right_margin - self.left_margin) * \
                            self.__tbl_style.get_width() / 100.0
        self.__cell_widths = []

    def end_table(self):
        """Close the table environment"""
        # output table contents
        self.__output_table()
        self.__in_table = 0
        self.__y = self.__advance_line(self.__y)

    def start_row(self):
        """Begin a new row"""
        # Initialize row, compute cell widths
        self.__row_data = []
        self.rownum = self.rownum + 1
        self.cellnum = -1
        self.__span = 1
        self.__cell_widths.append([0] * self.__ncols)
        for cell in range(self.__ncols):
            self.__cell_widths[self.rownum][cell] = self.__table_width * \
                            self.__tbl_style.get_column_width(cell) / 100.0

    def end_row(self):
        """End the row (new line)"""
        # add row data to the data we have for the current table
        self.__table_data.append(self.__row_data)
            
    def start_cell(self,style_name,span=1):
        """Add an entry to the table."""
        # Initialize a cell, take care of span>1 cases
        self.__in_cell = 1
        self.__cell_data = []
        self.cellnum = self.cellnum + self.__span
        self.__span = span
        for __extra_cell in range(1,span):
            self.__cell_widths[self.rownum][self.cellnum] += \
                self.__cell_widths[self.rownum][self.cellnum + __extra_cell]
            self.__cell_widths[self.rownum][self.cellnum + __extra_cell] = 0
 
    def end_cell(self):
        """Prepares for next cell"""
        # append the cell text to the row data
        self.__in_cell = 0
        self.__row_data.append(self.__cell_data)

    def add_photo(self,name,pos,x,y):
        """Add photo to report"""
        pass

    def horizontal_line(self):
        self.__pc.moveto(self.__x, self.__y)
        self.__pc.lineto(self.right_margin, self.__y)

    def write_cmdstr(self,text):
        """
        Writes the text in the current paragraph. Should only be used after a
        start_paragraph and before an end_paragraph.
                                                                                
        text - text to write.
        """
        pass
#        if not self.paragraph:
#           self.start_paragraph()
#       
#        self.write(text)    
                                                                                
    def draw_arc(self,style,x1,y1,x2,y2,angle,extent):
        pass
                                                                                
    def draw_path(self,style,path):
        pass
                                                                                
    def draw_box(self,style,text,x,y):
        box_style = self.draw_styles[style]
        para_style = box_style.get_paragraph_style()
        fontstyle = para_style.get_font()
        
        #assuming that we start drawing box from current position
        __width=x-self.__x
        __height=y-self.__y
        self.__pc.rect_stroked(self.__x, self.__y) 

        if text != None:
           __text_width=self.__get_text_width(text,fontstyle)
           #try to center text in box
           self.__pc.setfont(find_font_from_fontstyle(fontstyle))
           self.__pc.moveto(self.__x+(__width/2)-(__text_width/2),
                            self.__y+(__height/2))
           self.__pc.show(text)                                                                       

    def write_at (self, style, text, x, y):
        box_style = self.draw_styles[style]
        para_style = box_style.get_paragraph_style()
        fontstyle = para_style.get_font()

        self.__pc.setfont(find_font_from_fontstyle(fontstyle))
        self.__pc.moveto(x, y)
        self.__pc.show(text)

    def draw_bar(self, style, x1, y1, x2, y2):
        self.__pc.moveto(x1, y1)
        self.__pc.lineto(x2, y2)

    def draw_text(self,style,text,x1,y1):
        box_style = self.draw_styles[style]
        para_style = box_style.get_paragraph_style()
        fontstyle = para_style.get_font()

        self.__pc.setfont(find_font_from_fontstyle(fontstyle))
        self.__pc.moveto(x1,y1)
        self.__pc.show(text)
                                                                                
    def center_text(self,style,text,x1,y1):
        box_style = self.draw_styles[style]
        para_style = box_style.get_paragraph_style()
        fontstyle = para_style.get_font()

        #not sure how x1, y1 fit into this
        #should we assume x1 y1 is the starting location
        #and that the right margin is the right edge?
        __width=self.get_text_width(text)
        __center=self.right_margin-self.left_margin
        __center-=__width/2
        self.__pc.setfont(find_font_from_fontstyle(fontstyle))
        self.__pc.moveto(__center, self.__y)
        self.__pc.show(text)
                                                                                
    def rotate_text(self,style,text,x,y,angle):
        pass
                                                                                
    def draw_line(self,style,x1,y1,x2,y2):
        self.__pc.line_stroked(x1,y1,x2,y2)
                                                                                
    def write_text(self,text):
        """Add the text to the paragraph"""
        # Take care of superscript tags
        super_count = text.count('<super>')
        for num in range(super_count):
            start = text.find('<super>')
            self.__paragraph_text = self.__paragraph_text + text[:start]
            append_to_paragraph(self.paragraph,self.__paragraph_directive,self.__paragraph_text)
            self.__paragraph_text = ""
            text = text[start+7:]

            start = text.find('</super>')
            self.__paragraph_text = self.__paragraph_text + text[:start]
            append_to_paragraph(self.paragraph,_SUPER,self.__paragraph_text)
            self.__paragraph_text = ""
            text = text[start+8:]

        self.__paragraph_text = self.__paragraph_text + text

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
                line = string.join(string.split(line))
                self.write_text(line)
                self.end_paragraph()

    #function to help us advance a line 
    def __advance_line(self, y):
        new_y = y - _LINE_SPACING
        if y < self.bottom_margin:
            x = self.__x
            self.end_page()
            self.start_page()
            new_y = self.__y
            self.__x = x
        return new_y

    def write_paragraph(self,paragraph,x,y,width):
        """
        Write the contents of the paragraph, observing per-piece info.
        
        paragraph   - GnomePrintParagraph instance
        x,y         - coordinates to start at
        left_margin,right_margin - boundaries to obey
        """
        
        if not paragraph.get_piece_list():
            return (x,y)

        left_margin = x
        no_space = 0
        paragraph.format(width)

        if y - _LINE_SPACING < self.bottom_margin:
            self.end_page()
            self.start_page()
            x = left_margin
            y = self.__y

        # Loop over lines which were assembled by paragraph.format()
        for (start_piece,start_word,end_piece,end_word,avail_width) \
                                                    in paragraph.lines:

            if paragraph.get_alignment() == BaseDoc.PARA_ALIGN_CENTER:
                x = x + 0.5 * avail_width
            elif paragraph.get_alignment() == BaseDoc.PARA_ALIGN_RIGHT:
                x = x + avail_width
            elif paragraph.get_alignment() == BaseDoc.PARA_ALIGN_LEFT:
                pass
            elif paragraph.get_alignment() == BaseDoc.PARA_ALIGN_JUSTIFY:
                print "Paragraph justification not supported."
                print "Falling back to left-justified mode."

            # Loop over pieces that constitute the line
            for piece_num in range(start_piece,end_piece+1):
                (directive,text) = paragraph.get_piece_list()[piece_num]
                fontstyle = BaseDoc.FontStyle(paragraph.get_fontstyle())
                if directive == _BOLD:
                    fontstyle.set_bold(1)
                elif directive == _SUPER:
                    size = fontstyle.get_size()
                    fontstyle.set_size(size-2)
                    y = y + 0.25 * _LINE_SPACING

                textlist = text.split()
                if start_piece == end_piece:
                    the_textlist = textlist[start_word:end_word]
                elif piece_num > start_piece and piece_num < end_piece:
                    the_textlist = textlist[:]
                elif piece_num == start_piece:
                    the_textlist = textlist[start_word:]
                elif piece_num == end_piece:
                    the_textlist = textlist[:end_word]

                the_text = string.join(the_textlist)
                if piece_num == start_piece \
                                or directive == _SUPER \
                                or no_space \
                                or (the_text and the_text[0] in string.punctuation):
                    spacer = ""
                else:
                    spacer = " "
                the_text = spacer + the_text

                self.__pc.setfont(find_font_from_fontstyle(fontstyle))
                self.__pc.moveto(x, y)
                self.__pc.show(the_text)
                x = x + get_text_width(the_text,fontstyle)
                if directive == _SUPER:
                    y = y - 0.25 * _LINE_SPACING

            # If this was the linebreak, no space on the next line's start
            if end_word:
                no_space = 0
            else:
                no_space = 1

            y = self.__advance_line(y)
            x = left_margin

        return (x,y)

    def __output_table(self):
        """do calcs on data in table and output data in a formatted way"""
        __min_col_size = [0] * self.__ncols
        __max_vspace = [0] * len(self.__table_data)

        for __row_num in range(len(self.__table_data)):
            __row = self.__table_data[__row_num][:]
            #do calcs on each __row and keep track on max length of each column
            for __col in range(self.__ncols):
                if not self.__cell_widths[__row_num][__col]:
                    continue

                __max = 0
                for paragraph in __row[__col]:
                    __min = paragraph.get_min_width()
                    if __min > __min_col_size[__col]:
                        __min_col_size[__col] = __min

                    __max += paragraph.get_height(
                                        self.__cell_widths[__row_num][__col])
                if __max > __max_vspace[__row_num]:
                    __max_vspace[__row_num] = __max

        #is table width larger than the width of the paper?
        __min_table_width = 0
        for __size in __min_col_size:
            __min_table_width = __min_table_width + __size

        if __min_table_width > (self.right_margin - self.left_margin):
            print "Table does not fit onto the page.\n"

        #for now we will assume left justification of tables
        #output data in table
        for __row_num in range(len(self.__table_data)):
            __row = self.__table_data[__row_num]
            # If this row puts us below the bottom, start new page here
            if self.__y - __max_vspace[__row_num] < self.bottom_margin:
                self.end_page()
                self.start_page()

            __x = self.left_margin         #reset so that x is at margin
            col_y = self.__y    # all columns start at the same height
            for __col in range(self.__ncols):
                if not self.__cell_widths[__row_num][__col]:
                    continue
                self.__y = col_y
                for paragraph in __row[__col]:
                    junk, self.__y = self.write_paragraph(paragraph,
                                     __x, self.__y, 
                                     self.__cell_widths[__row_num][__col])

                __x = __x + self.__cell_widths[__row_num][__col]    # set up margin for this row
            self.__y = col_y - __max_vspace[__row_num]

    #function to print text to a printer
    def __do_print(self,dialog, job):
        __pc = gnomeprint.Context(dialog.get_config())
        job.render(__pc)
        __pc.close()
 
    #I believe this is a print preview
    def __show_preview(self, dialog):
         __w = gnomeprint.ui.JobPreview(self.__job, _("Print Preview"))
         __w.set_property('allow-grow', 1)
         __w.set_property('allow-shrink', 1)
         __w.set_transient_for(dialog)
         __w.show_all()
 
    #function used to get users response and do a certain
    #action depending on that response
    def __print_dialog_response(self, dialog, resp, job):
         if resp == gnomeprint.ui.DIALOG_RESPONSE_PREVIEW:
            self.__show_preview(dialog)
         elif resp == gnomeprint.ui.DIALOG_RESPONSE_CANCEL:
            dialog.destroy()
         elif resp == gnomeprint.ui.DIALOG_RESPONSE_PRINT:
            self.__do_print(dialog, self.__job)
            dialog.destroy()

    #function displays a window that allows user to choose 
    #to print, show, etc
    def __show_print_dialog(self):
         __dialog = gnomeprint.ui.Dialog(self.__job, _("Print..."), 0)
         __dialog.connect('response', self.__print_dialog_response, self.__job)
         __dialog.show()

#------------------------------------------------------------------------
#
# Register the document generator with the system
#
#------------------------------------------------------------------------
Plugins.register_text_doc(
    name=_("Print..."),
    classref=LPRDoc,
    table=1,
    paper=1,
    style=1,
    ext=""
    )
