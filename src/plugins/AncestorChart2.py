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

"Graphical Reports/Ancestor Chart"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import math
from TransUtils import sgettext as _

#------------------------------------------------------------------------
#
# gtk
#
#------------------------------------------------------------------------
import gtk

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import BaseDoc
from SubstKeywords import SubstKeywords
from PluginUtils import Report, ReportOptions, ReportUtils, register_report
pt2cm = ReportUtils.pt2cm
cm2pt = ReportUtils.cm2pt

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------
_BORN = _('b.')
_DIED = _('d.')

#------------------------------------------------------------------------
#
# log2val
#
#------------------------------------------------------------------------
def log2(val):
    return int(math.log10(val)/math.log10(2))

#------------------------------------------------------------------------
#
# Layout class
#
#------------------------------------------------------------------------
class GenChart:

    def __init__(self,generations):
        self.generations = generations
        self.size = (2**(generations))
        self.array = [None]*(self.size)
        self.map = {}
        self.compress_map = {}
        
        for i in range(0,(self.size)):
            self.array[i] = [0]*generations

        self.max_x = 0
        self.ad = (self.size,generations)

    def set(self,index,value):
        x = log2(index)
        y = index - (2**x)
        delta = int((self.size/(2**(x))))
        new_y = int((delta/2) + (y)*delta)
        self.array[new_y][x] = (value,index)
        self.max_x = max(x,self.max_x)
        self.map[value] = (new_y,x)

    def index_to_xy(self,index):
        if index:
            x = log2(index)
            ty = index - (2**x)
            delta = int(self.size/(2**x))
            y = int(delta/2 + ty*delta)
        else:
            x = 0
            y = self.size/2
        
        if len(self.compress_map) > 0:
            return (x,self.compress_map[y])
        else:
            return (x,y)
    
    def get(self,index):
        try:
            (x,y) = self.index_to_xy(index)
            return self.array[y][x]
        except:
            return None

    def get_xy(self,x,y):
        return self.array[y][x]

    def set_xy(self,x,y,value):
        self.array[y][x] = value

    def dimensions(self):
        return (len(self.array),self.max_x+1)

    def compress(self):
        new_map = {}
        new_array = []
        old_y = 0
        new_y = 0

        for i in self.array:
            if i and self.not_blank(i):
                self.compress_map[old_y] = new_y
                new_array.append(i)
                x = 0
                for entry in i:
                    if entry:
                        new_map[entry] = (new_y,x)
                    x =+ 1
                new_y += 1
            old_y += 1
        self.array = new_array
        self.map = new_map
        self.ad = (new_y,self.ad[1])

    def display(self):
        index = 0
        for i in self.array:
            print "%04d" % index,i
            index=index+1

    def not_blank(self,line):
        for i in line:
            if i and type(i) == tuple:
                return 1
        return 0

#------------------------------------------------------------------------
#
# AncestorChart
#
#------------------------------------------------------------------------
class AncestorChart(Report.Report):

    def __init__(self,database,person,options_class):
        """
        Creates AncestorChart object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        person          - currently selected person
        options_class   - instance of the Options class for this report

        This report needs the following parameters (class variables)
        that come in the options class.
        
        gen       - Maximum number of generations to include.
        pagebbg   - Whether to include page breaks between generations.
        dispf     - Display format for the output box.
        singlep   - Whether to scale to fit on a single page.
        compress  - Whether to compress chart.
        title     - Title of the report displayed on top.
        """
        Report.Report.__init__(self,database,person,options_class)

        (self.max_generations,self.pgbrk) \
                        = options_class.get_report_generations()
        self.display = options_class.handler.options_dict['dispf']
        self.force_fit = options_class.handler.options_dict['singlep']
        self.compress = options_class.handler.options_dict['compress']
        self.title = options_class.handler.options_dict['title'].strip()

        self.map = {}
        self.text = {}

        self.box_width = 0
        self.box_height = 0
        self.lines = 0

        self.font = self.doc.style_list["AC2-Normal"].get_font()
        self.tfont = self.doc.style_list["AC2-Title"].get_font()

        self.apply_filter(self.start_person.get_handle(),1)

        keys = self.map.keys()
        keys.sort()
        max_key = log2(keys[-1])

        self.genchart = GenChart(max_key+1)
        for key in self.map.keys():
            self.genchart.set(key,self.map[key])
        self.calc()

    def apply_filter(self,person_handle,index):
        """traverse the ancestors recursively until either the end
        of a line is found, or until we reach the maximum number of 
        generations that we want to deal with"""

        if (not person_handle) or (index >= 2**self.max_generations):
            return
        self.map[index] = person_handle

        self.text[index] = []

        em = self.doc.string_width(self.font,"m")

        subst = SubstKeywords(self.database,person_handle)
        self.text[index] = subst.replace_and_clean(self.display)

        for line in self.text[index]:
            this_box_width = self.doc.string_width(self.font,line) + 2*em
            self.box_width = max(self.box_width,this_box_width)

        self.lines = max(self.lines,len(self.text[index]))    

        person = self.database.get_person_from_handle(person_handle)
        family_handle = person.get_main_parents_family_handle()
        if family_handle:
            family = self.database.get_family_from_handle(family_handle)
            self.apply_filter(family.get_father_handle(),index*2)
            self.apply_filter(family.get_mother_handle(),(index*2)+1)

    def write_report(self):

        generation = 1
        done = 0
        page = 1
        (maxy,maxx) = self.genchart.dimensions()
        maxh = int(self.uh/self.box_height)
        
        if self.force_fit:
            self.print_page(0,maxx,0,maxy,0,0)
        else:
            starty = 0
            coly = 0
            while starty < maxy-1:
                startx = 0
                colx = 0
                while startx < maxx-1:
                    stopx = min(maxx,startx+self.generations_per_page)
                    stopy = min(maxy,starty+maxh)
                    self.print_page(startx,stopx,starty,stopy,colx,coly)
                    colx += 1
                    startx += self.generations_per_page
                coly += 1
                starty += maxh
            
    def calc(self):
        """
        calc - calculate the maximum width that a box needs to be. From
        that and the page dimensions, calculate the proper place to put
        the elements on a page.
        """

        self.add_lines()
        if self.compress:
            self.genchart.compress()

        self.box_pad_pts = 10
        if self.title and self.force_fit:
            self.offset = pt2cm(1.25* self.tfont.get_size())
        else:
            self.offset = 0
        self.uh = self.doc.get_usable_height() - self.offset
        uw = self.doc.get_usable_width()-pt2cm(self.box_pad_pts)

        calc_width = pt2cm(self.box_width + self.box_pad_pts) + 0.2 
        self.box_width = pt2cm(self.box_width)
        self.box_height = self.lines*pt2cm(1.25*self.font.get_size())

        self.scale = 1
        
        if self.force_fit:
            (maxy,maxx) = self.genchart.dimensions()

            bw = calc_width/(uw/maxx)
            bh = self.box_height/(self.uh/maxy)
            
            self.scale = max(bw,bh)
            self.box_width = self.box_width/self.scale
            self.box_height = self.box_height/self.scale
            self.box_pad_pts = self.box_pad_pts/self.scale

        maxh = int(self.uh/self.box_height)
        maxw = int(uw/calc_width) 

        if log2(maxh) < maxw:
            self.generations_per_page = int(log2(maxh))
        else:
            self.generations_per_page = maxw
        acty = 2**self.generations_per_page

        # build array of x indices

        xstart = 0
        ystart = self.offset-self.box_height/2.0
        self.delta = pt2cm(self.box_pad_pts) + self.box_width + 0.2
        if not self.force_fit:
            calc_width = self.box_width + 0.2 + pt2cm(self.box_pad_pts)
            remain = self.doc.get_usable_width() - ((self.generations_per_page)*calc_width)
            self.delta += remain/(self.generations_per_page)

        self.font.set_size(self.font.get_size()/self.scale)
        
        g = BaseDoc.GraphicsStyle()
        g.set_height(self.box_height)
        g.set_width(self.box_width)
        g.set_paragraph_style("AC2-Normal")
        g.set_shadow(1,0.2/self.scale)
        g.set_fill_color((255,255,255))
        self.doc.add_draw_style("AC2-box",g)

        g = BaseDoc.GraphicsStyle()
        g.set_paragraph_style("AC2-Title")
        g.set_color((255,255,255))
        g.set_fill_color((255,255,255))
        g.set_line_width(0)
        g.set_width(self.doc.get_usable_width())
        self.doc.add_draw_style("AC2-title",g)

        g = BaseDoc.GraphicsStyle()
        self.doc.add_draw_style("AC2-line",g)

    def print_page(self,startx,stopx,starty,stopy,colx,coly):

        self.doc.start_page()
        if self.title and self.force_fit:
            self.doc.center_text('AC2-title',self.title,self.doc.get_usable_width()/2,0)
        phys_y = 0
        for y in range(starty,stopy):
            phys_x = 0
            for x in range(startx,stopx):
                value = self.genchart.get_xy(x,y)
                if value:
                    if type(value) == tuple:
                        (person,index) = value
                        text = '\n'.join(self.text[index])
                        self.doc.draw_box("AC2-box",text,phys_x*self.delta,
                                          phys_y*self.box_height+self.offset)
                    elif value == 2:
                        self.doc.draw_line("AC2-line",
                                           phys_x*self.delta+self.box_width*0.5,
                                           phys_y*self.box_height+self.offset,
                                           phys_x*self.delta+self.box_width*0.5,
                                           (phys_y+1)*self.box_height+self.offset)
                    elif value == 1:
                        x1 = phys_x*self.delta+self.box_width*0.5
                        x2 = (phys_x+1)*self.delta
                        y1 = phys_y*self.box_height+self.offset+self.box_height/2
                        y2 = (phys_y+1)*self.box_height+self.offset
                        self.doc.draw_line("AC2-line",x1,y1,x1,y2)
                        self.doc.draw_line("AC2-line",x1,y1,x2,y1)
                    elif value == 3:
                        x1 = phys_x*self.delta+self.box_width*0.5
                        x2 = (phys_x+1)*self.delta
                        y1 = (phys_y)*self.box_height+self.offset+self.box_height/2
                        y2 = (phys_y)*self.box_height+self.offset
                        self.doc.draw_line("AC2-line",x1,y1,x1,y2)
                        self.doc.draw_line("AC2-line",x1,y1,x2,y1)
                        
                phys_x +=1
            phys_y += 1
                    
        if not self.force_fit:
            self.doc.draw_text('AC2-box',
                               '(%d,%d)' % (colx+1,coly+1),
                               self.doc.get_usable_width()+0.5,
                               self.doc.get_usable_height()+0.75)
        self.doc.end_page()

    def add_lines(self):

        (my,mx) = self.genchart.dimensions()
        
        for y in range(0,my):
            for x in range(0,mx):
                value = self.genchart.get_xy(x,y)
                if not value:
                    continue
                if type(value) == tuple:
                    (person,index) = value
                    if self.genchart.get(index*2):
                        (px,py) = self.genchart.index_to_xy(index*2)
                        self.genchart.set_xy(x,py,1)
                        for ty in range(py+1,y):
                            self.genchart.set_xy(x,ty,2)
                    if self.genchart.get(index*2+1):
                        (px,py) = self.genchart.index_to_xy(index*2+1)
                        self.genchart.set_xy(px-1,py,3)
                        for ty in range(y+1,py):
                            self.genchart.set_xy(x,ty,2)
                    
#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
class AncestorChartOptions(ReportOptions.ReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self,name,person_id=None):
        ReportOptions.ReportOptions.__init__(self,name,person_id)

    def set_new_options(self):
        # Options specific for this report
        self.options_dict = {
            'singlep'   : 1,
            'compress'  : 1,
            'title'     : '',
        }
        self.options_help = {
            'singlep'   : ("=0/1","Whether to scale to fit on a single page.",
                            ["Do not scale to fit","Scale to fit"],
                            True),
            'compress'  : ("=0/1","Whether to compress chart.",
                            ["Do not compress chart","Compress chart"],
                            True),
            'title'     : ("=str","Title string for the report",
                            "Whatever String You Wish"),
        }

    def enable_options(self):
        # Semi-common options that should be enabled for this report
        self.enable_dict = {
            'gen'       : 10,
            'pagebbg'   : 0,
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

        self.scale = gtk.CheckButton(_('Sc_ale to fit on a single page'))
        self.scale.set_active(self.options_dict['singlep'])
        dialog.add_option('',self.scale)

        self.compress = gtk.CheckButton(_('Co_mpress chart'))
        self.compress.set_active(self.options_dict['compress'])
        dialog.add_option('',self.compress)

        self.title_box = gtk.Entry()
        if self.options_dict['title']:
            self.title_box.set_text(self.options_dict['title'])
        else:
            self.title_box.set_text(dialog.get_header(dialog.person.get_primary_name().get_name()))
        dialog.add_option(_('Title'),self.title_box)

    def parse_user_options(self,dialog):
        """
        Parses the custom options that we have added.
        """
        self.options_dict['singlep'] = int(self.scale.get_active ())
        self.options_dict['compress'] = int(self.compress.get_active ())
        self.options_dict['title'] = unicode(self.title_box.get_text()).strip()

    def make_default_style(self,default_style):
        """Make the default output style for the Ancestor Chart report."""
        f = BaseDoc.FontStyle()
        f.set_size(9)
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        p = BaseDoc.ParagraphStyle()
        p.set_font(f)
        p.set_description(_('The basic style used for the text display.'))
        default_style.add_style("AC2-Normal",p)

        f = BaseDoc.FontStyle()
        f.set_size(16)
        f.set_type_face(BaseDoc.FONT_SANS_SERIF)
        p = BaseDoc.ParagraphStyle()
        p.set_font(f)
        p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
        p.set_description(_('The basic style used for the title display.'))
        default_style.add_style("AC2-Title",p)

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
register_report(
    name = 'ancestor_chart2',
    category = Report.CATEGORY_DRAW,
    report_class = AncestorChart,
    options_class = AncestorChartOptions,
    modes = Report.MODE_GUI | Report.MODE_BKI | Report.MODE_CLI,
    translated_name = _("Ancestor Graph"),
    status = _("Stable"),
    author_name = "Donald N. Allingham",
    author_email = "don@gramps-project.org",
    description = _("Produces a graphical ancestral tree graph"),
    )
