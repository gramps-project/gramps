#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2003  Donald N. Allingham
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

"Text Reports/Ahnentafel Report"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import string

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
class AncestorReport(Report.Report):

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
        
    def setup(self):
        pass

    def filter(self,person,index,generation=1):
        if person == None or generation >= self.max_generations:
            return
        self.map[index] = person
    
        family = person.getMainParents()
        if family != None:
            self.filter(family.getFather(),index*2,generation+1)
            self.filter(family.getMother(),(index*2)+1,generation+1)

    def write_report(self):

        if self.newpage:
            self.doc.page_break()

        self.filter(self.start,1)
        
        name = self.start.getPrimaryName().getRegularName()
        self.doc.start_paragraph("Title")
        title = _("Ahnentafel Report for %s") % name
        self.doc.write_text(title)
        self.doc.end_paragraph()
    
        keys = self.map.keys()
        keys.sort()
        generation = 0

        for key in keys :
            if generation == 0 or key >= ( 1 << 30):
                if self.pgbrk and generation > 0:
                    self.doc.page_break()
                self.doc.start_paragraph("Generation")
                t = _("%s Generation") % AncestorReport.gen[generation+1]
                self.doc.write_text(t)
                self.doc.end_paragraph()
                generation = generation + 1

            self.doc.start_paragraph("Entry","%s." % str(key))
            person = self.map[key]
            name = person.getPrimaryName().getRegularName()
        
            self.doc.start_bold()
            self.doc.write_text(name)
            self.doc.end_bold()
            if name[-1:] == '.':
                self.doc.write_text(" ")
            else:
                self.doc.write_text(". ")

            # Check birth record
        
            birth = person.getBirth()
            if birth:
                date = birth.getDateObj().get_start_date()
                place = birth.getPlaceName()
                if place[-1:] == '.':
                    place = place[:-1]
                if date.getDate() != "" or place != "":
                    if date.getDate() != "":
                        if date.getDayValid() and date.getMonthValid():
                            if place != "":
                                t = _("%s was born on %s in %s. ") % \
                                    (name,date.getDate(),place)
                            else:
                                t = _("%s was born on %s. ") % \
                                    (name,date.getDate())
                        else:
                            if place != "":
                                t = _("%s was born in the year %s in %s. ") % \
                                    (name,date.getDate(),place)
                            else:
                                t = _("%s was born in the year %s. ") % \
                                    (name,date.getDate())
                        self.doc.write_text(t)

            death = person.getDeath()
            buried = None
            for event in person.getEventList():
                if string.lower(event.getName()) == "burial":
                    buried = event
        
            if death:
                date = death.getDateObj().get_start_date()
                place = death.getPlaceName()
                if place[-1:] == '.':
                    place = place[:-1]
                if date.getDate() != "" or place != "":
                    if person.getGender() == RelLib.Person.male:
                        male = 1
                    else:
                        male = 0

                    if date.getDate() != "":
                        if date.getDayValid() and date.getMonthValid():
                            if male:
                                if place != "":
                                    t = _("He died on %s in %s") % \
                                        (date.getDate(),place)
                                else:
                                    t = _("He died on %s") % date.getDate()
                            else:
                                if place != "":
                                    t = _("She died on %s in %s") % \
                                        (date.getDate(),place)
                                else:
                                    t = _("She died on %s") % date.getDate()
                        else:
                            if male:
                                if place != "":
                                    t = _("He died in the year %s in %s") % \
                                        (date.getDate(),place)
                                else:
                                    t = _("He died in the year %s") % date.getDate()
                            else:
                                if place != "":
                                    t = _("She died in the year %s in %s") % \
                                        (date.getDate(),place)
                                else:
                                    t = _("She died in the year %s") % date.getDate()

                        self.doc.write_text(t)

                    if buried:
                        date = buried.getDateObj().get_start_date()
                        place = buried.getPlaceName()
                        if place[-1:] == '.':
                            place = place[:-1]
                        if date.getDate() != "" or place != "":
                            if date.getDate() != "":
                                if date.getDayValid() and date.getMonthValid():
                                    if place != "":
                                        t = _(", and was buried on %s in %s.") % \
                                            (date.getDate(),place)
                                    else:
                                        t = _(", and was buried on %s.") % \
                                            date.getDate()
                                else:
                                    if place != "":
                                        t = _(", and was buried in the year %s in %s.") % \
                                            (date.getDate(),place)
                                    else:
                                        t = _(", and was buried in the year %s.") % \
                                            date.getDate()
                            else:
                                t = _(" and was buried in %s." % place)
                        self.doc.write_text(t)
                    else:
                        self.doc.write_text(".")
                        
            self.doc.end_paragraph()
        if self.standalone:
            self.doc.close()
 

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class AncestorReportDialog(Report.TextReportDialog):
    def __init__(self,database,person):
        Report.TextReportDialog.__init__(self,database,person)

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" % (_("Ahnentafel Report"),_("Text Reports"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Ahnentafel Report for %s") % name

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Save Ahnentafel Report")

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return "ancestor_report.xml"
    
    def make_default_style(self):
        _make_default_style(self.default_style)

    def make_report(self):
        """Create the object that will produce the Ahnentafel Report.
        All user dialog has already been handled and the output file
        opened."""
        try:
            MyReport = AncestorReport(self.db, self.person,
                self.max_gen, self.pg_brk, self.doc, self.target_path)
            MyReport.write_report()
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
# Standalone report function
#
#------------------------------------------------------------------------
def report(database,person):
    AncestorReportDialog(database,person)


#------------------------------------------------------------------------
#
# Set up sane defaults for the book_item
#
#------------------------------------------------------------------------
_style_file = "ancestor_report.xml"
_style_name = "default" 

_person_id = ""
_max_gen = 10
_pg_brk = 0
_options = ( _person_id, _max_gen, _pg_brk )

#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class AncestorBareReportDialog(Report.BareReportDialog):

    def __init__(self,database,person,opt,stl):

        self.options = opt
        self.db = database
        if self.options[0]:
            self.person = self.db.getPerson(self.options[0])
        else:
            self.person = person
        self.style_name = stl

        Report.BareReportDialog.__init__(self,database,self.person)

        self.max_gen = int(self.options[1]) 
        self.pg_brk = int(self.options[2])
        self.new_person = None

        self.generations_spinbox.set_value(self.max_gen)
        self.pagebreak_checkbox.set_active(self.pg_brk)
        
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
        return "%s - GRAMPS Book" % (_("Ahnentafel Report"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Ahnentafel Report for GRAMPS Book") 

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
        self.options = ( self.person.getId(), self.max_gen, self.pg_brk )
        self.style_name = self.selected_style.get_name() 

#------------------------------------------------------------------------
#
# Function to write Book Item 
#
#------------------------------------------------------------------------
def write_book_item(database,person,doc,options,newpage=0):
    """Write the Ahnentafel Report using options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options[0]:
            person = database.getPerson(options[0])
        max_gen = int(options[1])
        pg_brk = int(options[2])
        return AncestorReport(database, person, max_gen, pg_brk, doc, None, newpage )
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
def _make_default_style(default_style):
    """Make the default output style for the Ahnentafel report."""
    font = TextDoc.FontStyle()
    font.set(face=TextDoc.FONT_SANS_SERIF,size=16,bold=1)
    para = TextDoc.ParagraphStyle()
    para.set_font(font)
    para.set_header_level(1)
    para.set(pad=0.5)
    para.set_description(_('The style used for the title of the page.'))
    default_style.add_style("Title",para)
    
    font = TextDoc.FontStyle()
    font.set(face=TextDoc.FONT_SANS_SERIF,size=14,italic=1)
    para = TextDoc.ParagraphStyle()
    para.set_font(font)
    para.set_header_level(2)
    para.set(pad=0.5)
    para.set_description(_('The style used for the generation header.'))
    default_style.add_style("Generation",para)
    
    para = TextDoc.ParagraphStyle()
    para.set(first_indent=-1.0,lmargin=1.0,pad=0.25)
    para.set_description(_('The basic style used for the text display.'))
    default_style.add_style("Entry",para)

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
from Plugins import register_report, register_book_item

register_report(
    report,
    _("Ahnentafel Report"),
    category=_("Text Reports"),
    status=(_("Beta")),
    description= _("Produces a textual ancestral report"),
    xpm=get_xpm_image(),
    author_name="Donald N. Allingham",
    author_email="dallingham@users.sourceforge.net"
    )

# (name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style)
register_book_item( 
    _("Ahnentafel Report"), 
    _("Text"),
    AncestorBareReportDialog,
    write_book_item,
    _options,
    _style_name,
    _style_file,
    _make_default_style
   )
