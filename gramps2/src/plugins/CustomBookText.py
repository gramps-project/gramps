# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2003  Donald N. Allingham
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

#
# Written by Alex Roitman, 
# largely based on the SimpleBookTitle.py by Don Allingham
#

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
import Report
import BaseDoc
import Errors
from QuestionDialog import ErrorDialog
from gettext import gettext as _

import gtk

#------------------------------------------------------------------------
#
# CustomText
#
#------------------------------------------------------------------------
class CustomText(Report.Report):

    def __init__(self,database,person,top_text,middle_text,bottom_text,doc,output,newpage=0):
        self.map = {}
        self.database = database
        self.start = person
        self.top_text = top_text
        self.middle_text = middle_text
        self.bottom_text = bottom_text
        self.doc = doc
        self.newpage = newpage
        if output:
            self.standalone = 1
            self.doc.open(output)
            self.doc.init()
        else:
            self.standalone = 0
        self.sref_map = {}
        self.sref_index = 1
        
    def setup(self):
        pass

    def write_report(self):

        if self.newpage:
            self.doc.page_break()

        self.doc.start_paragraph('CBT-Initial')
        self.doc.write_text(self.top_text)
        self.doc.end_paragraph()

        self.doc.start_paragraph('CBT-Middle')
        self.doc.write_text(self.middle_text)
        self.doc.end_paragraph()

        self.doc.start_paragraph('CBT-Final')
        self.doc.write_text(self.bottom_text)
        self.doc.end_paragraph()

        if self.standalone:
            self.doc.close()


def _make_default_style(default_style):
    """Make the default output style for the Custom Text report."""
    font = BaseDoc.FontStyle()
    font.set(face=BaseDoc.FONT_SANS_SERIF,size=12,bold=0,italic=0)
    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
    para.set(pad=0.5)
    para.set_description(_('The style used for the first portion of the custom text.'))
    default_style.add_style("CBT-Initial",para)
    
    font = BaseDoc.FontStyle()
    font.set(face=BaseDoc.FONT_SANS_SERIF,size=12,bold=0,italic=0)
    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    para.set(pad=0.5)
    para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
    para.set_description(_('The style used for the middle portion of the custom text.'))
    default_style.add_style("CBT-Middle",para)
    
    font = BaseDoc.FontStyle()
    font.set(face=BaseDoc.FONT_SANS_SERIF,size=12,bold=0,italic=0)
    para = BaseDoc.ParagraphStyle()
    para.set_font(font)
    para.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
    para.set(pad=0.5)
    para.set_description(_('The style used for the last portion of the custom text.'))
    default_style.add_style("CBT-Final",para)

#------------------------------------------------------------------------
#
# Set up sane defaults for the book_item
#
#------------------------------------------------------------------------
_style_file = "custom_text.xml"
_style_name = "default" 

_person_id = ""
_top_text = ""
_middle_text = ""
_bottom_text = ""

_options = ( _person_id, _top_text, _middle_text, _bottom_text )


#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class CustomTextDialog(Report.BareReportDialog):

    def __init__(self,database,person,opt,stl):

        self.options = opt
        self.db = database
        if self.options[0]:
            self.person = self.db.get_person(self.options[0])
        else:
            self.person = person
        self.style_name = stl

        Report.BareReportDialog.__init__(self,database,self.person)

        self.top_text = self.options[1]
        self.middle_text = self.options[2]
        self.bottom_text = self.options[3]

        self.top_text_view.get_buffer().set_text(self.top_text)
        self.middle_text_view.get_buffer().set_text(self.middle_text)
        self.bottom_text_view.get_buffer().set_text(self.bottom_text)

        self.notebook.set_size_request(450,300)

        self.new_person = None

        self.window.run()

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def make_default_style(self):
        _make_default_style(self.default_style)

    def get_title(self):
        """The window title for this dialog"""
        return "%s - GRAMPS Book" % (_("Custom Text"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Custom Text for GRAMPS Book") 

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return _style_file
    
    def setup_center_person(self): 
        pass

    def setup_report_options_frame(self):
        self.notebook = gtk.Notebook()
        self.notebook.set_border_width(6)
        self.window.vbox.add(self.notebook)

    def add_user_options(self):
        self.top_sw = gtk.ScrolledWindow()
        self.middle_sw = gtk.ScrolledWindow()
        self.bottom_sw = gtk.ScrolledWindow()

        self.top_sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.middle_sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.bottom_sw.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

        self.top_text_view = gtk.TextView()
        self.middle_text_view = gtk.TextView()
        self.bottom_text_view = gtk.TextView()

        self.top_sw.add_with_viewport(self.top_text_view)
        self.middle_sw.add_with_viewport(self.middle_text_view)
        self.bottom_sw.add_with_viewport(self.bottom_text_view)
  
        self.add_frame_option(_('Initial Text'),"",self.top_sw)
        self.add_frame_option(_('Middle Text'),"",self.middle_sw)
        self.add_frame_option(_('Final Text'),"",self.bottom_sw)

    def parse_report_options_frame(self):
        """Parse the report options frame of the dialog.  
        Save the user selected choices for later use."""

        # call the parent task to handle normal options
        Report.BareReportDialog.parse_report_options_frame(self)

        # get values from the widgets
        self.top_text = self.top_text_view.get_buffer().get_text(
            self.top_text_view.get_buffer().get_start_iter(),
            self.top_text_view.get_buffer().get_end_iter(),
            gtk.FALSE)
        self.middle_text = self.middle_text_view.get_buffer().get_text(
            self.middle_text_view.get_buffer().get_start_iter(),
            self.middle_text_view.get_buffer().get_end_iter(),
            gtk.FALSE)
        self.bottom_text = self.bottom_text_view.get_buffer().get_text(
            self.bottom_text_view.get_buffer().get_start_iter(),
            self.bottom_text_view.get_buffer().get_end_iter(),
            gtk.FALSE)

    def on_cancel(self, obj):
        pass

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices. Parse all options
        and close the window."""

        # Preparation
        self.parse_style_frame()
        self.parse_report_options_frame()
        
        if self.new_person:
            self.person = self.new_person
        self.options = ( self.person.get_id(), 
            self.top_text, self.middle_text, self.bottom_text )
        self.style_name = self.selected_style.get_name() 

#------------------------------------------------------------------------
#
# Function to write Book Item 
#
#------------------------------------------------------------------------
def write_book_item(database,person,doc,options,newpage=0):
    """Write the Title Page using options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options[0]:
            person = database.get_person(options[0])
        top_text = options[1]
        middle_text = options[2]
        bottom_text = options[3]
        return CustomText(database, person, 
            top_text, middle_text, bottom_text, doc, None, newpage )
    except Errors.ReportError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except Errors.FilterError, msg:
        (m1,m2) = msg.messages()
        ErrorDialog(m1,m2)
    except:
        import DisplayTrace
        DisplayTrace.DisplayTrace()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_xpm_image():
    return [
        "48 48 33 1",
        " 	c None",
        ".	c #1A1A1A",
        "+	c #847B6E",
        "@	c #B7AC9C",
        "#	c #D1D1D0",
        "$	c #EEE2D0",
        "%	c #6A655C",
        "&	c #868686",
        "*	c #F1EADF",
        "=	c #5C5854",
        "-	c #B89C73",
        ";	c #E2C8A1",
        ">	c #55524C",
        ",	c #F5EEE6",
        "'	c #4F4E4C",
        ")	c #A19C95",
        "!	c #B3966E",
        "~	c #CDC8BF",
        "{	c #F6F2ED",
        "]	c #A6A5A4",
        "^	c #413F3F",
        "/	c #D8D1C5",
        "(	c #968977",
        "_	c #BAB9B6",
        ":	c #FAFAF9",
        "<	c #BEA27B",
        "[	c #E9DAC2",
        "}	c #9D9385",
        "|	c #E4E3E3",
        "1	c #7A7062",
        "2	c #E6D3B4",
        "3	c #BAA488",
        "4	c #322E2B",
        "                                                ",
        "                                                ",
        "             (+(+++++111%1%%%%===%1             ",
        "             +______________@_@)&==1            ",
        "             +_::::::::::::::*|#_&&}>           ",
        "             &_:::::::::::::::{|#]1~}^          ",
        "             +_::::::::::::::::{|#=|~&4         ",
        "             +_::::]]]]]]]]:::::|{':|~&4        ",
        "             +_::::::::::::::::::{'::|~&4       ",
        "             +_:::::::::::::::::::'*::|~&^      ",
        "             +_:::::::::::::::::::'|*::|~}>     ",
        "             1_::::]]]]]]]]]]]]:::'~|{::|_}%    ",
        "             1_:::::::::::::::::::'..4^'=1+%1   ",
        "             +_::::]]]]]]]]]]]]:::|__])&+%=^%   ",
        "             1_::::::::::::::::::::|#__)&&+'^   ",
        "             1_::::]]]]]]]]]::::::::|#~_])&%^   ",
        "             1_::::::::::::::::::::{||#~_])14   ",
        "             1_::::]]]]]]]]]]]]]]]]]]&}#~_]+4   ",
        "             1_::::::::::::::::::{{{{||#~~@&4   ",
        "             %_::::]]]]]]]]]]]]]]]])))}(~~~&4   ",
        "             %_:::::::::::::::::{{{{{*|#/~_(4   ",
        "             %_::::]]]]]]]]]]]]]]])))))}2;/}4   ",
        "             %_:::::::::::::::{{{{{***||[#~}4   ",
        "             %_::::]]]]]]]]]])]))))))))}2/;)4   ",
        "             %_::::::::::::::{{{{{**|$$[/2~!4   ",
        "             %_::::]]]]]]]]){{{{******$$[2/}4   ",
        "             %_::::::::::::{{{{****$$$$$[2/!4   ",
        "             =_::::]]]]]]])]))))))))})}}[2/!4   ",
        "             %_:::::::::{{{{{{**|$$$$$$[[2;)4   ",
        "             =_::::]]]])]]))))))))))}}}}[22!4   ",
        "             %_::::::::{{{{{|**|$$[$[[[[[22}4   ",
        "             =_::::]]])])))))))))}}}}}}}222-4   ",
        "             =_:::::{{{{{|{*|$$$$$[[[[22222!4   ",
        "             =_::::)]])))))))))}}}}}}(}(2;2-4   ",
        "             =_:::{{{{{{***|$$$$$[[[[22222;-4   ",
        "             =_:::{])))))))))}}}}}}}(}((2;;<4   ",
        "             >_:{{{{{{**|$$$$$[[[[22222;2;;-4   ",
        "             >_{{{{)))))))}}}}}}}(!(((((;;;-4   ",
        "             >_{{{{|**|*$$$$$[[[[22222;;;;;!4   ",
        "             '_{{{{****$$$$$2[[222222;2;;;;-4   ",
        "             '@{{****$$$$$[[[2[222;;2;;;;;;!4   ",
        "             >]{******$$$[$[2[[2222;;;;;;;;!4   ",
        "             '_****$$$$[$[[[[2222;2;;;;;;;;!4   ",
        "             '@__@@@@@@@33<3<<<<<<-<-!!!!!!!4   ",
        "             44444444444444444444444444444444   ",
        "                                                ",
        "                                                ",
        "                                                "]

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_book_item

# (name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style)
register_book_item( 
    _("Custom Text"), 
    _("Text"),
    CustomTextDialog,
    write_book_item,
    _options,
    _style_name,
    _style_file,
    _make_default_style
   )
