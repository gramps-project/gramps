#
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

# $Id$

"""
Timeline report
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os

#------------------------------------------------------------------------
#
# GNOME/gtk
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import Utils
import Report
import BaseDoc
import GenericFilter
import Errors
import Date
import FontScale
import sort
from QuestionDialog import ErrorDialog

from gettext import gettext as _

#------------------------------------------------------------------------
#
# TimeLine
#
#------------------------------------------------------------------------
class TimeLine:

    def __init__(self,database,person,filter,title,sort_func,document,output,newpage=0):
        """
        Creates the Timeline object that produces the report. This class
        is used by the TimelineDialog class. The arguments are:

        database - the GRAMPS database
        person   - currently selected person
        output   - name of the output file
        document - BaseDoc instance for the output file. Any class derived
                   from BaseDoc may be used.
        filter   - filtering function selected by the TimeLineDialog
                   class.
        """
        self.d = document
	self.filter = filter
	self.db = database
	self.person = person
	self.output = output
        self.title = title
        self.sort_func = sort_func
        self.newpage = newpage
        self.setup()
        if output:
            self.standalone = 1
            self.d.open(output)
            self.d.init()
        else:
            self.standalone = 0

    def setup(self):
        """
        Define the graphics styles used by the report. Paragraph definitions
        have already been defined in the document. The styles used are:

        TLG-grid  - 0.5pt wide line dashed line. Used for the lines that make up
                the grid.
        TLG-line  - 0.5pt wide line. Used for the line connecting two endpoints
                and for the birth marker.
        TLG-solid - 0.5pt line with a black fill color. Used for the date of
                death marker.
        TLG-text  - Contains the TLG-Name paragraph style used for the individual's
                name
        TLG-title - Contains the TLG-Title paragraph style used for the title of
                the document
        TLG-label - Contains the TLG-Label paragraph style used for the year label's
                in the document.
        """
        g = BaseDoc.GraphicsStyle()
        g.set_line_width(0.5)
        g.set_color((0,0,0))
        self.d.add_draw_style("TLG-line",g)

        g = BaseDoc.GraphicsStyle()
        g.set_line_width(0.5)
        g.set_color((0,0,0))
        g.set_fill_color((0,0,0))
        self.d.add_draw_style("TLG-solid",g)

        g = BaseDoc.GraphicsStyle()
        g.set_line_width(0.5)
        g.set_color((0,0,0))
        g.set_fill_color((255,255,255))
        self.d.add_draw_style("open",g)

        g = BaseDoc.GraphicsStyle()
        g.set_line_width(0.5)
        g.set_line_style(BaseDoc.DASHED)
        g.set_color((0,0,0))
        self.d.add_draw_style("TLG-grid",g)

        g = BaseDoc.GraphicsStyle()
        g.set_paragraph_style("TLG-Name")
        g.set_color((255,255,255))
        g.set_fill_color((255,255,255))
        g.set_line_width(0)
        self.d.add_draw_style("TLG-text",g)

        g = BaseDoc.GraphicsStyle()
        g.set_paragraph_style("TLG-Title")
        g.set_color((255,255,255))
        g.set_fill_color((255,255,255))
        g.set_line_width(0)
        g.set_width(self.d.get_usable_width())
        self.d.add_draw_style("TLG-title",g)

        g = BaseDoc.GraphicsStyle()
        g.set_paragraph_style("TLG-Label")
        g.set_color((255,255,255))
        g.set_fill_color((255,255,255))
        g.set_line_width(0)
        self.d.add_draw_style("TLG-label",g)

    def write_report(self):

        (low,high) = self.find_year_range()

        st_size = self.name_size()

        font = self.d.style_list['TLG-Name'].get_font()
        
        incr = pt2cm(font.get_size())
        pad =  incr*.75
        
        x1,x2,y1,y2 = (0,0,0,0)

        start = st_size+0.5
        stop = self.d.get_usable_width()-0.5
        size = (stop-start)
        self.header = 2.0
        
        if self.newpage:
            self.d.page_break()
        self.d.start_page()

        index = 1
        current = 1;
        
        length = len(self.plist)

        self.plist.sort(self.sort_func)
        
        for p in self.plist:
            b = p.getBirth().getDateObj().getYear()
            d = p.getDeath().getDateObj().getYear()

            n = p.getPrimaryName().getName()
            self.d.draw_text('TLG-text',n,incr+pad,self.header + (incr+pad)*index)
            
            y1 = self.header + (pad+incr)*index
            y2 = self.header + ((pad+incr)*index)+incr
            y3 = (y1+y2)/2.0
            w = 0.05
            
            if b != Date.UNDEF:
                start_offset = ((float(b-low)/float(high-low)) * (size))
                x1 = start+start_offset
                path = [(x1,y1),(x1+w,y3),(x1,y2),(x1-w,y3)]
                self.d.draw_path('TLG-line',path)

            if d != Date.UNDEF:
                start_offset = ((float(d-low)/float(high-low)) * (size))
                x1 = start+start_offset
                path = [(x1,y1),(x1+w,y3),(x1,y2),(x1-w,y3)]
                self.d.draw_path('TLG-solid',path)

            if b != Date.UNDEF and d != Date.UNDEF:
                start_offset = ((float(b-low)/float(high-low)) * size) + w
                stop_offset = ((float(d-low)/float(high-low)) * size) - w

                x1 = start+start_offset
                x2 = start+stop_offset
                self.d.draw_line('open',x1,y3,x2,y3)

            if (y2 + incr) >= self.d.get_usable_height():
                if current != length:
                    self.build_grid(low,high,start,stop)
                    self.d.end_page()
                    self.d.start_page()
                    self.build_grid(low,high,start,stop)
                index = 1
                x1,x2,y1,y2 = (0,0,0,0)
            else:
                index += 1;
            current += 1
            
        self.build_grid(low,high,start,stop)
        self.d.end_page()    
        if self.standalone:
            self.d.close()

    def build_grid(self,year_low,year_high,start_pos,stop_pos):
        """
        Draws the grid outline for the chart. Sets the document label,
        draws the vertical lines, and adds the year labels. Arguments
        are:

        year_low  - lowest year on the chart
        year_high - highest year on the chart
        start_pos - x position of the lowest leftmost grid line
        stop_pos  - x position of the rightmost grid line
        """
        width = self.d.get_usable_width()

        title_font = self.d.style_list['TLG-Title'].get_font()
        normal_font = self.d.style_list['TLG-Name'].get_font()
        label_font = self.d.style_list['TLG-Label'].get_font()

        self.d.center_text('TLG-title',self.title,width/2.0,0)
        
        label_y = self.header - (pt2cm(normal_font.get_size())*1.2)
        top_y = self.header
        bottom_y = self.d.get_usable_height()
        
        incr = (year_high - year_low)/5
        delta = (stop_pos - start_pos)/ 5

        for val in range(0,6):
            year_str = str(year_low + (incr*val))

            xpos = start_pos+(val*delta)
            self.d.center_text('TLG-label', year_str, xpos, label_y)
            self.d.draw_line('TLG-grid', xpos, top_y, xpos, bottom_y)

    def find_year_range(self):
        low  =  999999
	high = -999999
	
        self.plist = self.filter.apply(self.db,self.db.getPersonMap().values())

	for p in self.plist:
	    b = p.getBirth().getDateObj().getYear()
	    d = p.getDeath().getDateObj().getYear()

	    if b != Date.UNDEF:
	       low = min(low,b)
	       high = max(high,b)

	    if d != Date.UNDEF:
	       low = min(low,d)
	       high = max(high,d)
               
	low = (low/10)*10
	high = ((high+9)/10)*10
        
        if low == Date.UNDEF:
            low = high
        if high == Date.UNDEF:
            high = low
        
        return (low,high)

    def name_size(self):
        self.plist = self.filter.apply(self.db,self.db.getPersonMap().values())

        style_name = self.d.draw_styles['TLG-text'].get_paragraph_style()
        font = self.d.style_list[style_name].get_font()
        
        size = 0
	for p in self.plist:
            n = p.getPrimaryName().getName()
            size = max(FontScale.string_width(font,n),size)
        return pt2cm(size)


#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def _make_default_style(default_style):
    """Make the default output style for the Timeline report."""
    f = BaseDoc.FontStyle()
    f.set_size(10)
    f.set_type_face(BaseDoc.FONT_SANS_SERIF)
    p = BaseDoc.ParagraphStyle()
    p.set_font(f)
    p.set_description(_("The style used for the person's name."))
    default_style.add_style("TLG-Name",p)

    f = BaseDoc.FontStyle()
    f.set_size(8)
    f.set_type_face(BaseDoc.FONT_SANS_SERIF)
    p = BaseDoc.ParagraphStyle()
    p.set_font(f)
    p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
    p.set_description(_("The style used for the year labels."))
    default_style.add_style("TLG-Label",p)

    f = BaseDoc.FontStyle()
    f.set_size(14)
    f.set_type_face(BaseDoc.FONT_SANS_SERIF)
    p = BaseDoc.ParagraphStyle()
    p.set_font(f)
    p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
    p.set_description(_("The style used for the title of the page."))
    default_style.add_style("TLG-Title",p)

#------------------------------------------------------------------------
#
# Builds filter list for this report
#
#------------------------------------------------------------------------
def _get_report_filters(person):
    """Set up the list of possible content filters."""

    name = person.getPrimaryName().getName()
        
    all = GenericFilter.GenericFilter()
    all.set_name(_("Entire Database"))
    all.add_rule(GenericFilter.Everyone([]))

    des = GenericFilter.GenericFilter()
    des.set_name(_("Descendants of %s") % name)
    des.add_rule(GenericFilter.IsDescendantOf([person.getId()]))

    ans = GenericFilter.GenericFilter()
    ans.set_name(_("Ancestors of %s") % name)
    ans.add_rule(GenericFilter.IsAncestorOf([person.getId()]))

    com = GenericFilter.GenericFilter()
    com.set_name(_("People with common ancestor with %s") % name)
    com.add_rule(GenericFilter.HasCommonAncestorWith([person.getId()]))

    return [all,des,ans,com]

#------------------------------------------------------------------------
#
# Builds list of sorting functions for this report
#
#------------------------------------------------------------------------
def _get_sort_functions():
    return [
        (_("Birth Date"),sort.by_birthdate),
        (_("Name"),sort.by_last_name), 
    ]

#------------------------------------------------------------------------
#
# TimeLineDialog
#
#------------------------------------------------------------------------
class TimeLineDialog(Report.DrawReportDialog):

    report_options = {}

    def __init__(self,database,person):
        Report.DrawReportDialog.__init__(self,database,person,self.report_options)

    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" % (_("Timeline Graph"),
                                     _("Graphical Reports"))

    def get_header(self, name):
        """The header line at the top of the dialog contents."""
        return _("Timeline Graph for %s") % name

    def get_stylesheet_savefile(self):
        """Where to save user defined styles for this report."""
        return _style_file

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Timeline File")

    def get_report_generations(self):
        """No generation options."""
        return (0, 0)
    
    def add_user_options(self):
        """
        Override the base class add_user_options task to add a menu that allows
        the user to select the sort method.
        """
        
        self.sort_style = gtk.OptionMenu()
        self.sort_menu = gtk.Menu()

        sort_functions = _get_sort_functions()
        for item in sort_functions:
            menuitem = gtk.MenuItem(item[0])
            menuitem.set_data('sort',item[1])
            menuitem.show()
            self.sort_menu.append(menuitem)

        self.sort_style.set_menu(self.sort_menu)
        self.add_option(_('Sort by'),self.sort_style)

        self.title_box = gtk.Entry()
        self.title_box.set_text(self.get_header(self.person.getPrimaryName().getName()))
        self.title_box.show()
        self.add_option(_('Title'),self.title_box)
        
    def get_report_filters(self):
        return _get_report_filters(self.person)

    def make_default_style(self):
        _make_default_style(self.default_style)

    def make_report(self):

        title = unicode(self.title_box.get_text())
        sort_func = self.sort_menu.get_active().get_data('sort')

        try:
            MyReport = TimeLine(self.db, self.person, 
                    self.filter, title, sort_func, self.doc, self.target_path)
            MyReport.write_report()
        except Errors.FilterError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)
        except Errors.ReportError, msg:
            (m1,m2) = msg.messages()
            ErrorDialog(m1,m2)
        except:
            import DisplayTrace
            DisplayTrace.DisplayTrace()

#------------------------------------------------------------------------
#
# point to centimeter convertion
#
#------------------------------------------------------------------------
def pt2cm(val):
    return (float(val)/28.3465)

#------------------------------------------------------------------------
#
# entry point
#
#------------------------------------------------------------------------
def report(database,person):
    """
    report - task starts the report. The plugin system requires that the
    task be in the format of task that takes a database and a person as
    its arguments.
    """
    TimeLineDialog(database,person)

def get_description():
    """
    get_description - returns a descriptive name for the report. The plugin
    system uses this to provide a description in the report selector.
    """
    return _("Generates a timeline graph.")


#------------------------------------------------------------------------
#
# Set up sane defaults for the book_item
#
#------------------------------------------------------------------------
_style_file = "timeline.xml"
_style_name = "default" 

_person_id = ""
_filter_num = 0
_sort_func_num = 0
_title_str = ""
_options = ( _person_id, _filter_num, _sort_func_num, _title_str )

#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class TimeLineBareDialog(Report.BareReportDialog):

    def __init__(self,database,person,opt,stl):

        self.options = opt
        self.db = database
        if self.options[0]:
            self.person = self.db.getPerson(self.options[0])
        else:
            self.person = person
        self.style_name = stl

        Report.BareReportDialog.__init__(self,database,self.person)

        self.filter_num = int(self.options[1])
        self.sort_func_num = int(self.options[2])
        self.title_str = self.options[3]
        self.new_person = None

        self.filter_combo.set_history(self.filter_num)
        self.sort_style.set_history(self.sort_func_num)
        self.title_box.set_text(self.title_str)

        self.window.run()

    #------------------------------------------------------------------------
    #
    # Customization hooks
    #
    #------------------------------------------------------------------------
    def get_title(self):
        """The window title for this dialog"""
        return "%s - GRAMPS Book" % (_("Timeline Graph"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Timeline Graph for GRAMPS Book") 

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return _style_file
    
    def get_report_generations(self):
        """No generations, no page breaks."""
        return (0, 0)
    
    def add_user_options(self):
        """
        Override the base class add_user_options task to add a menu that allows
        the user to select the sort method.
        """
        
        self.sort_style = gtk.OptionMenu()
        self.sort_menu = gtk.Menu()

        sort_functions = _get_sort_functions()
        for item in sort_functions:
            menuitem = gtk.MenuItem(item[0])
            menuitem.set_data('sort',item[1])
            menuitem.show()
            self.sort_menu.append(menuitem)

        self.sort_style.set_menu(self.sort_menu)
        self.add_option(_('Sort by'),self.sort_style)

        self.title_box = gtk.Entry()
        self.title_box.show()
        self.add_option(_('Title'),self.title_box)

    def make_default_style(self):
        _make_default_style(self.default_style)

    def get_report_filters(self):
        return _get_report_filters(self.person)

    def on_cancel(self, obj):
        pass

    def on_ok_clicked(self, obj):
        """The user is satisfied with the dialog choices. Parse all options
        and close the window."""

        # Preparation
        self.parse_style_frame()
        
        if self.new_person:
            self.person = self.new_person
        self.filter_num = self.filter_combo.get_history()
        self.sort_func_num = self.sort_style.get_history()
        self.title_str = unicode(self.title_box.get_text())

        self.options = ( self.person.getId(), self.filter_num, 
            self.sort_func_num, self.title_str )
        self.style_name = self.selected_style.get_name()

#------------------------------------------------------------------------
#
# Function to write Book Item 
#
#------------------------------------------------------------------------
def write_book_item(database,person,doc,options,newpage=0):
    """Write the Timeline Graph using options set.
    All user dialog has already been handled and the output file opened."""
    try:
        if options[0]:
            person = database.getPerson(options[0])
        filter_num = int(options[1])
        filters = _get_report_filters(person)
        afilter = filters[filter_num]
        sort_func_num = int(options[2])
        sort_functions = _get_sort_functions()
        sort_func = sort_functions[sort_func_num][1]
        title_str = options[3]
        return TimeLine(database, person, 
                    afilter, title_str, sort_func, doc, None, newpage )
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
# Register the TimeLine report with the plugin system. The register_report
# task of the Plugins module takes the following arguments.
#
# task - function that starts the task
# name - Name of the report
# status - alpha/beta/production
# category - Category entry in the menu system.
# author_name - Name of the author
# author_email - Author's email address
# description - function that returns the description of the report
#
#------------------------------------------------------------------------
from Plugins import register_report, register_book_item

register_report(
    task=report,
    name=_("Timeline Graph"),
    status=(_("Beta")),
    category=_("Graphical Reports"),
    author_name="Donald N. Allingham",
    author_email="dallingham@users.sourceforge.net",
    description=get_description()
    )

# (name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style)
register_book_item( 
    _("Timeline Graph"), 
    _("Graphics"),
    TimeLineBareDialog,
    write_book_item,
    _options,
    _style_name,
    _style_file,
    _make_default_style
    )
