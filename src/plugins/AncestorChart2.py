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

"Graphical Reports/Ancestor Chart"

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import os
import string
import math

import gtk

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------
import GrampsCfg
import BaseDoc
import Report
import Errors
import FontScale
from QuestionDialog import ErrorDialog
from SubstKeywords import SubstKeywords
from gettext import gettext as _

_BORN = _('b.')
_DIED = _('d.')

def log2(val):
    return int(math.log10(val)/math.log10(2))

#------------------------------------------------------------------------
#
# pt2cm - convert points to centimeters
#
#------------------------------------------------------------------------
def pt2cm(pt):
    return (float(pt)/72.0)*(254.0/100.0)

#------------------------------------------------------------------------
#
# cm2pt - convert centimeters to points
#
#------------------------------------------------------------------------
def cm2pt(cm):
    return (float(cm)/2.54)*72

#------------------------------------------------------------------------
#
# Layout class
#
#------------------------------------------------------------------------
class GenChart :

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
            if i:
                return 1
        return 0

#------------------------------------------------------------------------
#
# AncestorChart
#
#------------------------------------------------------------------------
class AncestorChart:

    def __init__(self,database,person,max,display,doc,output,scale,
                 title,newpage=0):
        self.doc = doc
        self.title = title.strip()
        self.doc.creator(database.getResearcher().getName())
        self.map = {}
        self.text = {}
        self.start = person
        self.max_generations = max
        self.output = output
	self.box_width = 0
	self.box_height = 0
        self.lines = 0
        self.display = display
        self.newpage = newpage
        self.force_fit = scale
        if output:
            self.doc.open(output)
        self.standalone = output
        self.font = self.doc.style_list["AC-Normal"].get_font()
        self.tfont = self.doc.style_list["AC-Title"].get_font()

        self.filter(self.start,1)

        keys = self.map.keys()
        keys.sort()
        max_key = log2(keys[-1])

        self.genchart = GenChart(max_key+1)
        for key in self.map.keys():
            self.genchart.set(key,self.map[key])
	self.calc()

    def filter(self,person,index):
        """traverse the ancestors recursively until either the end
        of a line is found, or until we reach the maximum number of 
        generations that we want to deal with"""

        if person == None or index >= 2**self.max_generations:
            return
        self.map[index] = person

	self.text[index] = []

        subst = SubstKeywords(person)
        
        for line in self.display:
            self.text[index].append(subst.replace(line))

	for line in self.text[index]:
	    self.box_width = max(self.box_width,FontScale.string_width(self.font,line))

	self.lines = max(self.lines,len(self.text[index]))    

        family = person.getMainParents()
        if family:
            self.filter(family.getFather(),index*2)
            self.filter(family.getMother(),(index*2)+1)

    def write_report(self):

        if self.newpage:
            self.doc.page_break()

        generation = 1
        done = 0
        page = 1
        (maxy,maxx) = self.genchart.dimensions()
        maxh = int(self.uh/self.box_height)
        
        if self.force_fit:
            self.print_page(0,maxx,0,maxy)
        else:
            starty = 0
            while starty < maxy-1:
                startx = 0
                while startx < maxx-1:
                    stopx = min(maxx,startx+self.generations_per_page)
                    stopy = min(maxy,starty+maxh)
                    self.print_page(startx,stopx,starty,stopy)
                    startx += self.generations_per_page
                starty += maxh-1
        if self.standalone:
            self.doc.close()
            
    def calc(self):
        """
        calc - calculate the maximum width that a box needs to be. From
        that and the page dimensions, calculate the proper place to put
        the elements on a page.
        """

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
        g.set_paragraph_style("AC-Normal")
        g.set_shadow(1,0.2/self.scale)
        g.set_fill_color((255,255,255))
        self.doc.add_draw_style("box",g)

        g = BaseDoc.GraphicsStyle()
        g.set_paragraph_style("AC-Title")
        g.set_color((255,255,255))
        g.set_fill_color((255,255,255))
        g.set_line_width(0)
        g.set_width(self.doc.get_usable_width())
        self.doc.add_draw_style("title",g)

        g = BaseDoc.GraphicsStyle()
        self.doc.add_draw_style("line",g)
        if self.standalone:
            self.doc.init()

    def get_numbers(self,start,index,vals):
        if index > 4:
            return
        if self.map.has_key(start):
            vals.append(start)
        self.get_numbers(start*2,index+1,vals)
        self.get_numbers((start*2)+1,index+1,vals)

    def print_page(self,startx,stopx,starty,stopy):

        self.doc.start_page()
        if self.title and self.force_fit:
            self.doc.center_text('title',self.title,self.doc.get_usable_width()/2,0)
        phys_y = 0
        for y in range(starty,stopy):
            phys_x = 0
            for x in range(startx,stopx):
                value = self.genchart.get_xy(x,y)
                if value:
                    (person,index) = value
                    text = string.join(self.text[index],"\n")
                    self.doc.draw_box("box",text,phys_x*self.delta,phys_y*self.box_height+self.offset)
                    if self.genchart.get(index*2):
                        (px,py) = self.genchart.index_to_xy(index*2)
                        x2 = min(self.doc.get_usable_width(),(px-startx)*self.delta)
                        x1 = (x-startx)*self.delta+(0.5 * self.box_width)
                        y2 = self.box_height * (py-starty) + 0.5*self.box_height + self.offset
                        y1 = self.box_height * (y-starty) + self.offset
                        self.doc.draw_line("line",x1,y1,x1,y2)
                        self.doc.draw_line("line",x1,y2,x2,y2)
                    if self.genchart.get(index*2+1):
                        (px,py) = self.genchart.index_to_xy(index*2+1)
                        x2 = min(self.doc.get_usable_width(),(px-startx)*self.delta)
                        x1 = (x-startx)*self.delta+(0.5 * self.box_width)
                        y2 = self.box_height * (py-starty) + 0.5*self.box_height + self.offset
                        y1 = self.box_height * (y-starty+1) + self.offset
                        self.doc.draw_line("line",x1,y1,x1,y2)
                        self.doc.draw_line("line",x1,y2,x2,y2)
                phys_x +=1
            phys_y += 1
                    
        self.doc.end_page()

#------------------------------------------------------------------------
#
# 
#
#------------------------------------------------------------------------
def _make_default_style(default_style):
    """Make the default output style for the Ancestor Chart report."""
    f = BaseDoc.FontStyle()
    f.set_size(9)
    f.set_type_face(BaseDoc.FONT_SANS_SERIF)
    p = BaseDoc.ParagraphStyle()
    p.set_font(f)
    p.set_description(_('The basic style used for the text display.'))
    default_style.add_style("AC-Normal",p)

    f = BaseDoc.FontStyle()
    f.set_size(16)
    f.set_type_face(BaseDoc.FONT_SANS_SERIF)
    p = BaseDoc.ParagraphStyle()
    p.set_font(f)
    p.set_alignment(BaseDoc.PARA_ALIGN_CENTER)
    p.set_description(_('The basic style used for the title display.'))
    default_style.add_style("AC-Title",p)

#------------------------------------------------------------------------
#
# AncestorChartDialog
#
#------------------------------------------------------------------------
class AncestorChartDialog(Report.DrawReportDialog):

    report_options = {}
    
    def __init__(self,database,person):
        Report.DrawReportDialog.__init__(self,database,person,self.report_options)

    def add_user_options(self):
        self.title=gtk.Entry()
        self.title.set_text(self.get_header(self.person.getPrimaryName().getName()))
        self.title.show()
        self.add_option(_('Title'),self.title)
        self.scale = gtk.CheckButton(_('Scale to fit on a single page'))
        self.scale.set_active(1)
        self.scale.show()
        self.add_option('',self.scale)

    def get_title(self):
        """The window title for this dialog"""
        return "%s - %s - GRAMPS" % (_("Ancestor Chart"),_("Graphical Reports"))

    def get_header(self, name):
        """The header line at the top of the dialog contents."""
        return _("Ancestor Chart for %s") % name

    def get_target_browser_title(self):
        """The title of the window created when the 'browse' button is
        clicked in the 'Save As' frame."""
        return _("Save Ancestor Chart")

    def get_stylesheet_savefile(self):
        """Where to save user defined styles for this report."""
        return _style_file
    
    def get_report_generations(self):
        """Default to 10 generations, no page breaks."""
        return (10, 0)
    
    def get_report_extra_textbox_info(self):
        """Label the textbox and provide the default contents."""
        return (_("Display Format"), "$n\n%s $b\n%s $d" % (_BORN,_DIED),
                _("Allows you to customize the data in the boxes in the report"))

    def make_default_style(self):
        _make_default_style(self.default_style)

    def make_report(self):
        """Create the object that will produce the Ancestor Chart.
        All user dialog has already been handled and the output file
        opened."""

        try:
            MyReport = AncestorChart(self.db, self.person, 
                                     self.max_gen, self.report_text,
                                     self.doc,self.target_path,
                                     self.scale.get_active(),
                                     self.title.get_text()
                                     )
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
# entry point
#
#------------------------------------------------------------------------
def report(database,person):
    AncestorChartDialog(database,person)

#------------------------------------------------------------------------
#
# Set up sane defaults for the book_item
#
#------------------------------------------------------------------------
_style_file = "ancestor_chart.xml"
_style_name = "default" 

_person_id = ""
_max_gen = 10
_disp_format = [ "$n", "%s $b" % _BORN, "%s $d" % _DIED ]
_options = ( _person_id, _max_gen, _disp_format )

#------------------------------------------------------------------------
#
# Book Item Options dialog
#
#------------------------------------------------------------------------
class AncestorChartBareDialog(Report.BareReportDialog):

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
        self.disp_format = string.join(self.options[2],'\n')
        self.new_person = None

        self.generations_spinbox.set_value(self.max_gen)
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
        return "%s - GRAMPS Book" % (_("Ancestor Chart"))

    def get_header(self, name):
        """The header line at the top of the dialog contents"""
        return _("Ancestor Chart for GRAMPS Book") 

    def get_stylesheet_savefile(self):
        """Where to save styles for this report."""
        return _style_file
    
    def get_report_generations(self):
        """Default to 10 generations, no page breaks."""
        return (10, 0)
    
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
        self.options = ( self.person.getId(), self.max_gen, self.report_text )
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
            person = database.getPerson(options[0])
        max_gen = int(options[1])
        disp_format = options[2]
        return AncestorChart(database, person, max_gen,
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
def get_xpm_image():
    return [
        "48 48 85 1",
        " 	c None",
        ".	c #887D6C",
        "+	c #8C8A87",
        "@	c #787775",
        "#	c #766D5F",
        "$	c #67655F",
        "%	c #5E5A54",
        "&	c #55524C",
        "*	c #BBBAB8",
        "=	c #B7AFA2",
        "-	c #A9A5A0",
        ";	c #99948A",
        ">	c #FAFAFA",
        ",	c #F8F6F2",
        "'	c #F6F2EC",
        ")	c #E6E5E5",
        "!	c #D2CCBF",
        "~	c #C7C6C3",
        "{	c #413F3F",
        "]	c #DCD9D4",
        "^	c #322E2B",
        "/	c #4F4E4C",
        "(	c #908F8D",
        "_	c #989897",
        ":	c #8A8986",
        "<	c #898885",
        "[	c #F5EEE5",
        "}	c #F5F5F5",
        "|	c #979695",
        "1	c #888784",
        "2	c #8B8A87",
        "3	c #1A1A1A",
        "4	c #858582",
        "5	c #949390",
        "6	c #858480",
        "7	c #92918E",
        "8	c #8F8E8B",
        "9	c #8E8D8A",
        "0	c #797773",
        "a	c #7B7975",
        "b	c #81807C",
        "c	c #817F7C",
        "d	c #989796",
        "e	c #807E7B",
        "f	c #8C8B88",
        "g	c #E3CAA5",
        "h	c #F2EADF",
        "i	c #DDCDB4",
        "j	c #8E8E8B",
        "k	c #888785",
        "l	c #EFE4D2",
        "m	c #969694",
        "n	c #9F9F9D",
        "o	c #E6D4B7",
        "p	c #A5967E",
        "q	c #8A8987",
        "r	c #EBDCC4",
        "s	c #878683",
        "t	c #9B9995",
        "u	c #9A9892",
        "v	c #807F7B",
        "w	c #7E7C79",
        "x	c #8E8C88",
        "y	c #8F8E8C",
        "z	c #8D8B88",
        "A	c #B59871",
        "B	c #878581",
        "C	c #8E8B87",
        "D	c #848480",
        "E	c #898785",
        "F	c #8A8886",
        "G	c #7D7B77",
        "H	c #8D8C89",
        "I	c #8B8A86",
        "J	c #918F8B",
        "K	c #989795",
        "L	c #BBA382",
        "M	c #8D8B86",
        "N	c #868480",
        "O	c #8E8C87",
        "P	c #8E8B86",
        "Q	c #8A8985",
        "R	c #807F7A",
        "S	c #8D8A84",
        "T	c #898884",
        "                                                ",
        "                                                ",
        "             .+....@@#####$$$%$%&$@             ",
        "             .**************=*-;+%%@            ",
        "             .*>>,>>>>>>,>>>>')!*..;&           ",
        "             .*>>>>>>>>>>>>>>>,)!=@~;{          ",
        "             .*,>>>>>>>>>>>>>>>,]]%)~+^         ",
        "             .*>>>>>>>>>>>>>>>>>))/>)~+^        ",
        "             .*>>>>>>>>>>>>>>>>>(_/>>)~+^       ",
        "             .*>>>>>>>>>>>>>>>>>:>/)>>)~+{      ",
        "             @*>>>>>>>>>>>>>>>>><>/]'>>)~;&     ",
        "             @*>>>>>>>>>>>>>>>>>:>/~][>>)~;$    ",
        "             #*>>>>>>>>>}}|1<<2>:>/33^{{%$@$@   ",
        "             .*>>>>>>>>>4:<<<<<56>)~*-;+@$%{$   ",
        "             #*>>>>>>>>><>|<1<7>8>>)!~=-;+@&{   ",
        "             #*>>>>>>>>><>>>>>>>9>>,]!~*-;+${   ",
        "             #*>>>>>>>>><>>>>>>>8>>,))~~*-;@^   ",
        "             #*>>>>>>>>><>>>>>>>:>(000a!~*-@^   ",
        "             #*>>>>>>>>>1>>>>>>>b2<<<1c]~~*.^   ",
        "             #*>>>>>>>>><>>>>>>>,>de<<f]g~*+^   ",
        "             #*>>>>>>>>><>>>>>>,,,''[h]]ii~+^   ",
        "             $*>>jkkkkj><>>>>>,>'''[[hl]]ig;^   ",
        "             $*>>mkkkkjn<>>>>>,,'''h[hl]o!!p^   ",
        "             $*>>jkkkkq><>>>>,'''[)[hhll]i!p^   ",
        "             $*>>>>>>>>><>>>,,'),[hh)llrro!p^   ",
        "             $*>>>>>>>>><>>,,'''h[hhhllrriip^   ",
        "             $*>>>>>>>>><>,'''h[hhlllllrroip^   ",
        "             %*>>>>>>>>><,''''[[hh|<s<2rroip^   ",
        "             %*>>>>>>>>><'''hhh)tu<<v0wrroip^   ",
        "             $*>>>>>>>>,<''['[[hxly<<<zroooA^   ",
        "             %*>>>>>>>,,<'hh)hhlxllrrrrrroiA^   ",
        "             %*>>>>>>,''1[[[[hllxlrlrroooooA^   ",
        "             %*>>>>>,,''<hqk<<BlClrrrrrooooA^   ",
        "             %*>>>>,'''hDEF<<<GHIrrrroooogiA^   ",
        "             %*>>>,,'''h)hJ<1<KrCrrorooooggL^   ",
        "             &*>>,''[[h[[hllllrlCroroooggogA^   ",
        "             &*>,,''[h[hlhllrlrrCroooooggggA^   ",
        "             &=,''[[[[hlhllllrrrMoqkk1NogggL^   ",
        "             &*''''h)hhlllrrrrrrOPQ<ksRggggA^   ",
        "             /=''h[[[h)llrllrrrooo2STE6ggggA^   ",
        "             &=''h)hlhlllrrrrorooooggggggggA^   ",
        "             /=[[[[hhllrrlrroroooogggggg*ggA^   ",
        "             /=hhhllllllrrrroooogogggggggggA^   ",
        "             /=*=======LLLLLLLLLLLLAAAAAAAAA^   ",
        "             ^^^^^^^^^^^^^^^^^^^^^^^^^^3^^3^^   ",
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
    _("Ancestor Chart (Wall Chart)"),
    category=_("Graphical Reports"),
    status=(_("Beta")),
    description=_("Produces a graphical ancestral tree graph"),
    xpm=get_xpm_image(),
    author_name="Donald N. Allingham",
    author_email="dallingham@users.sourceforge.net"
    )

# (name,category,options_dialog,write_book_item,options,style_name,style_file,make_default_style)
register_book_item( 
    _("Ancestor Chart (Wall Chart)"), 
    _("Graphics"),
    AncestorChartBareDialog,
    write_book_item,
    _options,
    _style_name,
    _style_file,
    _make_default_style
    )

