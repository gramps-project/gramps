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

"Generate files/Descendant Report"

import os
import sort
import string
import intl

_ = intl.gettext

from Report import *

import gtk
import libglade

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DescendantReport:

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def __init__(self,db,person,name,max,doc):
        self.creator = db.getResearcher().getName()
        self.name = name
        self.person = person
        self.max_generations = max
        self.doc = doc
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def setup(self):
        self.doc.open(self.name)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def end(self):
        self.doc.close()

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def dump_dates(self, person):
        birth = person.getBirth().getDateObj().get_start_date()
        death = person.getDeath().getDateObj().get_start_date()
        if birth.getYearValid() or death.getYearValid():
            self.doc.write_text(' (')
            if birth.getYearValid():
                self.doc.write_text('b. ' + str(birth.getYear()))
            if death.getYearValid():
                if birth.getYearValid():
                    self.doc.write_text(', ')
                self.doc.write_text('d. ' + str(death.getYear()))
            self.doc.write_text(')')
        
    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def report(self):
        self.doc.start_paragraph("Title")
        name = self.person.getPrimaryName().getRegularName()
        self.doc.write_text(_("Descendants of %s") % name)
        self.dump_dates(self.person)
        self.doc.end_paragraph()
        self.dump(0,self.person)

    #--------------------------------------------------------------------
    #
    # 
    #
    #--------------------------------------------------------------------
    def dump(self,level,person):

        if level != 0:
            self.doc.start_paragraph("Level" + str(level))
            self.doc.write_text(str(level) + '. ')
            self.doc.write_text(person.getPrimaryName().getRegularName())
            self.dump_dates(person)
            self.doc.end_paragraph()

        if (level >= self.max_generations):
            return
        
        childlist = []
        for family in person.getFamilyList():
            for child in family.getChildList():
                childlist.append(child)

        childlist.sort(sort.by_birthdate)
        for child in childlist:
            self.dump(level+1,child)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DescendantReportDialog(TextReportDialog):
    def __init__(self,person,database):
        TextReportDialog.__init__(self,database,person)

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return _("Gramps - Descendant Report")

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Descendant Report for %s") % name

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Save Descendant Report")

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return "descend_report.xml"
    
    #------------------------------------------------------------------------
    #
    # Create output styles appropriate to this report.
    #
    #------------------------------------------------------------------------
    def make_default_style(self):
        """Make the default output style for the Descendant Report."""
        f = FontStyle()
        f.set_size(14)
        f.set_type_face(FONT_SANS_SERIF)
        f.set_bold(1)
        p = ParagraphStyle()
        p.set_header_level(1)
        p.set_font(f)
        self.default_style.add_style("Title",p)

        f = FontStyle()
        for i in range(1,10):
            p = ParagraphStyle()
            p.set_font(f)
            p.set_left_margin(float(i-1))
            self.default_style.add_style("Level" + str(i),p)

    #------------------------------------------------------------------------
    #
    # Create the contents of the report.
    #
    #------------------------------------------------------------------------
    def make_report(self):
        """Create the object that will produce the Descendant Report.
        All user dialog has already been handled and the output file
        opened."""
        MyReport = DescendantReport(self.db, self.person, self.target_path,
                                    self.max_gen, self.doc)
        MyReport.setup()
        MyReport.report()
        MyReport.end()
        
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def report(database,person):
    DescendantReportDialog(person,database)

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
        "       +...@@@@@@@@@@@@@@@@@@@@@@@@@@...+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +...@@@@@@@@@@@..................+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +......@@@@@@@@@@@...............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +......@@@@@@@@@@@...............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.............@@@@@@@@@@@........+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.............@@@@@@@@@@@........+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +......@@@@@@@@@@@...............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +.........@@@@@@@@@@@............+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +............@@@@@@@@@@@.........+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +................@@@@@@@@@@......+       ",
        "       +................................+       ",
        "       +................................+       ",
        "       +................@@@@@@@@@@......+       ",
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
    _("Descendant Report"),
    category=_("Text Reports"),
    status=(_("Beta")),
    description=_("Generates a list of descendants of the active person"),
    xpm=get_xpm_image()
    )

