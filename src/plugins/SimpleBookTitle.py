
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

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import string
import cStringIO

#------------------------------------------------------------------------
#
# gramps modules
#
#------------------------------------------------------------------------
import Report
import TextDoc
import RelLib
import Errors
from QuestionDialog import ErrorDialog
from intl import gettext as _

#------------------------------------------------------------------------
#
# AncestorReport
#
#------------------------------------------------------------------------
class SimpleBookTitle(Report.Report):

    def __init__(self,database,person,max,pgbrk,doc,output,newpage=0):
        self.map = {}
        self.database = database
        self.start = person
        self.max_generations = max
        self.pgbrk = pgbrk
        self.doc = doc
        self.newpage = newpage
        if output:
            self.standalone = 1
            self.doc.open(output)
        else:
            self.standalone = 0
        self.sref_map = {}
        self.sref_index = 1
        
    def setup(self):
        pass

    def write_report(self):

        if self.newpage:
            self.doc.page_break()

        self.doc.start_paragraph('SBT-Title')
        self.doc.write_text('Title of the book')
        self.doc.end_paragraph()


        import time

        dateinfo = time.localtime(time.time())
        name = self.database.getResearcher().getName()
        self.doc.start_paragraph('SBT-Subtitle')
        self.doc.write_text(_('Copyright %d %s') % (dateinfo[0], name))
        self.doc.end_paragraph()

        if self.standalone:
            self.doc.close()


def _make_default_style(default_style):
    """Make the default output style for the Simple Boot Title report."""
    font = TextDoc.FontStyle()
    font.set(face=TextDoc.FONT_SANS_SERIF,size=16,bold=1,italic=1)
    para = TextDoc.ParagraphStyle()
    para.set_font(font)
    para.set_header_level(1)
    para.set_alignment(TextDoc.PARA_ALIGN_CENTER)
    para.set(pad=0.5)
    para.set_description(_('The style used for the title of the page.'))
    default_style.add_style("SBT-Title",para)
    
    font = TextDoc.FontStyle()
    font.set(face=TextDoc.FONT_SANS_SERIF,size=14,italic=1)
    para = TextDoc.ParagraphStyle()
    para.set_font(font)
    para.set_header_level(2)
    para.set(pad=0.5)
    para.set_alignment(TextDoc.PARA_ALIGN_CENTER)
    para.set_description(_('The style used for the subtitle.'))
    default_style.add_style("SBT-Subtitle",para)
    
#------------------------------------------------------------------------
#
# Set up sane defaults for the book_item
#
#------------------------------------------------------------------------
_style_file = "simple_book_title.xml"
_style_name = "default" 

_person_id = ""
_max_gen = 10
_pg_brk = 0
_options = [ _person_id, _max_gen, _pg_brk ]

#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class SimpleBookTitleDialog(Report.BareReportDialog):

    def __init__(self,database,person,opt,stl):

        self.options = opt
        self.db = database
        if self.options[0]:
            self.person = self.db.getPerson(self.options[0])
        else:
            self.person = person
        Report.BareReportDialog.__init__(self,database,self.person)

        def make_default_style(self):
            _make_default_style(self.default_style)

        self.max_gen = int(self.options[1]) 
        self.pg_brk = int(self.options[2])
        self.style_name = stl
        self.new_person = None

        self.generations_spinbox.set_value(self.max_gen)
        self.pagebreak_checkbox.set_active(self.pg_brk)
        
        self.window.run()

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return "%s - GRAMPS Book" % (_("Simple Book Title"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("FTM Style Ancestor Report for GRAMPS Book") 

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return _style_file
    
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
        self.options = [ self.person.getId(), self.max_gen, self.pg_brk ]
        self.style_name = self.selected_style.get_name() 
   

#------------------------------------------------------------------------
#
# Function to write Book Item 
#
#------------------------------------------------------------------------
def write_book_item(database,person,doc,options,newpage=0):
    """Write the FTM Style Ancestor Report options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options[0]:
            person = database.getPerson(options[0])
        max_gen = int(options[1])
        pg_brk = int(options[2])
        return SimpleBookTitle(database, person, max_gen, pg_brk, doc, None, newpage )
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
    _("Simple Book Title"), 
    _("Text"),
    SimpleBookTitleDialog,
    write_book_item,
    _options,
    _style_name,
    _style_file,
    _make_default_style
   )

