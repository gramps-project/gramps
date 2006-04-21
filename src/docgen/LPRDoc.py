#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
# Modified by Alex Roitman, 2004-2005

# $Id$

"""LPR document generator"""

#------------------------------------------------------------------------
#
# python modules 
#
#------------------------------------------------------------------------
from string import punctuation
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GNOME/GTK Modules 
#
#------------------------------------------------------------------------
import gtk.gdk


try:
    import gnomeprint, gnomeprint.ui
except ImportError:
    raise Errors.UnavailableError(_("Cannot be loaded because python bindinds for GNOME print are not installed"))

### FIXME ###
if gnomeprint.Context.__dict__.has_key('grestore'):
    support_photos = 1
else:
    support_photos = 0
    print "LPRDoc: Photos and rotated text (used in FanChart)"
    print "        are not supported for direct printing."
    print "        Get gnome-python from CVS" 
    print "        or wait for the next gnome-python release."
### end FIXME ###

#------------------------------------------------------------------------
#
# gramps modules 
#
#------------------------------------------------------------------------
import BaseDoc
from PluginUtils import ReportUtils, \
     register_text_doc, register_draw_doc, register_book_doc
rgb_color = ReportUtils.rgb_color

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------

# Spacing in points (distance between the bottoms of two adjacent lines)
_LINE_SPACING = 20  

# Elevation of superscripts: a fraction of it's size
_SUPER_ELEVATION_FRACTION = 0.3

# Number of points to subtract to get the superscrip size
_SUPER_SIZE_REDUCTION = 2

# Factor which multiplies the font size to get line spacing for the font
_EXTRA_SPACING_FACTOR = 1.2

# Grey color to use for box shadows
_SHADOW_COLOR = (192,192,192)

# Font constants -- specific for gnome-print
_TTF_FREEFONT = ( 
('FreeSerif Medium','FreeSerif Bold','FreeSerif Italic','FreeSerif BoldItalic' ),
('FreeSans Medium','FreeSans Bold','FreeSans Oblique','FreeSans BoldOblique'),
('FreeMono Medium','FreeMono Bold','FreeMono Oblique','FreeMono BoldOblique')
                )
_MS_TTFONT = (  
('Times New Roman Regular','Times New Roman Bold','Times New Roman Italic','Times New Roman Bold Italic' ),
('Arial Regular','Arial Bold','Arial Italic','Arial Bold Italic'),
('Courier New Regular','Courier New Bold','Courier New Italic','Courier New Bold Italic')
                )
_GNOME_FONT = ( 
('Serif Regular','Serif Bold','Serif Italic','Serif Bold Italic' ),
('Sans Regular','Sans Bold','Sans Italic','Sans Bold Italic'),
('Monospace Regular','Monospace New Bold','Monospace New Italic','Monospace New Bold Italic')
                )

# Search for ttf-freefont first
ttf_not_found = 0
for family in _TTF_FREEFONT:
    for font in family:
        if font not in gnomeprint.font_list():
            ttf_not_found = 1
            break

if ttf_not_found:
    print "LPRDoc: Free true type fonts not found."
    # Search for MS ttfs
    ms_not_found = 0
    for family in _MS_TTFONT:
        for font in family:
            if font not in gnomeprint.font_list():
                ms_not_found = 1
                break
    if ms_not_found:
        print "        Microsoft true type fonts not found."
        print "        Using Gnome standard fonts."
        print "        Non-ascii characters will appear garbled in the output."
        print "        INSTALL Free true type fonts" 
        print "        from http://www.nongnu.org/freefont/"
        _FONT_SET = _GNOME_FONT
    else:
        print "        Found Microsoft true type fonts. Will use them for now."
        print "        These fonts are not free. "
        print "        You are advised to switch to Free true type fonts"
        print "        INSTALL Free true type fonts" 
        print "        from http://www.nongnu.org/freefont/"
        _FONT_SET = _MS_TTFONT
else:
    _FONT_SET = _TTF_FREEFONT

# Formatting directive constants
_LINE_BREAK = "Break"
_BOLD       = "Bold"
_SUPER      = "Super"
_MONO       = "Mono"
_POSTLEADER = "Postleader"

#------------------------------------------------------------------------
#
# Units conversion
#
#------------------------------------------------------------------------
def cm2u(cm):
    """
    Convert cm to gnome-print units.
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

    if fontstyle.get_type_face() == BaseDoc.FONT_SERIF:
        family = _FONT_SET[0]
    elif fontstyle.get_type_face() == BaseDoc.FONT_SANS_SERIF:
        family = _FONT_SET[1]
    elif fontstyle.get_type_face() == BaseDoc.FONT_MONOSPACE:
        family = _FONT_SET[2]
        
    if fontstyle.get_bold():
        if fontstyle.get_italic():
            font = family[3]
        else:
            font = family[1]
    elif fontstyle.get_italic():
        font = family[2]
    else:
        font = family[0]

    size = fontstyle.get_size()
    return gnomeprint.font_find_closest(font,size)

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
        Return fontstyle for the paragraph.
        """
        return self.fontstyle

    def get_alignment(self):
        """
        Return requested alignment of the paragraph.
        """
        return self.style.get_alignment()

    def get_min_width(self):
        """
        Determine the minimal width of the paragraph (longest word).
        """
        max_word_size = 0
        
        for (directive,text) in self.piece_list:
            fontstyle = BaseDoc.FontStyle(self.fontstyle)
            if directive == _BOLD:
                fontstyle.set_bold(1)
            elif directive == _SUPER:
                size = fontstyle.get_size()
                fontstyle.set_size(size-_SUPER_SIZE_REDUCTION)
            elif directive == _MONO:
                fontstyle.set_type_face(BaseDoc.FONT_MONOSPACE)

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

        width = width   - cm2u(self.style.get_right_margin()) \
                        - cm2u(self.style.get_left_margin())

        nlines = 1
        avail_width = width

        start_piece = end_piece = start_word = end_word = 0
        first = 1
        
        for piece_num in range(len(self.piece_list)):
            end_piece = piece_num

            (directive,text) = self.piece_list[piece_num]

            fontstyle = BaseDoc.FontStyle(self.fontstyle)
            if directive == _BOLD:
                fontstyle.set_bold(1)
            elif directive == _SUPER:
                size = fontstyle.get_size()
                fontstyle.set_size(size-_SUPER_SIZE_REDUCTION)
            elif directive == _MONO:
                fontstyle.set_type_face(BaseDoc.FONT_MONOSPACE)
            
            if first:
                first = 0
                avail_width = avail_width - cm2u(self.style.get_first_indent())

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
        self.height = nlines * self.fontstyle.get_size() \
                      * _EXTRA_SPACING_FACTOR \
                      + cm2u(self.style.get_top_margin()
                             +self.style.get_bottom_margin())
    
    def get_lines(self):
        """
        Return a list of assemlbed lines for the paragraph.

        Each element is a tuple corresponding to the line's contents:
        (start_piece,start_word,end_piece,end_word,avail_width)
        """
        return self.lines

#------------------------------------------------------------------------
#
# Photo class
#
#------------------------------------------------------------------------
class GnomePrintPhoto:
    """
    A photo abstraction which provides the means for correct photo placement.
    Way less complex that paragraph, but still useful. 
    """
    
    def __init__(self,name,pos,x_size,y_size):
        """
        Creates a GnomePrintPhoto instance. 
        """
        self.name = name
        self.alignment = pos
        self.pixbuf = gtk.gdk.pixbuf_new_from_file(name)
        self.height = self.pixbuf.get_height()
        self.width = self.pixbuf.get_width()
        max_size = cm2u(max(x_size,y_size))
        self.scale_x = int(max_size * float(self.width)/max(self.height,
                                                             self.width))
        self.scale_y = int(max_size * float(self.height)/max(self.height,
                                                              self.width))

    def get_image(self):
        """
        Return the raw image of the photo.
        """
        return self.pixbuf.get_pixels()

    def get_has_alpha(self):
        """
        Return has_alpha of the photo.
        """
        return self.pixbuf.get_has_alpha()

    def get_rowstride(self):
        """
        Return the rowstride of the photo.
        """
        return self.pixbuf.get_rowstride()

    def get_height(self,width=None):
        """
        Return the real height of the photo as it should appear on the page.
        """
        return self.scale_y
    
    def get_width(self):
        """
        Return the real width of the photo as it should appear on the page.
        """
        return self.scale_x

    def get_min_width(self):
        """
        Return the minimum width of the photo as it should appear on the page.
        """
        return self.scale_x

    def get_image_height(self):
        """
        Return the height of the photo in terms of image's pixels.
        """
        return self.height
    
    def get_image_width(self):
        """
        Return the width of the photo in terms of image's pixels.
        """
        return self.width

    def get_alignment(self):
        """
        Return the alignment of the photo.
        """
        return self.alignment

#------------------------------------------------------------------------
#
# LPRDoc class
#
#------------------------------------------------------------------------
class LPRDoc(BaseDoc.BaseDoc):
    """Gnome-print document interface class. Derived from BaseDoc."""
    
    #------------------------------------------------------------------------
    #
    # General methods
    #
    #------------------------------------------------------------------------
    def open(self,filename):
        """Sets up initialization."""
        #set up variables needed to keep track of which state we are in
        self.in_table = 0
        self.in_cell = 0
        self.page_count = 0
        self.page_open = 0
        self.brand_new_page = 0        
        self.paragraph = None
        self.cell_data = []
        self.table_data = []

        #create main variables for this print job
        self.job = gnomeprint.Job(gnomeprint.config_default())
        self.gpc = self.job.get_context()

        #find out what the width and height of the page is
        width, height = gnomeprint.job_get_page_size_from_config(
            self.job.get_config())

        self.left_margin = cm2u(self.get_left_margin()) 
        self.right_margin = width - cm2u(self.get_right_margin()) 
        self.top_margin = height - cm2u(self.get_top_margin()) 
        self.bottom_margin = cm2u(self.get_bottom_margin()) 

        self.start_page(self)
        self.filename = ""

    def close(self):
        """Clean up and close the document."""
        #gracefully end page before we close the doc if a page is open
        if self.page_open:
           self.end_page()

        self.job.close()
        self.show_print_dialog()

    def start_page(self,orientation=None):
        """Create a new page."""
        # Don't start new page if it is just started
        if self.brand_new_page:
            return
        #reset variables dealing with opening a page
        if (self.page_open):
            self.end_page()

        self.page_open = 1
        self.page_count += 1
        self.x = self.left_margin
        self.y = self.top_margin
        
        self.gpc.beginpage(str(self.page_count))
        self.gpc.moveto(self.x, self.y)
        self.brand_new_page = 1

    def end_page(self):
        """Close the current page."""
        if (self.page_open):
            self.page_open = 0
            self.gpc.showpage()
        self.brand_new_page = 0

    def page_break(self):
        "Forces a page break, creating a new page."
        # If we're already at the very top, relax and do nothing
        if not self.brand_new_page:
            self.end_page()
            self.start_page()

    #------------------------------------------------------------------------
    #
    # Text methods
    #
    #------------------------------------------------------------------------

    def string_width(self,fontstyle,text):
        "Override generic Fontscale-based width."
        return get_text_width(text,fontstyle)

    def line_break(self):
        "Forces a line break within a paragraph."
        # Add previously held text to the paragraph, 
        # then add line break directive, 
        # then start accumulating further text 
        append_to_paragraph(self.paragraph,self.paragraph_directive,
                            self.paragraph_text)
        self.paragraph.add_piece(_LINE_BREAK,"")
        self.paragraph_text = ""
        self.brand_new_page = 0

    def start_paragraph(self,style_name,leader=None):
        """Paragraphs handling - A Gramps paragraph is any 
        single body of text, from a single word, to several sentences.
        We assume a linebreak at the end of each paragraph."""
        # Instantiate paragraph object and initialize buffers
        self.paragraph = GnomePrintParagraph(self.style_list[style_name])
        if leader:
            append_to_paragraph(self.paragraph,"",leader)
            self.paragraph_directive = _POSTLEADER
        else:
            self.paragraph_directive = ""
        self.paragraph_text = ""
        self.brand_new_page = 0
    
    def end_paragraph(self):
        """End the current paragraph."""
        # Add current text/directive to paragraoh,
        # then either add paragrah to the list of cell's paragraphs
        # or print it right away if not in cell
        append_to_paragraph(self.paragraph,self.paragraph_directive,
                            self.paragraph_text)
        if self.in_cell:
            # We're inside cell. Add paragrah to celldata
            self.cell_data.append(self.paragraph)
        else:
            # paragraph not in table: write it right away
            self.x, self.y = self.write_paragraph(self.paragraph,
                                        self.x, self.y, 
                                        self.right_margin - self.left_margin)
        self.paragraph = None
        self.brand_new_page = 0
            
    def start_bold(self):
        """Bold face."""
        append_to_paragraph(self.paragraph,self.paragraph_directive,
                            self.paragraph_text)
        self.paragraph_directive = _BOLD
        self.paragraph_text = ""
        self.brand_new_page = 0
        
    def end_bold(self):
        """End bold face."""
        append_to_paragraph(self.paragraph,self.paragraph_directive,
                            self.paragraph_text)
        self.paragraph_directive = ""
        self.paragraph_text = ""
        self.brand_new_page = 0

    def start_superscript(self):
        append_to_paragraph(self.paragraph,self.paragraph_directive,
                            self.paragraph_text)
        self.paragraph_directive = _SUPER
        self.paragraph_text = ""
        self.brand_new_page = 0

    def end_superscript(self):
        append_to_paragraph(self.paragraph,self.paragraph_directive,
                            self.paragraph_text)
        self.paragraph_directive = ""
        self.paragraph_text = ""
        self.brand_new_page = 0

    def start_table(self,name,style_name):
        """Begin new table."""
        # initialize table, compute its width, find number of columns
        self.table_data = []
        self.in_table = 1
        self.tbl_style = self.table_styles[style_name]
        self.ncols = self.tbl_style.get_columns()
        self.rownum = -1
        self.table_width = (self.right_margin - self.left_margin) * \
                            self.tbl_style.get_width() / 100.0
        self.cell_widths = []
        self.gp_cell_styles = []
        self.brand_new_page = 0

    def end_table(self):
        """Close the table environment."""
        # output table contents
        self.output_table()
        self.in_table = 0
        self.y = self.advance_line(self.y)
        self.brand_new_page = 0

    def start_row(self):
        """Begin a new row."""
        # Initialize row, compute cell widths
        self.row_data = []
        self.rownum = self.rownum + 1
        self.cellnum = -1
        self.span = 1
        self.cell_widths.append([0] * self.ncols)
        self.gp_cell_styles.append([None] * self.ncols)
        for cell in range(self.ncols):
            self.cell_widths[self.rownum][cell] = self.table_width * \
                            self.tbl_style.get_column_width(cell) / 100.0
        self.brand_new_page = 0

    def end_row(self):
        """End the row (new line)."""
        # add row data to the data we have for the current table
        self.table_data.append(self.row_data)
        self.brand_new_page = 0
            
    def start_cell(self,style_name,span=1):
        """Add an entry to the table."""
        # Initialize a cell, take care of span>1 cases
        self.brand_new_page = 0
        self.in_cell = 1
        self.cell_data = []
        self.cellnum = self.cellnum + self.span
        self.span = span
        self.gp_cell_styles[self.rownum][self.cellnum] = \
                                    self.cell_styles[style_name]
        for extra_cell in range(1,span):
            self.cell_widths[self.rownum][self.cellnum] += \
                self.cell_widths[self.rownum][self.cellnum + extra_cell]
            self.cell_widths[self.rownum][self.cellnum + extra_cell] = 0

    def end_cell(self):
        """Prepares for next cell."""
        # append the cell text to the row data
        self.in_cell = 0
        self.row_data.append(self.cell_data)
        self.brand_new_page = 0

    def add_media_object(self,name,pos,x,y):
        """Add photo to report."""

        photo = GnomePrintPhoto(name,pos,x,y)
        if self.in_cell:
            # We're inside cell. Add photo to celldata
            self.cell_data.append(photo)
        else:
            # photo not in table: write it right away
            self.x, self.y = self.write_photo(photo,
                                        self.x, self.y, 
                                        self.right_margin - self.left_margin)
        self.brand_new_page = 0

    def write_photo(self,photo,x,y,alloc_width):
        """
        Write the photo.

        photo       - GnomePrintPhoto instance
        x,y         - coordinates to start at
        alloc_width - allocated width
        """

        self.brand_new_page = 0
        # FIXME -- remove when gnome-python is released and hits every distro
        if not support_photos:
            return (x,y)
        # end FIXME
        
        width = photo.get_width()
        height = photo.get_height()

        if y - height < self.bottom_margin:
            self.end_page()
            self.start_page()
            y = self.y

        if photo.get_alignment() == 'center':
            add_x = 0.5* (alloc_width - width)
        elif photo.get_alignment() == 'right':
            add_x = alloc_width - width
        else:
            add_x = 0

        self.gpc.gsave()
        self.gpc.translate(x+add_x,y-height)
        self.gpc.scale(width,height)
        
        if photo.get_has_alpha():
            self.gpc.rgbaimage(photo.get_image(), 
                                photo.get_image_width(), 
                                photo.get_image_height(), 
                                photo.get_rowstride())
        else:
            self.gpc.rgbimage(photo.get_image(), 
                                photo.get_image_width(), 
                                photo.get_image_height(), 
                                photo.get_rowstride())

        self.gpc.grestore()
        x = x
        y = y - height
        return (x,y)
                                                                                
    def write_text(self,text):
        """Add the text to the paragraph"""
        self.brand_new_page = 0
        # Take care of superscript tags
        super_count = text.count('<super>')
        for num in range(super_count):
            start = text.find('<super>')
            self.paragraph_text = self.paragraph_text + text[:start]
            append_to_paragraph(self.paragraph,self.paragraph_directive,self.paragraph_text)
            self.paragraph_text = ""
            text = text[start+7:]

            start = text.find('</super>')
            self.paragraph_text = self.paragraph_text + text[:start]
            append_to_paragraph(self.paragraph,_SUPER,self.paragraph_text)
            self.paragraph_text = ""
            text = text[start+8:]

        self.paragraph_text = self.paragraph_text + text

    def write_note(self,text,format,style_name):
        self.brand_new_page = 0
        if format == 1:
            for line in text.split('\n'):
                self.start_paragraph(style_name)
                self.paragraph_directive = _MONO
                self.write_text(line)
                self.end_paragraph()
        elif format == 0:
            for line in text.split('\n\n'):
                self.start_paragraph(style_name)
                line = line.replace('\n',' ')
                line = ' '.join(line.split())
                self.write_text(line)
                self.end_paragraph()

    #function to help us advance a line 
    def advance_line(self,y,paragraph=None):
        self.brand_new_page = 0
        if paragraph:
            spacing = paragraph.fontstyle.get_size() * _EXTRA_SPACING_FACTOR
        else:
            spacing = _LINE_SPACING
        new_y = y - spacing
        if y < self.bottom_margin:
            x = self.x
            self.end_page()
            self.start_page()
            new_y = self.y
            self.x = x
        return new_y

    def write_paragraph(self,paragraph,x,y,width):
        """
        Write the contents of the paragraph, observing per-piece info.
        
        paragraph   - GnomePrintParagraph instance
        x,y         - coordinates to start at
        width       - allocated width
        """
        
        self.brand_new_page = 0
        if not paragraph.get_piece_list():
            return (x,y)

        paragraph.format(width)

        x = x + cm2u(paragraph.style.get_left_margin())
        
        width = width   - cm2u(paragraph.style.get_right_margin()) \
                        - cm2u(paragraph.style.get_left_margin())

        left_margin = x
        no_space = 0
        next_no_space = 0
        first = 1

        if y - paragraph.fontstyle.get_size() * _EXTRA_SPACING_FACTOR \
               < self.bottom_margin:
            self.end_page()
            self.start_page()
            x = left_margin
            y = self.y

        if y != self.top_margin:
            y = y - cm2u(paragraph.style.get_top_margin())

        line_number = 0
        total_lines = len(paragraph.get_lines())
        
        # Loop over lines which were assembled by paragraph.format()
        for (start_piece,start_word,end_piece,end_word,avail_width) \
                in paragraph.get_lines():

            line_number += 1

            if paragraph.get_alignment() == BaseDoc.PARA_ALIGN_CENTER:
                x = x + 0.5 * avail_width
            elif paragraph.get_alignment() == BaseDoc.PARA_ALIGN_RIGHT:
                x = x + avail_width
            elif paragraph.get_alignment() == BaseDoc.PARA_ALIGN_LEFT:
                pass
            elif paragraph.get_alignment() == BaseDoc.PARA_ALIGN_JUSTIFY:
                print "LPRDoc: Paragraph justification not supported."
                print "        Falling back to left-justified mode."

            if first:
                first = 0
                x = x + cm2u(paragraph.style.get_first_indent())
                y = y - paragraph.fontstyle.get_size() * _EXTRA_SPACING_FACTOR

            # Loop over pieces that constitute the line
            for piece_num in range(start_piece,end_piece+1):
                (directive,text) = paragraph.get_piece_list()[piece_num]
                fontstyle = BaseDoc.FontStyle(paragraph.get_fontstyle())
                if directive == _BOLD:
                    fontstyle.set_bold(1)
                elif directive == _SUPER:
                    size = fontstyle.get_size()
                    fontstyle.set_size(size-_SUPER_SIZE_REDUCTION)
                    y = y + _SUPER_ELEVATION_FRACTION * fontstyle.get_size()
                elif directive == _MONO:
                    fontstyle.set_type_face(BaseDoc.FONT_MONOSPACE)
                elif directive == _POSTLEADER:
                    x = left_margin
                    if text == '':
                        next_no_space = 1
                textlist = text.split()
                if start_piece == end_piece:
                    the_textlist = textlist[start_word:end_word]
                elif piece_num > start_piece and piece_num < end_piece:
                    the_textlist = textlist[:]
                elif piece_num == start_piece:
                    the_textlist = textlist[start_word:]
                elif piece_num == end_piece:
                    the_textlist = textlist[:end_word]

                the_text = ' '.join(the_textlist)
                if piece_num == start_piece \
                                or directive == _SUPER \
                                or directive == _POSTLEADER \
                                or next_no_space \
                                or no_space \
                                or (the_text and the_text[0] in punctuation):
                    spacer = ""
                else:
                    spacer = " "
                the_text = spacer + the_text

                self.gpc.setfont(find_font_from_fontstyle(fontstyle))
                self.gpc.moveto(x, y)
                self.gpc.show(the_text)
                x = x + get_text_width(the_text,fontstyle)
                if directive == _SUPER:
                    y = y - _SUPER_ELEVATION_FRACTION * fontstyle.get_size()
                if directive != _POSTLEADER and next_no_space:
                    next_no_space = 0

            # If this was the linebreak, no space on the next line's start
            if end_word:
                no_space = 0
            else:
                no_space = 1

            if line_number < total_lines:
                y = self.advance_line(y,paragraph)
            x = left_margin

        x = x - cm2u(paragraph.style.get_left_margin())
        y = y - cm2u(paragraph.style.get_bottom_margin())
        return (x,y)

    def output_table(self):
        """Do calcs on data in table and output data in a formatted way."""
        self.brand_new_page = 0
        min_col_size = [0] * self.ncols
        max_vspace = [0] * len(self.table_data)

        for row_num in range(len(self.table_data)):
            row = self.table_data[row_num][:]
            #do calcs on each row and keep track on max length of each column
            for col in range(self.ncols):
                if not self.cell_widths[row_num][col]:
                    continue

                padding = cm2u(self.gp_cell_styles[row_num][col].get_padding())
                the_max = 0
                for paragraph in row[col]:
                    the_min = paragraph.get_min_width()
                    if the_min > min_col_size[col]:
                        min_col_size[col] = the_min

                    the_max += paragraph.get_height(
                                        self.cell_widths[row_num][col])
                the_max += 2 * padding
                if the_max > max_vspace[row_num]:
                    max_vspace[row_num] = the_max

        #is table width larger than the width of the paper?
        min_table_width = 0
        for size in min_col_size:
            min_table_width = min_table_width + size

        if min_table_width > (self.right_margin - self.left_margin):
            print "LPRDoc: Table does not fit onto the page."

        #for now we will assume left justification of tables
        #output data in table
        for row_num in range(len(self.table_data)):
            row = self.table_data[row_num]
            # If this row puts us below the bottom, start new page here
            if self.y - max_vspace[row_num] < self.bottom_margin:
                self.end_page()
                self.start_page()

            x = self.left_margin         #reset so that x is at margin
            col_y = self.y    # all columns start at the same height
            for col in range(self.ncols):
                if not self.cell_widths[row_num][col]:
                    continue
                self.y = col_y
                padding = cm2u(self.gp_cell_styles [row_num][col].get_padding())
                for paragraph in row[col]:
                    if paragraph.__class__.__name__ == 'GnomePrintPhoto':
                        write_item = self.write_photo
                    else:
                        write_item = self.write_paragraph
                    junk, self.y = write_item(paragraph,
                                     x + padding, self.y - padding, 
                                     self.cell_widths[row_num][col] \
                                            - 2 * padding)

                x = x + self.cell_widths[row_num][col]    # set up margin for this row
            self.y = col_y - max_vspace[row_num]

    #------------------------------------------------------------------------
    #
    # Graphic methods
    #
    #------------------------------------------------------------------------

    def horizontal_line(self):
        self.brand_new_page = 0
        self.gpc.moveto(self.left_margin, self.y)
        self.gpc.lineto(self.right_margin, self.y)

    def draw_path(self,style,path):
        self.brand_new_page = 0
        stype = self.draw_styles[style]
        self.gpc.setlinewidth(stype.get_line_width())
        fill_color = rgb_color(stype.get_fill_color())
        color = rgb_color(stype.get_color())

        point = path[0]
        x = cm2u(point[0]) + self.left_margin
        y = self.top_margin - cm2u(point[1])
        self.gpc.moveto(x,y)

        for point in path[1:]:
            x = cm2u(point[0]) + self.left_margin
            y = self.top_margin - cm2u(point[1])
            self.gpc.lineto(x,y)
        self.gpc.closepath()

        self.gpc.setrgbcolor(fill_color[0],fill_color[1],fill_color[2])
        self.gpc.fill()

        point = path[0]
        x = cm2u(point[0]) + self.left_margin
        y = self.top_margin - cm2u(point[1])
        self.gpc.moveto(x,y)

        for point in path[1:]:
            x = cm2u(point[0]) + self.left_margin
            y = self.top_margin - cm2u(point[1])
            self.gpc.lineto(x,y)
        self.gpc.closepath()

        self.gpc.setrgbcolor(color[0],color[1],color[2])
        self.gpc.stroke()

        self.gpc.setrgbcolor(0,0,0)
        
    def draw_box(self,style,text,x,y):
        #assuming that we start drawing box from current position

        self.brand_new_page = 0
        x = self.left_margin + cm2u(x)
        y = self.top_margin - cm2u(y)

        box_style = self.draw_styles[style]
        para_name = box_style.get_paragraph_style()
        para_style = self.style_list[para_name]
        fontstyle = para_style.get_font()
        bh = cm2u(box_style.get_height())
        bw = cm2u(box_style.get_width())

        if box_style.get_shadow():
            ss = cm2u(box_style.get_shadow_space())
            color = rgb_color(_SHADOW_COLOR)
            path = (
                (x+ss,y-bh), (x+ss,y-bh-ss), (x+bw+ss,y-bh-ss),
                (x+bw+ss,y-ss), (x+bw,y-ss), (x+bw,y-bh), (x+ss,y-bh),
            )
            x_i,y_i = path[0]
            self.gpc.moveto(x_i,y_i)
            for (x_i,y_i) in path[1:]:
                self.gpc.lineto(x_i,y_i)
            self.gpc.closepath()
            
            self.gpc.setrgbcolor(color[0],color[1],color[2])
            self.gpc.fill()
            self.gpc.setrgbcolor(0,0,0)

        self.gpc.rect_stroked(x,y,bw,-bh)

        if text:
            lines = text.split('\n')
            start_x = x + 0.5 * fontstyle.get_size()
            start_y = y - fontstyle.get_size() * _EXTRA_SPACING_FACTOR
            for line in lines:
                if not line.split():
                    continue
                self.gpc.setfont(find_font_from_fontstyle(fontstyle))
                self.gpc.moveto(start_x,start_y)
                self.gpc.show(line)
                start_y -= fontstyle.get_size() * _EXTRA_SPACING_FACTOR

    def write_at (self, style, text, x, y):
        self.brand_new_page = 0
        para_style = self.style_list[style]
        fontstyle = para_style.get_font()

        self.gpc.setfont(find_font_from_fontstyle(fontstyle))
        x = self.left_margin + cm2u(x)
        y = self.top_margin - cm2u(y) - fontstyle.get_size() * _EXTRA_SPACING_FACTOR
        self.gpc.moveto(x,y)
        self.gpc.show(text)

    def draw_bar(self, style, x1, y1, x2, y2):
        self.brand_new_page = 0

        stype = self.draw_styles[style]
        self.gpc.setlinewidth(stype.get_line_width())
        fill_color = rgb_color(stype.get_fill_color())
        color = rgb_color(stype.get_color())

        x = self.left_margin + cm2u(x1)
        y = self.top_margin - cm2u(y1)
        bh = cm2u(y2-y1)
        bw = cm2u(x2-x1)

        self.gpc.setrgbcolor(fill_color[0],fill_color[1],fill_color[2])
        self.gpc.rect_filled(x,y,bw,-bh)
        self.gpc.setrgbcolor(color[0],color[1],color[2])
        self.gpc.rect_stroked(x,y,bw,-bh)
        self.gpc.setrgbcolor(0,0,0)

    def draw_text(self,style,text,x,y):
        self.brand_new_page = 0
        box_style = self.draw_styles[style]
        para_name = box_style.get_paragraph_style()
        para_style = self.style_list[para_name]
        fontstyle = para_style.get_font()

        start_x = self.left_margin + cm2u(x)
        start_y = self.top_margin - cm2u(y) - fontstyle.get_size() * _EXTRA_SPACING_FACTOR
        
        self.gpc.setfont(find_font_from_fontstyle(fontstyle))
        self.gpc.moveto(start_x,start_y)
        self.gpc.show(text)
                                                                                
    def center_text(self,style,text,x,y):
        self.brand_new_page = 0
        box_style = self.draw_styles[style]
        para_name = box_style.get_paragraph_style()
        para_style = self.style_list[para_name]
        fontstyle = para_style.get_font()

        width = get_text_width(text,fontstyle)
        start_x = self.left_margin + cm2u(x) - 0.5 * width
        start_y = self.top_margin - cm2u(y) \
                - fontstyle.get_size() * _EXTRA_SPACING_FACTOR
        self.gpc.setfont(find_font_from_fontstyle(fontstyle))
        self.gpc.moveto(start_x, start_y)
        self.gpc.show(text)
                                                                                
    def rotate_text(self,style,text,x,y,angle):
        self.brand_new_page = 0
        # FIXME - remove when new gnome-python is in all distros
        if not support_photos:
            return
        # end FIXME
        box_style = self.draw_styles[style]
        para_name = box_style.get_paragraph_style()
        para_style = self.style_list[para_name]
        fontstyle = para_style.get_font()
        
        y_start = self.top_margin - cm2u(y)
        x_start = self.left_margin + cm2u(x)
        size = fontstyle.get_size()

        self.gpc.gsave()
        self.gpc.translate(x_start,y_start)
        self.gpc.rotate(-angle)

        this_y = 0
        for line in text:
            if not line.split():
                continue
            width = get_text_width(line,fontstyle)
            this_x = -0.5 * width
            self.gpc.setfont(find_font_from_fontstyle(fontstyle))
            self.gpc.moveto(this_x,this_y)
            self.gpc.show(line)
            this_y -= size * _EXTRA_SPACING_FACTOR

        self.gpc.grestore()
                                                                                
    def draw_line(self,style,x1,y1,x2,y2):
        self.brand_new_page = 0
        x1 = cm2u(x1) + self.left_margin
        x2 = cm2u(x2) + self.left_margin
        y1 = self.top_margin - cm2u(y1)
        y2 = self.top_margin - cm2u(y2)
        self.gpc.line_stroked(x1,y1,x2,y2)

    #------------------------------------------------------------------------
    #
    # Print job methods
    #
    #------------------------------------------------------------------------

    #function to print text to a printer
    def do_print(self,dialog,job):
        self.gpc = gnomeprint.Context(dialog.get_config())
        job.render(self.gpc)
        self.gpc.close()
 
    #I believe this is a print preview
    def show_preview(self,dialog):
         w = gnomeprint.ui.JobPreview(self.job, _("Print Preview"))
         w.set_property('allow-grow', 1)
         w.set_property('allow-shrink', 1)
         w.set_transient_for(dialog)
         w.show_all()
 
    #function used to get users response and do a certain
    #action depending on that response
    def print_dialog_response(self, dialog, resp, job):
         if resp == gnomeprint.ui.DIALOG_RESPONSE_PREVIEW:
            self.show_preview(dialog)
         elif resp == gnomeprint.ui.DIALOG_RESPONSE_CANCEL:
            dialog.destroy()
         elif resp == gnomeprint.ui.DIALOG_RESPONSE_PRINT:
            self.do_print(dialog, self.job)
            dialog.destroy()

    #function displays a window that allows user to choose 
    #to print, show, etc
    def show_print_dialog(self):
        dialog = gnomeprint.ui.Dialog(self.job, _("Print..."), 
                        gnomeprint.ui.DIALOG_RANGE|gnomeprint.ui.DIALOG_COPIES)
        dialog.construct_range_page(
                        gnomeprint.ui.RANGE_ALL|gnomeprint.ui.RANGE_RANGE, 
                        1, self.page_count, "A", "Pages: ")
        dialog.connect('response', self.print_dialog_response, self.job)
        dialog.show()

#------------------------------------------------------------------------
#
# Register the document generator with the system
#
#------------------------------------------------------------------------
register_text_doc(
    name=_("Print..."),
    classref=LPRDoc,
    table=1,
    paper=1,
    style=1,
    ext="",
    print_report_label=None,
    clname='print')
    
register_book_doc(
    _("Print..."),
    LPRDoc,
    1,
    1,
    1,
    "",
    'print')

register_draw_doc(
    _("Print..."),
    LPRDoc,
    1,
    1,
    "",
    None,
    'print')
