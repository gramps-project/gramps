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

"Generate files/Descendant Report"

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
from gettext import gettext as _

#------------------------------------------------------------------------
#
# GTK/GNOME modules
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
from PluginUtils import register_report
from ReportBase import Report, ReportUtils, ReportOptions, \
     CATEGORY_DRAW, MODE_GUI, MODE_BKI, MODE_CLI

pt2cm = ReportUtils.pt2cm
import BaseDoc
from SubstKeywords import SubstKeywords
import Errors
from BasicUtils import NameDisplay

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------
_BORN = _('b.')
_DIED = _('d.')
_sep = 0.5

class GraphLayout:

    def __init__(self,database,plist,person_handle):
        self.database = database
        self.plist = plist
        self.person_handle = person_handle
        self.v = []
        self.e = []
        self.maxx = 0
        self.maxy = 0

    def max_size(self):
        return (self.maxx,self.maxy)
    
    def layout(self):
        return ([],[])

class DescendLine(GraphLayout):

    def layout(self):
        self.elist = [(0,0)]
        try:
            self.space_for(self.person_handle)
        except RuntimeError,msg:
            person = self.database.get_person_from_handle(self.person_handle)
            raise Errors.DatabaseError(
                _("Database error: %s is defined as his or her own ancestor") %
                NameDisplay.displayer.display(person))
        
        return (self.v,self.e[1:])
    
    def space_for(self,person_handle,level=1.0,pos=1.0):

        person = self.database.get_person_from_handle(person_handle)
            
        last = self.elist[-1]
        self.elist.append((level,pos))
        self.e.append((last[0],last[1],level,pos))
        self.v.append((person_handle,level,pos))
        if level > self.maxx:
            self.maxx = level
        if pos > self.maxy:
            self.maxy = pos
            
        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            for child_handle in family.get_child_handle_list():
                self.space_for(child_handle,level+1.0,pos)
                pos = pos + max(self.depth(child_handle),1)
                if pos > self.maxy:
                    self.maxy = pos
        self.elist.pop()
        
    def depth(self,person_handle,val=0):
        person = self.database.get_person_from_handle(person_handle)
        for family_handle in person.get_family_handle_list():
            family = self.database.get_family_from_handle(family_handle)
            clist = family.get_child_handle_list()
            val = val + len(clist)
            for child_handle in clist:
                d = self.depth(child_handle)
                if d > 0:
                   val = val + d - 1 #first child is always on the same
        return val                   #row as the parent, so subtract 1

#------------------------------------------------------------------------
#
# DescendantGraph
#
#------------------------------------------------------------------------
class DescendantGraph(Report):

    def __init__(self,database,person,options_class):
        """
        Creates DescendantGraph object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        dispf     - Display format for the output box.
        """
        Report.__init__(self,database,person,options_class)

        self.display = options_class.handler.options_dict['dispf']

        self.map = {}
        self.text = {}

        self.box_width = 0
        self.height = 0
        self.lines = 0

        plist = self.database.get_person_handles(sort_handles=False)
        self.layout = DescendLine(self.database,plist,person.get_handle())
        (self.v,self.e) = self.layout.layout()
        
        self.text = {}
        for (p_id,x,y) in self.v:

            self.text[p_id] = []
            subst = SubstKeywords(self.database,p_id)
            for line in self.display:
                self.text[p_id].append(subst.replace(line))

            self.font = self.doc.style_list["DG-Normal"].get_font()
            for line in self.text[p_id]:
                new_width = self.doc.string_width(self.font,line)
                self.box_width = max(self.box_width,new_width)

            self.lines = max(self.lines,len(self.text[p_id]))
        self.calc()

    def write_report(self):

        maxx,maxy = self.layout.max_size()

        maxx = int(maxx)
        maxy = int(maxy)

        cols = ((maxx-1)/self.maxx)
        rows = ((maxy-1)/self.maxy)

        self.pg = []
        self.ln = []

        for i in range(rows+1):
            self.pg.append([None]*(cols+1))
            self.ln.append([None]*(cols+1))

        for (p_id,x,y) in self.v:
            r = int((y-1)/self.maxy)
            c = int((x-1)/self.maxx)

            nx = x - (self.maxx)*c
            ny = y - (self.maxy)*r
            l = self.pg[r]
            if l[c] == None:
                l[c] = [(p_id,nx,ny)]
            else:
                l[c].append((p_id,nx,ny))

        for (x1,y1,x2,y2) in self.e:
            r1 = int((y1-1)/self.maxy)
            c1 = int((x1-1)/self.maxx)
            r2 = int((y2-1)/self.maxy)
            c2 = int((x2-1)/self.maxx)

            nx1 = x1 - (self.maxx)*c1
            nx2 = x2 - (self.maxx)*c2
            ny1 = y1 - (self.maxy)*r1
            ny2 = y2 - (self.maxy)*r2
            if r1 == r2:
                if c1 == c2:
                    l = self.ln[r1][c1]
                    if l == None:
                        self.ln[r1][c1] = [(nx1,ny1,nx2,ny2)]
                    else:
                        l.append((nx1,ny1,nx2,ny2))
                else:
                    l1 = self.ln[r1][c1]
                    l2 = self.ln[r2][c2]
                    if l1 == None:
                        self.ln[r1][c1] = [(nx1,ny1,-nx2,ny2)]
                    else:
                        l1.append((nx1,ny1,-nx2,ny2))
                    if l2 == None:
                        self.ln[r2][c2] = [(-nx2,ny2,nx2,ny2)]
                    else:
                        l2.append((-nx2,ny2,nx2,ny2))
                        
                    for c in range(c1+1,c2):
                        if self.ln[r1][c]:
                            self.ln[r1][c].append((nx1,-ny1,nx2,-ny2))
                        else:
                            self.ln[r1][c] = [(nx1,-ny1,nx2,-ny2)]
            else:
                if c1 == c2:
                    l1 = self.ln[r1][c1]
                    l2 = self.ln[r2][c2]
                    if l1 == None:
                        self.ln[r1][c1] = [(nx1,ny1,nx2,-ny2)]
                    else:
                        l1.append((nx1,ny1,nx2,-ny2))
                    if l2 == None:
                        self.ln[r2][c2] = [(nx1,-ny2,nx2,ny2)]
                    else:
                        l2.append((nx1,-ny2,nx2,ny2))
                    for r in range(r1+1,r2):
                        if self.ln[r][c1]:
                            self.ln[r][c1].append((nx1,-ny1,nx2,-ny2))
                        else:
                            self.ln[r][c1] = [(nx1,-ny1,nx2,-ny2)]
                else:
                    l1 = self.ln[r1][c1]
                    l2 = self.ln[r2][c2]
                    l3 = self.ln[r2][c1]

                    if l1 == None:
                        self.ln[r1][c1] = [(nx1,ny1,-nx2,-ny2)]
                    else:
                        l1.append((nx1,ny1,-nx2,-ny2))

                    if l2 == None:
                        self.ln[r2][c2] = [(-nx1,ny2,nx2,ny2)]
                    else:
                        l2.append((-nx1,ny2,nx2,ny2))

                    if l3 == None:
                        self.ln[r2][c1] = [(nx1,-ny2,-nx2,ny2)]
                    else:
                        l3.append((nx1,-ny2,-nx2,ny2))
            
        for r in range(len(self.pg)):
            for c in range(len(self.pg[r])):
                self.print_page(self.pg[r][c],self.ln[r][c],r,c)
        
    def calc(self):
        """calc - calculate the maximum width that a box needs to be. From
        that and the page dimensions, calculate the proper place to put
        the elements on a page."""
        self.height = self.lines*pt2cm(1.25*self.font.get_size())
        self.box_width = pt2cm(self.box_width+20)

        self.maxx = int(self.doc.get_usable_width()/(self.box_width+_sep))
        self.maxy = int(self.doc.get_usable_height()/(self.height+_sep))

        g = BaseDoc.GraphicsStyle()
        g.set_height(self.height)
        g.set_width(self.box_width)
        g.set_paragraph_style("DG-Normal")
        g.set_shadow(1)
        self.doc.add_draw_style("box",g)

        g = BaseDoc.GraphicsStyle()
        self.doc.add_draw_style("line",g)

    def print_page(self, plist,elist,r,c):
        self.doc.start_page()

        delta = self.doc.get_usable_width()/(self.maxx)
        top = 0
        bottom = self.doc.get_usable_height()
        left = 0
        right = self.doc.get_usable_width() - (2*_sep)

        if plist:
            for (p_id,x,y) in plist:
                name = '\n'.join(self.text[p_id])
                x = (x-1)*delta + left + _sep
                y = (y-1)*(self.height+_sep)+top
                self.doc.draw_box("box",name,x,y)
        if elist:
            for (x1,y1,x2,y2) in elist:
                if x1 < 0:
                    nx1 = left
                else:
                    nx1 = (x1-1) * delta + left + self.box_width + _sep
                if x2 < 0:
                    nx2 = right + _sep
                else:
                    nx2 = (x2-1) * delta + left + _sep
                if y1 < 0:
                    ny1 = top
                else:
                    ny1 = (y1-1)*(self.height+_sep)+ top + self.height/2.0
                if y2 < 0:
                    ny2 = bottom
                else:
                    ny2 = (y2-1)*(self.height+_sep) + top + self.height/2.0
                if y1 < 0 and y2 < 0:
                    half = (nx1+nx2)/2.0
                    self.doc.draw_line("line",half,ny1,half,ny2)
                elif ny1 != ny2:
                    if x1 == -x2:
                        self.doc.draw_line("line",nx1,ny1,nx2,ny2)
                    else:
                        half = (nx1+nx2)/2.0
                        if y1 > 0:
                            self.doc.draw_line("line",nx1,ny1,half,ny1)
                        self.doc.draw_line("line",half,ny1,half,ny2)
                        if y2 > 0:
                            self.doc.draw_line("line",half,ny2,nx2,ny2)
                else:
                    self.doc.draw_line("line",nx1,ny1,nx2,ny2)

        y = bottom + (self.doc.get_bottom_margin()/2.0)
        if r or c:
            self.doc.write_at("DG-Normal","(%d,%d)" % (r,c), right, y)
        self.doc.end_page()


#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class DescendantGraphOptions(ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.__init__(self,name,person_id)

    def enable_options(self):
        # Semi-common options that should be enabled for this report
        self.enable_dict = {
            'dispf'     : [ "$n", "%s $b" % _BORN, "%s $d" % _DIED ],
        }

    def get_textbox_info(self):
        """Label the textbox and provide the default contents."""
        return (_("Display Format"), self.options_dict['dispf'],
                _("Allows you to customize the data in the boxes in the report"))

    def add_user_options(self,dialog):
        """
        Override the base class add_user_options task to add a menu that allows
        the user to select the sort method.
        """
        dialog.get_report_extra_textbox_info = self.get_textbox_info

    def make_default_style(self,default_style):
        """Make the default output style for the Descendant Graph report."""
        f = BaseDoc.FontStyle()
        f.set_size(9)
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        p = BaseDoc.ParagraphStyle()
        p.set_font(f)
        p.set_description(_('The basic style used for the text display.'))
        default_style.add_style("DG-Normal",p)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'descendant_graph',
    category = CATEGORY_DRAW,
    report_class = DescendantGraph,
    options_class = DescendantGraphOptions,
    modes = MODE_GUI | MODE_BKI | MODE_CLI,
    translated_name = _("Descendant Graph"),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description = _("Generates a graph of descendants of the active person"),
    unsupported = True,
    )
