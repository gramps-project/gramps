#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

import RelLib
import os
import string
import intl

_ = intl.gettext

from Report import *

import gtk
import gnome.ui
import libglade

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class AncestorReport(Report):

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,database,person,output,max,doc,pgbrk):
        self.map = {}
        self.database = database
        self.start = person
        self.max_generations = max
        self.pgbrk = pgbrk
        self.doc = doc

        try:
            self.doc.open(output)
        except IOError,msg:
            gnome.ui.GnomeErrorDialog(_("Could not open %s") % output + "\n" + msg)
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def filter(self,person,index):
        if person == None or index >= 2**self.max_generations:
            return
        self.map[index] = person
    
        family = person.getMainFamily()
        if family != None:
            self.filter(family.getFather(),index*2)
            self.filter(family.getMother(),(index*2)+1)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def write_report(self):

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
            if generation == 0 or key >= 2**generation:
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

        self.doc.close()
 

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class AncestorReportDialog(TextReportDialog):
    def __init__(self,database,person):
        TextReportDialog.__init__(self,database,person)

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return _("Gramps - Ahnentafel Report")

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Ahnentafel Report for %s") % name

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Save Ancestor Report")

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return "ancestor_report.xml"
    
    #------------------------------------------------------------------------
    #
    # Create output styles appropriate to this report.
    #
    #------------------------------------------------------------------------
    def make_default_style(self):
        """Make the default output style for the Ahnentafel report."""
        font = FontStyle()
        font.set(face=FONT_SANS_SERIF,size=16,bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set(pad=0.5)
        self.default_style.add_style("Title",para)
    
        font = FontStyle()
        font.set(face=FONT_SANS_SERIF,size=14,italic=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set(pad=0.5)
        self.default_style.add_style("Generation",para)
    
        para = ParagraphStyle()
        para.set(first_indent=-1.0,lmargin=1.0,pad=0.25)
        self.default_style.add_style("Entry",para)

    #------------------------------------------------------------------------
    #
    # Create the contents of the report.
    #
    #------------------------------------------------------------------------
    def make_report(self):
        """Create the object that will produce the Ahnentafel Report.
        All user dialog has already been handled and the output file
        opened."""
        MyReport = AncestorReport(self.db, self.person, self.target_path,
                                  self.max_gen, self.doc, self.pg_brk)
        MyReport.write_report()


#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    AncestorReportDialog(database,person)


#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def get_xpm_image():
    return [
        "48 48 4 1",
        " 	c None",
        ".	c #FFFFFF",
        "+	c #C0C0C0",
        "@	c #000000",
        "                                                ",
        "                                                ",
        "                                                ",
        "       ++++++++++++++++++++++++++++++++++       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +...@@@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +...@@@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +........@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +........@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.....@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       ++++++++++++++++++++++++++++++++++       ",
        "                                                ",
        "                                                ",
        "                                                "]

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
from Plugins import register_report

register_report(
    report,
    _("Ahnentafel Report"),
    category=_("Text Reports"),
    description= _("Produces a textual ancestral report"),
    xpm=get_xpm_image()
    )

