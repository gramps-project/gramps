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
# Paragraph Handling
#
#------------------------------------------------------------------------
    
#------------------------------------------------------------------------
#
# Units conversion
#
#------------------------------------------------------------------------
def cm(unit):
    """
    Convert gnome-print units to cm
    """
    return 2.54 * unit / 72.0 

def unit(cms):
    """
    Convert cms to gnome-print units
    """
    return cms * 72.0 / 2.54 

#------------------------------------------------------------------------
#
# LPRDoc
#
#------------------------------------------------------------------------
class LPRDoc(BaseDoc.BaseDoc):
    """Gnome-print document interface class. Derived from BaseDoc"""
    
    def open(self,filename):
        """Sets up initialization"""
        #set up variables needed to keep track of which state we are in
        self.__in_table=0
        self.__in_cell=0
        self.__in_paragraph=0
        self.__page_count=0
        self.__page_open=0
        
        self.__paragraph_data=""
        self.__cell_data=""
        self.__table_data=[]

        #create main variables for this print job
        self.__job = gnomeprint.Job(gnomeprint.config_default())
        self.__pc = self.__job.get_context()

        #find out what the width and height of the page is
        __width, __height =gnomeprint.job_get_page_size_from_config(self.__job.get_config())
        self.__left_margin=__width*0.1
        self.__right_margin=__width*0.9
        self.__top_margin=__height*0.9
        self.__bottom_margin=__height*0.1

        #set what fonts we will use
        self.__regular_font=gnomeprint.font_find_closest("Serif Regular", 10)
        self.__bold_font=gnomeprint.font_find_closest("Serif Bold", 10)
        self.__font=self.__regular_font

        self.start_page(self)
 
    def close(self):
        """Clean up and close the document"""
        #print "close doc"
        #gracefully end page before we close the doc if a page is open
        if self.__page_open:
           self.end_page()

        self.__job.close()
        self.__show_print_dialog()

    def line_break(self):
        "Forces a line break within a paragraph"
        self.__advance_line(self.__y)

    def page_break(self):
        "Forces a page break, creating a new page"
        self.start_page()
                                                                                
    def start_page(self,orientation=None):
        """Create a new page"""
        #print "begin page"
        #reset variables dealing with opening a page
        if (self.__page_open):
           self.end_page()

        self.__page_open=1
        self.__page_count+=1
        self.__x=self.__left_margin
        self.__y=self.__top_margin
        
        self.__pc.beginpage(str(self.__page_count))
        self.__pc.setfont(self.__font)
        self.__pc.moveto(self.__x, self.__y)

    def end_page(self):
        """Close the current page"""
        #print "end page"
        if (self.__page_open):
           self.__page_open=0
           self.__pc.showpage()

    def start_paragraph(self,style_name,leader=None):
        """Paragraphs handling - A Gramps paragraph is any 
        single body of text, from a single word, to several sentences.
        We assume a linebreak at the end of each paragraph."""
        #print "start paragraph"
        #set paragraph variables so we know that we are in a paragraph
        self.__in_paragraph=1
        self.__paragraph_data=""
    
    def end_paragraph(self):
        """End the current paragraph"""
        #print "end paragraph"
        self.__in_paragraph=0
        #print text in paragraph if any data exists
        if len(self.__paragraph_data) > 0:
            self.__x, self.__y=self.__print_text(self.__paragraph_data, 
                                                self.__x, self.__y,
                                                self.__left_margin, 
                                                        self.__right_margin)
            self.__paragraph_data=""
            self.__y=self.__advance_line(self.__y)

    def start_bold(self):
        """Bold face"""
        #print "start bold"
        self.__font=self.__bold_font
        self.__pc.setfont(self.__font)
        
    def end_bold(self):
        """End bold face"""
        #print "end bold"
        self.__font=self.__regular_font
        self.__pc.setfont(self.__font)

    def start_superscript(self):
        pass
                                                                                
    def end_superscript(self):
        pass
                                                                                
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
        #print "start table"
        #reset variables for this state 
        self.__table_data=[]
        self.__in_table=1

    def end_table(self):
        """Close the table environment"""
        #print "end table"
        #output table contents
        self.__output_table()
        self.__in_table=0
        self.__y=self.__advance_line(self.__y)

    def start_row(self):
        """Begin a new row"""
        # doline/skipfirst are flags for adding hor. rules
        #print "start row"
        #reset this state, so we can get data from user
        self.__row_data=[]

    def end_row(self):
        """End the row (new line)"""
        #print "end row"
        #add row data to the data we have for the current table
        self.__table_data.append(self.__row_data)
            
    def start_cell(self,style_name,span=1):
        """Add an entry to the table.
           We always place our data inside braces 
           for safety of formatting."""
        #print "start cell"
        #reset this state
        self.__in_cell=1
        self.__cell_data=""
 
    def end_cell(self):
        """Prepares for next cell"""
        #print "end cell"
        #append the cell text to the row data
        self.__in_cell=0
        self.__row_data.append(self.__cell_data)

    def add_photo(self,name,pos,x,y):
        """Add photo to report"""
        #print "add photo"

    def horizontal_line(self):
        self.__pc.moveto(self.__x, self.__y)
        self.__pc.lineto(self.__right_margin, self.__y)

    def write_cmdstr(self,text):
        """
        Writes the text in the current paragraph. Should only be used after a
        start_paragraph and before an end_paragraph.
                                                                                
        text - text to write.
        """
        if self__in_paragraph != 1:
           self.start_paragraph()
       
        self.write(text)    
                                                                                
    def draw_arc(self,style,x1,y1,x2,y2,angle,extent):
        pass
                                                                                
    def draw_path(self,style,path):
        pass
                                                                                
    def draw_box(self,style,text,x,y):
        #assuming that we start drawing box from current position
        __width=x-self.__x
        __height=y-self.__y
        self.__pc.rect_stroked(self.__x, self.__y) 

        if text != None:
           __text_width=self.__get_text_width(text)
           #try to center text in box
           self.__pc.moveto(self.__x+(__width/2)-(__text_width/2),
                            self.__y+(__height/2))
           self.__pc.show(text)                                                                       

    def write_at (self, style, text, x, y):
        self.__pc.moveto(x, y)
        self.__pc.show(text)

    def draw_bar(self, style, x1, y1, x2, y2):
        self.__pc.moveto(x1, y1)
        self.__pc.lineto(x2, y2)

    def draw_text(self,style,text,x1,y1):
        self.__pc.moveto(x1,y1)
        self.__pc.show(text)
                                                                                
    def center_text(self,style,text,x1,y1):
        #not sure how x1, y1 fit into this
        #should we assume x1 y1 is the starting location
        #and that the right margin is the right edge?
        __width=self.get_text_width(text)
        __center=self.__right_margin-self.__left_margin
        __center-=__width/2
        self.__pc.moveto(__center, self.__y)
        self.__pc.show(text)
                                                                                
    def rotate_text(self,style,text,x,y,angle):
        pass
                                                                                
    def draw_line(self,style,x1,y1,x2,y2):
        self.__pc.line_stroked(x1,y1,x2,y2)
                                                                                
    def write_text(self,text):
        """Write the text to the file"""
        #print "write text"
        #if we are in a cell add this text to cell_data
        if self.__in_cell:
           self.__cell_data=self.__cell_data+str(text)
           return

        #if we are in a paragraph add this text to the paragraph data
        if self.__in_paragraph:
           self.__paragraph_data=self.__paragraph_data+str(text)
           return

        #if we are at the bottom of the page, create a new page
        if self.__y < self.__bottom_margin:
           self.end_page()
           self.start_page()

        #output data if we get this far (we are not in a paragaph or
        #a table)
        self.__x, self.__y=self.__print_text(text, self.__x, self.__y,
                          self.__left_margin, self.__right_margin)
        #self.__y=self.__advance_line(self.__y)

    #function to help us advance a line 
    def __advance_line(self, y):
        return y-20

    #function to determine the width of text
    def __text_width(self, text):
        return self.__font.get_width_utf8(text)

    #this function tells us the minimum size that a column can be
    #by returning the width of the largest word in the text
    def __min_column_size (self, text):
        __textlist=string.split(text, " ")
        __max_word_size=0
        for __word in __textlist:
            __length=self.__text_width(__word+" "*3)
            if __length > __max_word_size:
               __max_word_size=__length
      
        return __max_word_size

    #function to print out text between left_margin and right_margin
    #at position y on page
    def __print_text(self, text, x, y, left_margin, right_margin):
        __width=right_margin-left_margin

        #all text will fit within the width provided
        if __width >= self.__text_width(text):
           self.__pc.moveto(left_margin, y)
           x=left_margin+self.__text_width(text)
           self.__pc.show(text)
           y=self.__advance_line(y)
        else:
          #divide up text and print
          __textlist=string.split(text, " ")
          __text=""
          for __element in __textlist:
              if self.__text_width(__text+__element+" ") < __width:
                 __text=__text+__element+" "
              else:
                 #__text contains as many words as this __width allows
                 self.__pc.moveto(left_margin, y)
                 self.__pc.show(__text)
                 __text=__element+" "
                 y=self.__advance_line(y)

                 #if not in table and cursor is below bottom margin
                 if self.__in_table==0 and y < self.__bottom_margin:
                    self.end_page()
                    self.start_page()
                    x=self.__x
                    y=self.__y

          #if __text still contains data, we will want to print it out
          if len(__text) > 0:
             self.__pc.moveto(left_margin, y)
             self.__pc.show(__text)
             y=self.__advance_line(y)

        return (x,y)

    def __output_table(self):
        """do calcs on data in table and output data in a formatted way"""
        __max_col_size=[0]*100
        __min_col_size=[0]*100

        for __row in self.__table_data:
           #do calcs on each __row and keep track on max length of each column
           for __col in range(0,len(__row)):
              __row[__col]=__row[__col]+" "*3;   
              if __max_col_size[__col] < self.__text_width(__row[__col]):
                  __max_col_size[__col]=self.__text_width(__row[__col])
              __min_col_size[__col]=self.__min_column_size(__row[__col])


        #now we have an idea of the max size of each column
        #now output data in the table
        #find total width that the table needs to be.
        #later this value may be used to cut the longest columns down
        #so that data fits on the width of the page
        __total_table_width=0
        for __value in __max_col_size:
          __total_table_width+=__value

        #is table width larger than the width of the paper?
        if __total_table_width > (self.__right_margin - self.__left_margin):
            #figure out the largest our table can be to fit on a page
            __width=self.__right_margin - self.__left_margin
            #find out how much larger our table is than what is allowed
            __extra_length=__total_table_width - __width
            #for each column, substract the extra width off so that
            #each column gets deduced a width determined by its 
            #size compared to the other columns
            #(larger columns get more taken off, smaller columns get
            # less width taken off)

            while __extra_length > 1:
                print __extra_length
                for __col in range(0, len(__max_col_size)):
                    if __extra_length<=1: break
                    if __max_col_size[__col] > __min_col_size[__col]:
                        __temp=__max_col_size[__col]-(__max_col_size[__col]/__total_table_width)*__extra_length
                    if __temp >= __min_col_size[__col]:
                        __max_col_size[__col]=__temp
           

                __total_table_width=0
                for __value in __max_col_size:
                    __total_table_width+=__value
                __extra_length=__total_table_width - __width  
                   
        #for now we will assume left justification of tables
        #output data in table
        __min_y=self.__y     #need to keep track of tallest column of 
                             #text in each row
        for __row in self.__table_data:
            __x=self.__left_margin         #reset so that x is at margin
            for __col in range(0,len(__row)):
                __nothing, __y=self.__print_text(__row[__col], 
                                                 self.__x, self.__y, 
                                                 __x, __x+__max_col_size[__col])

                __x=__x+__max_col_size[__col]    # set up margin for this row
                if __y < __min_y:     # if we go below current lowest 
                   __min_y=__y        # column
  
            self.__y=__min_y          #reset so that we do not overwrite

            #see if we are about to go off the page, if so, create new page
            if self.__y < self.__bottom_margin:
               self.end_page()
               self.start_page()
               __min_y=self.__y

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
    style=0,
    ext=""
    )
