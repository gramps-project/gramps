#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2004  Donald N. Allingham
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
import string

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
import GraphLayout
import FontScale
import Report
import BaseDoc
import Errors

from SubstKeywords import SubstKeywords
from gettext import gettext as _
from QuestionDialog import ErrorDialog

_BORN = _('b.')
_DIED = _('d.')

#------------------------------------------------------------------------
#
# constants
#
#------------------------------------------------------------------------
_sep = 0.5

#------------------------------------------------------------------------
#
# pt2cm - convert points to centimeters
#
#------------------------------------------------------------------------
def pt2cm(pt):
    return (float(pt)/72.0)*2.54

#------------------------------------------------------------------------
#
# DescendantReport
#
#------------------------------------------------------------------------
class DescendantReport:

    def __init__(self,database,person,display,doc,output,newpage=0):
        self.database = database
        self.doc = doc
        self.doc.creator(database.get_researcher().get_name())
        self.map = {}
        self.text = {}
        self.start = person
        self.output = output
        self.box_width = 0
        self.height = 0
        self.lines = 0
        self.display = display
        self.newpage = newpage
        if output:
            self.standalone = 1
            self.doc.open(output)
        else:
            self.standalone = 0

        plist = self.database.get_person_keys()
        self.layout = GraphLayout.DescendLine(self.database,plist,person.get_id())
        (self.v,self.e) = self.layout.layout()
        
        self.text = {}
        for (p_id,x,y) in self.v:

            self.text[p_id] = []
            subst = SubstKeywords(self.database,p_id)
            for line in self.display:
                self.text[p_id].append(subst.replace(line))

            self.font = self.doc.style_list["DG-Normal"].get_font()
            for line in self.text[p_id]:
                new_width = FontScale.string_width(self.font,line)
                self.box_width = max(self.box_width,new_width)

            self.lines = max(self.lines,len(self.text[p_id]))

    def write_report(self):

        self.calc()
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
            
        if self.newpage:
            self.doc.page_break()

        for r in range(len(self.pg)):
            for c in range(len(self.pg[r])):
                self.print_page(self.pg[r][c],self.ln[r][c],r,c)
        
        if self.standalone:
            self.doc.close()

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
        if self.standalone:
            self.doc.init()

    def print_page(self, plist,elist,r,c):
        self.doc.start_page()

        delta = self.doc.get_usable_width()/(self.maxx)
        top = 0
        bottom = self.doc.get_usable_height()
        left = 0
        right = self.doc.get_usable_width() - (2*_sep)

        if plist:
            for (p_id,x,y) in plist:
                name = string.join(self.text[p_id],"\n")
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
                    print x1,x2,y1,y2,nx1,nx2,half
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
def _make_default_style(default_style):
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
# DescendantReportDialog
#
#------------------------------------------------------------------------
class DescendantReportDialog(Report.DrawReportDialog):

    def __init__(self,database,person):
        Report.DrawReportDialog.__init__(self,database,person)

    def get_title(self):
        return "%s - %s - GRAMPS" % (_("Descendant Graph"),_("Graphical Reports"))

    def get_header(self,name):
        return _("Descendant Graph for %s") % name

    def get_target_browser_title(self):
        return _("Save Descendant Graph")

    def get_stylesheet_savefile(self):
        return _style_file

    def get_report_generations(self):
        """Default to 10 generations, no page breaks."""
        return (0, 0)
    
    def get_report_extra_textbox_info(self):
        """Label the textbox and provide the default contents."""
        return (_("Display Format"), "$n\n%s $b\n%s $d" % (_BORN,_DIED),
                _("Allows you to customize the data in the boxes in the report"))
    
    def make_default_style(self):
        _make_default_style(self.default_style)

    def make_report(self):
        """Create the object that will produce the Descendant Graph.
        All user dialog has already been handled and the output file
        opened."""
        try:
            MyReport = DescendantReport(self.db, self.person, 
                self.report_text, self.doc, self.target_path)
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
# 
#
#------------------------------------------------------------------------
def report(database,person):
    DescendantReportDialog(database,person)

#------------------------------------------------------------------------
#
# Set up sane defaults for the book_item
#
#------------------------------------------------------------------------
_style_file = "descendant_graph.xml"
_style_name = "default" 

_person_id = ""
_disp_format = [ "$n", "%s $b" % _BORN, "%s $d" % _DIED ]
_options = ( _person_id, _disp_format )

#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class DescendantGraphBareDialog(Report.BareReportDialog):

    def __init__(self,database,person,opt,stl):

        self.options = opt
        self.db = database
        if self.options[0]:
            self.person = self.db.get_person(self.options[0])
        else:
            self.person = person
        self.style_name = stl

        Report.BareReportDialog.__init__(self,database,self.person)

        self.disp_format = string.join(self.options[1],'\n')
        self.new_person = None

        self.extra_textbox.get_buffer().set_text(
            self.disp_format,len(self.disp_format))
        
        self.window.run()

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return "%s - GRAMPS Book" % (_("Descendant Graph"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Descendant Graph for GRAMPS Book") 

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return _style_file
    
    def get_report_generations(self):
        """No generations, no page breaks."""
        return (0, 0)
    
    def get_report_extra_textbox_info(self):
        """Label the textbox and provide the default contents."""
        return (_("Display Format"), "$n\n%s $b\n%s $d" % (_BORN,_DIED),
                _("Allows you to customize the data in the boxes in the report"))

    def make_default_style(self):
        _make_default_style(self.default_style)

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
        self.options = ( self.person.get_id(), self.report_text )
        self.style_name = self.selected_style.get_name()

#------------------------------------------------------------------------
#
# Function to write Book Item 
#
#------------------------------------------------------------------------
def write_book_item(database,person,doc,options,newpage=0):
    """Write the Ancestor Chart using options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options[0]:
            person = database.get_person(options[0])
        disp_format = options[1]
        return DescendantReport(database, person, 
                                   disp_format, doc, None, newpage )
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
from Plugins import register_report, register_book_item

register_report(
    report,
    _("Descendant Graph"),
    category=_("Graphical Reports"),
    description=_("Generates a graph of descendants of the active person"),
    status=(_("Alpha")),
    author_name="Donald N. Allingham",
    author_email="dallingham@users.sourceforge.net"
    )

# (name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style)
register_book_item( 
    _("Descendant Graph"), 
    _("Graphics"),
    DescendantGraphBareDialog,
    write_book_item,
    _options,
    _style_name,
    _style_file,
    _make_default_style
    )
