# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2008  Brian G. Matherly 	 
# Copyright (C) 2010       Jakim Friant#
# Copyright (C) 2010       Craig J. Anderson
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

"""Reports/Graphical Reports/Ancestor Tree"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import math
def log2(val):
    """
    Calculate the log base 2 of a value.
    """
    return int(math.log(val, 2))

X_INDEX = log2
    
from gen.ggettext import sgettext as _

#------------------------------------------------------------------------
#
# GRAMPS modules
#
#------------------------------------------------------------------------

#from Errors import ReportError

from gen.plug.menu import BooleanOption
from gen.plug.menu import NumberOption
from gen.plug.menu import StringOption
from gen.plug.menu import EnumeratedListOption
from gen.plug.menu import TextOption
from gen.plug.menu import PersonOption

from gen.plug.report import Report
from gen.plug.report import utils as ReportUtils
from gen.plug.report import MenuReportOptions

from gen.display.name import displayer as name_displayer

PT2CM = ReportUtils.pt2cm
#cm2pt = ReportUtils.cm2pt

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------
_BORN = _('short for born|b.')
_DIED = _('short for died|d.')
_MARR = _('short for married|m.')

from libtreebase import *

#------------------------------------------------------------------------
#
# Box classes
#
#------------------------------------------------------------------------
class AncestorBoxBase(BoxBase):
    """ The base class for the two boxes used in this report """
    
    def __init__(self, boxstr):
        BoxBase.__init__(self)
        self.boxstr = boxstr
    
    def y_index(self, max_gen):
        """ Calculate the column or generation that this person is in. """
        x_level = self.level[0]
        #Calculate which row in the column of people.
        tmp_y = self.level[2] - (2**x_level)
        #Calculate which row in the table (yes table) of people.
        delta = (2**max_gen) // (2**(x_level))
        return int((delta/2) + (tmp_y*delta))

class PersonBox(AncestorBoxBase):
    """
    Calculates information about the box that will print on a page
    """
    def __init__(self, level):
        AncestorBoxBase.__init__(self, "AC2-box")
        self.level = (X_INDEX(level), 0, level)

class FamilyBox(AncestorBoxBase):
    """
    Calculates information about the box that will print on a page
    """
    def __init__(self, level):
        AncestorBoxBase.__init__(self, "AC2-fam-box")
        self.level = (X_INDEX(level)+1, 1, level)
    
    def y_index(self, max_gen):
        """ Calculate the column or generation that this person is in. """
        x_level = self.level[0] - 1
        #Calculate which row in the column of people.
        tmp_y = self.level[2] - (2**x_level)
        #Calculate which row in the table (yes table) of people.
        delta = (2**max_gen) // (2**(x_level))
        return int((delta/2) + (tmp_y*delta))


#------------------------------------------------------------------------
#
# Titles Class(es)
#
#------------------------------------------------------------------------
class TitleN(TitleBox):
    """No Title class for the report """
    def __init__(self, doc):
        TitleBox.__init__(self, doc, "None")
        
    def calc_title(self, center):
        """Calculate the title of the report"""
        return

class TitleA(TitleBox):
    """Title class for the report """
    def __init__(self, doc):
        TitleBox.__init__(self, doc, "AC2-Title")

    def calc_title(self, center):
        """Calculate the title of the report"""
        name = ""
        if center is not None:
            name = name_displayer.display(center)
        
        # feature request 2356: avoid genitive form
        self.text = _("Ancestor Graph for %s") % name
        self.set_box_height_width()


#------------------------------------------------------------------------
#
# CalcItems           (helper class to calculate text)
# make_ancestor_tree  (main recursive functions)
#
#------------------------------------------------------------------------
class CalcItems(object):
    def __init__(self, dbase):
        __gui = GUIConnect()

        #calculate the printed lines for each box
        #display_repl = [] #Not used in this report
        #str = ""
        #if self.get_val('miss_val'):
        #    str = "_____"
        self.__calc_l =  CalcLines(dbase, [])
        
        self.__blank_father = None
        self.__blank_mother = None

        self.__blank_father = \
            self.__calc_l.calc_lines( None, None, __gui.get_val("father_disp"))
        self.__blank_mother = \
            self.__calc_l.calc_lines( None, None, __gui.get_val("mother_disp"))

        self.center_use = __gui.get_val("center_uses")
        self.disp_father = __gui.get_val("father_disp")
        self.disp_mother = __gui.get_val("mother_disp")
        
        self.disp_marr = [__gui.get_val("marr_disp")]
        self.__blank_marriage = \
            self.__calc_l.calc_lines(None, None, self.disp_marr)

    def calc_person(self, index, indi_handle, fams_handle):
        working_lines = ""
        if index % 2 == 0 or (index == 1 and self.center_use == 0):
            if indi_handle == fams_handle == None:
                working_lines = self.__blank_father
            else:
                working_lines = self.disp_father
        else:
            if indi_handle == fams_handle == None:
                working_lines = self.__blank_mother
            else:
                working_lines = self.disp_mother
        
        if indi_handle == fams_handle == None:
            return working_lines
        else:
            return self.__calc_l.calc_lines(indi_handle, fams_handle,
                                    working_lines)
        
    def calc_marriage(self, indi_handle, fams_handle):
        if indi_handle == fams_handle == None:
            return self.__blank_marriage
        else:
            return self.__calc_l.calc_lines(indi_handle, fams_handle,
                                self.disp_marr)


class MakeAncestorTree(object):
    """
    The main procedure to use recursion to make the tree based off of a person.
    order of people inserted into Persons is important.
    makes sure that order is done correctly.
    """
    def __init__(self, dbase, canvas, max_gen, inc_marr, fill_out):
        self.database = dbase
        self.canvas = canvas
        self.inlc_marr = inc_marr
        self.max_generations = max_gen
        self.fill_out = fill_out
        
        self.calc_items = CalcItems(self.database)
        
    def add_person_box(self, index, indi_handle, fams_handle):
        """ Makes a person box and add that person into the Canvas. """
        
        myself = PersonBox(index)
        
        myself.text = self.calc_items.calc_person(
                            index, indi_handle, fams_handle)

        self.canvas.add_box(myself)

        return myself
    
    def add_marriage_box(self, index, indi_handle, fams_handle):
        """ Makes a marriage box and add that person into the Canvas. """
        
        myself = FamilyBox(index)

        #calculate the text.
        myself.text = self.calc_items.calc_marriage(indi_handle, fams_handle)

        self.canvas.add_box(myself)
    
    def iterate(self, person_handle, index):
        """ Fills out the Ancestor tree as desired/needed.
            this is an iterative approach.  
        """
        if self.max_generations < 1:
            return

        person = self.database.get_person_from_handle(person_handle)
        if not person:
            return self.__fill(index, 
                      min(self.fill_out, self.max_generations)
                      )

        if self.max_generations == 1:
            return self.add_person_box(index, person_handle, None)

        ###########################
        #list of boxes
        #for each generation (self.max_generations)
        __boxes = [None] * self.max_generations
        __index = [index]

        __fams = [None] * self.max_generations
        __pers = [None] * self.max_generations

        ###########################
        #Helper functions:
        def _get_family(generation):
            person = self.database.get_person_from_handle(__pers[generation-1])
            __fams[generation] = person.get_main_parents_family_handle()

        def _get_person(generation):
            if not __fams[generation]:
                __pers[generation] = None
                return
            family = self.database.get_family_from_handle(__fams[generation])
            __pers[generation] = \
                    family.get_father_handle() \
                    if __index[generation] % 2 == 0 else \
                    family.get_mother_handle()

        ###########################
        #Prime the pump
        cur_gen = 1 #zero based!
        __pers[0] = person_handle
        #__fams[0] = person.get_main_parents_family_handle()
        #Cur_gen is the current Generation that we are working with
        #use a bottom up iterative approach
        while cur_gen > 0:
            ###########################
            #Step 1.  this level is blank.  add our father
            if len(__index) == cur_gen:
                __index.append(__index[cur_gen-1]*2)
                #we will be adding a father here

                #Set __fams[cur_gen] and __pers[cur_gen]
                _get_family(cur_gen)
                _get_person(cur_gen)
                
                if not __pers[cur_gen]:
                    #Fill in our father
                    if self.fill_out:
                        __boxes[cur_gen] = self.__fill(__index[cur_gen],
                                min(self.fill_out, self.max_generations -
                                    cur_gen))
                    else:
                        __boxes[cur_gen] = None
                elif cur_gen < self.max_generations-1:
                    #But first, go to this father first if we can
                    cur_gen += 1
                else:
                    #found our father. add him
                    __boxes[cur_gen] = self.add_person_box(__index[cur_gen], 
                            __pers[cur_gen], __fams[cur_gen])
                    
            ###########################
            #Step 1.5.  Dad has already been made.
            elif __index[cur_gen] % 2 == 0:
                
                ###########################
                #Step 2.  add our kid
                __boxes[cur_gen-1] = self.add_person_box(
                                        __index[cur_gen-1],
                                        __pers[cur_gen-1], __fams[cur_gen-1])
                
                ###########################
                #Step 2.6.  line part 1
                if __boxes[cur_gen]:
                    __boxes[cur_gen-1].line_to = LineBase(__boxes[cur_gen-1])
                    __boxes[cur_gen-1].line_to.add_to(__boxes[cur_gen])
                
                ###########################
                #Step 2.3.  add our marriage
                if self.inlc_marr:
                    if __fams[cur_gen]:
                        self.add_marriage_box(__index[cur_gen-1],
                                              __pers[cur_gen], __fams[cur_gen])
                    elif self.fill_out:
                        self.add_marriage_box(__index[cur_gen-1], None, None)

                #Set __fams[cur_gen] and __pers[cur_gen]
                #make sure there is a NEW int.
                __index.pop()
                #not a reference that will clobber dads (other peoples) info
                __index.append((__index[cur_gen-1] *2) +1)

                _get_person(cur_gen)
                
                if not __pers[cur_gen]:
                    #Fill in our father
                    __boxes[cur_gen] = self.__fill(__index[cur_gen],
                            min(self.fill_out, self.max_generations - cur_gen))
                elif cur_gen < self.max_generations-1:
                    cur_gen += 1
                else:
                    ###########################
                    #Step 3.  Now we can make Mom
                    __boxes[cur_gen] = self.add_person_box( __index[cur_gen], 
                            __pers[cur_gen], __fams[cur_gen])

            
            ###########################
            #Step 4.  Father and Mother are done but only 1/2 line
            else:
                if cur_gen > 0:
                    ###########################
                    #Step 2.6.  line part 2
                    if __boxes[cur_gen]:
                        if not __boxes[cur_gen-1].line_to:
                            __boxes[cur_gen-1].line_to = \
                                LineBase(__boxes[cur_gen-1])
                        __boxes[cur_gen-1].line_to.add_to(__boxes[cur_gen])
                
                __index.pop()
                cur_gen -= 1

        return __boxes[0]
    
    def __fill(self, index, max_fill):
        """ Fills out the Ancestor tree as desired/needed.
            this is an iterative approach.  
        """
        if max_fill < 1:
            return

        if max_fill == 1:
            return self.add_person_box(index, None, None)

        ###########################
        #list of boxes
        #for each generation (max_fill)
        __boxes = [None] * max_fill
        __index = [index]

        ###########################
        #Prime the pump
        cur_gen = 1 #zero based!
        #Cur_gen is the current Generation that we are working with
        #use a bottom up iterative approach
        while cur_gen > 0:
            ###########################
            #Step 1.  this level is blank.  add our father
            #if __INFO[cur_gen][__index] == 0:
            if len(__index) == cur_gen:
                __index.append(__index[cur_gen-1]*2)
                #we will be adding a father here
                
                if cur_gen < max_fill-1:
                    #But first, go to this father first if we can
                    cur_gen += 1
                else:
                    #found our father. add him
                    __boxes[cur_gen] = self.add_person_box(
                                            __index[cur_gen], None, None)
                    
            ###########################
            #Step 1.5.  Dad has already been made.
            elif __index[cur_gen] % 2 == 0:
                
                ###########################
                #Step 2.  add our kid
                __boxes[cur_gen-1] = self.add_person_box(
                                        __index[cur_gen-1], None, None)
                
                ###########################
                #Step 2.3.  add our marriage
                if self.inlc_marr and cur_gen <= max_fill+1:
                    self.add_marriage_box(__index[cur_gen-1], None, None)

                ###########################
                #Step 2.6.  line part 1
                __boxes[cur_gen-1].line_to = LineBase(__boxes[cur_gen-1])
                __boxes[cur_gen-1].line_to.add_to(__boxes[cur_gen])
                
                #make sure there is a NEW int.
                __index.pop()
                #not a reference that will clobber dads info
                __index.append((__index[cur_gen-1] *2) +1)
                #__index[cur_gen] +=1
                
                if cur_gen < max_fill-1:
                    cur_gen += 1
                else:
                    ###########################
                    #Step 3.  Now we can make Mom
                    __boxes[cur_gen] = self.add_person_box(
                                            __index[cur_gen], None, None)
            
            ###########################
            #Step 4.  Father and Mother are done but only 1/2 line
            else:
                if cur_gen > 0:
                    ###########################
                    #Step 2.6.  line part 2
                    __boxes[cur_gen-1].line_to.add_to(__boxes[cur_gen])
                
                __index.pop()
                cur_gen -= 1

        return __boxes[0]

    def start(self, person_id):
        """ go ahead and make it happen """
        center = self.database.get_person_from_gramps_id(person_id)
        center_h = center.get_handle()

        self.iterate(center_h, 1)

#------------------------------------------------------------------------
#
# Transform Classes
#
#------------------------------------------------------------------------
#------------------------------------------------------------------------
# Class rl_Transform
#------------------------------------------------------------------------
class RLTransform():
    """
    setup all of the boxes on the canvas in for a left/right report 
    """
    def __init__(self, canvas, max_generations, compress_tree):
        self.canvas = canvas
        self.rept_opts = canvas.report_opts
        self.max_generations = max_generations
        self.compress_tree = compress_tree
        self.y_offset = self.rept_opts.littleoffset*2 + self.canvas.title.height
        self.__last_y_level = 0
        self.__y_level = 0
    
    def __next_y(self, box):
        """ boxes are already in top down (.y_cm) form so if we
        set the box in the correct y level depending on compress_tree
        """
        y_index = box.y_index(self.max_generations+1) -1
        
        if self.compress_tree:
            current_y = self.__y_level
            if y_index > self.__last_y_level:
                self.__last_y_level = y_index
                self.__y_level += 1
                current_y = self.__y_level
            return current_y
        else:
            return y_index
    
    def _place(self, box):
        """ put the box in it's correct spot """
        #1. cm_x
        box.x_cm = self.rept_opts.littleoffset
        box.x_cm += (box.level[0] *
                (self.rept_opts.col_width + self.rept_opts.max_box_width))
        #2. cm_y
        box.y_cm = self.__next_y(box) * self.rept_opts.max_box_height
        box.y_cm += self.y_offset
        #if box.height < self.rept_opts.max_box_height:
        #    box.y_cm += ((self.rept_opts.max_box_height - box.height) /2)

    def place(self):
        """ step through boxes so they can be put in the right spot """
        #prime the pump
        self.__last_y_level = \
            self.canvas.boxes[0].y_index(self.max_generations+1) -1
        #go
        for box in self.canvas.boxes:
            self._place(box)


#------------------------------------------------------------------------
#
# class make_report
#
#------------------------------------------------------------------------
class MakeReport():

    def __init__(self, dbase, doc, canvas,
                 font_normal, inlc_marr, compress_tree):

        self.database = dbase
        self.doc = doc
        self.canvas = canvas
        self.font_normal = font_normal
        self.inlc_marr = inlc_marr
        self.compress_tree = compress_tree
        self.mother_ht = self.father_ht = 0
        
        self.max_generations = 0
        
    def get_height_width(self, box):
        """
        obtain width information for each level (x)
        obtain height information for each item
        """

        self.canvas.set_box_height_width(box)
        
        if box.width > self.canvas.report_opts.max_box_width:
            self.canvas.report_opts.max_box_width = box.width #+ box.shadow

        if box.level[2] > 0:
            if box.level[2] % 2 == 0 and box.height > self.father_ht:
                self.father_ht = box.height
            elif box.level[2] % 2 == 1 and box.height > self.mother_ht:
                self.mother_ht = box.height
        
        tmp = log2(box.level[2])
        if tmp > self.max_generations:
            self.max_generations = tmp
            
    def get_generations(self):
        return self.max_generations
    
    def start(self):
        # 1.
        #set the sizes for each box and get the max_generations.
        self.father_ht = 0.0
        self.mother_ht = 0.0
        for box in self.canvas.boxes:
            self.get_height_width(box)
            
        if self.compress_tree and not self.inlc_marr:
            self.canvas.report_opts.max_box_height = \
                        min(self.father_ht, self.mother_ht)
        else:
            self.canvas.report_opts.max_box_height = \
                        max(self.father_ht, self.mother_ht)
            
        #At this point we know everything we need to make the report.
        #Size of each column of people - self.rept_opt.box_width
        #size of each column (or row) of lines - self.rept_opt.col_width
        #size of each row - self.rept_opt.box_height
        #go ahead and set it now.
        for box in self.canvas.boxes:
            box.width = self.canvas.report_opts.max_box_width
        
        # 2.
        #setup the transform class to move around the boxes on the canvas
        transform = RLTransform(self.canvas, 
                                 self.max_generations, self.compress_tree)
        transform.place()


class GUIConnect():
    """ This is a BORG object.  There is ONLY one.
    This give some common routines that EVERYONE can use like
      get the value from a GUI variable
    """
    
    __shared_state = {}
    def __init__(self):  #We are BORG!
        self.__dict__ = self.__shared_state
    
    def set__opts(self, options):
        """ Set only once as we are BORG.  """
        self.__opts = options
        
    def get_val(self, val):
        """ Get a GUI value. """
        value = self.__opts.get_option_by_name(val)
        if value:
            return value.get_value() 
        else:
            False
    
    def title_class(self, doc):
        """  Return a class that holds the proper title based off of the
        GUI options """
        title_type = self.get_val('report_title')
        return TitleA(doc) if title_type else TitleN(doc)

#------------------------------------------------------------------------
#
# AncestorTree
#
#------------------------------------------------------------------------
class AncestorTree(Report):

    def __init__(self, database, options, user):
        """
        Create AncestorTree object that produces the report.
        
        The arguments are:

        database        - the GRAMPS database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        """
        Report.__init__(self, database, options, user)

        self.options = options
        self.database = database
        self._user = user

    def begin_report(self):
        """
        This report needs the following parameters (class variables)
        that come in the options class.
        
        max_generations - Maximum number of generations to include.
        pagebbg      - Whether to include page breaks between generations.
        dispf        - Display format for the output box.
        scale_report - Whether to scale the report to fit the width or all.
        indblank     - Whether to include blank pages.
        compress     - Whether to compress chart.

        We will
        1. a canvas in its full one-page size
        2. a page that we wish to print on
        scale up/down either or both of the above as needed/desired.
        almost all of this should be moved into Canvas!
        """

        database = self.database

        self.connect = GUIConnect()
        self.connect.set__opts(self.options.menu)

        #Set up the canvas that we will print on.
        style_sheet = self.doc.get_style_sheet()
        font_normal = style_sheet.get_paragraph_style("AC2-Normal").get_font()

        #The canvas that we will put our report on and print off of
        self.canvas = Canvas(self.doc, ReportOptions(self.doc, 
                                       font_normal, 'AC2-line'))

        
        self._user.begin_progress(_('Ancestor Tree'), 
                                  _('Making the Tree...'), 4)

        #make the tree onto the canvas
        inlc_marr = self.connect.get_val("inc_marr")
        self.max_generations = self.connect.get_val('maxgen')
        fillout = self.connect.get_val('fill_out')
        tree = MakeAncestorTree(database, self.canvas, self.max_generations,
                           inlc_marr, fillout)
        tree.start(self.connect.get_val('pid'))
        tree = None

        self._user.step_progress()

        #Title
        title = self.connect.title_class(self.doc)
        center = self.database.get_person_from_gramps_id(
                    self.connect.get_val('pid')
                    )
        title.calc_title(center)
        self.canvas.add_title(title)

        #make the report as big as it wants to be.
        compress = self.connect.get_val('compress_tree')
        report = MakeReport(database, self.doc, self.canvas, font_normal,
                             inlc_marr, compress)
        report.start()
        self.max_generations = report.get_generations()  #already know
        report = None

        self._user.step_progress()

        #Note?
        if self.connect.get_val("inc_note"):
            note_box = NoteBox(self.doc, "AC2-fam-box", 
                               self.connect.get_val("note_place"))
            subst = SubstKeywords(self.database, None, None)
            note_box.text = subst.replace_and_clean(
                self.connect.get_val('note_disp'))
            self.canvas.add_note(note_box)

        #Now we have the report in its full size.
        #Do we want to scale the report?
        one_page = self.connect.get_val("resize_page")
        scale_report = self.connect.get_val("scale_tree")

        scale = self.canvas.scale_report(one_page,
                                         scale_report != 0, scale_report == 2)
        if scale != 1:
            self.scale_styles(scale)

    def write_report(self):
        
        one_page = self.connect.get_val("resize_page")
        #scale_report = self.connect.get_val("scale_tree")

        #inlc_marr = self.connect.get_val("inc_marr")
        inc_border = self.connect.get_val('inc_border')
        incblank = self.connect.get_val("inc_blank")
        prnnum = self.connect.get_val("inc_pagenum")

        #####################
        #Setup page information

        colsperpage = self.doc.get_usable_width() 
        colsperpage += self.canvas.report_opts.col_width
        colsperpage = int(colsperpage / (self.canvas.report_opts.max_box_width +
                                       self.canvas.report_opts.col_width))
        colsperpage = colsperpage or 1

        #####################
        #Vars
        if prnnum:
            page_num_box = PageNumberBox(self.doc, 'AC2-box')
        
        self._user.step_progress()
        #####################
        #ok, everyone is now ready to print on the canvas.  Paginate?
        self.canvas.paginate(colsperpage, one_page)
        
        #####################
        #Yeah!!!
        #lets finally make some pages!!!
        #####################
        pages = self.canvas.page_count(incblank)
        self._user.end_progress()
        self._user.begin_progress( _('Ancestor Tree'), 
                                   _('Printing the Tree...'), pages)

        for page in self.canvas.page_iter_gen(incblank):

            self.doc.start_page()
    
            #do we need to print a border?
            if inc_border:
                page.draw_border('AC2-line')
    
            #Do we need to print the page number?
            if prnnum:
                page_num_box.display(page)
    
            #Print the individual people and lines
            page.display()
                    
            self._user.step_progress()
            self.doc.end_page()

        self._user.end_progress()
        

    def scale_styles(self, scale):
        """
        Scale the styles for this report.
        """
        style_sheet = self.doc.get_style_sheet()
        
        from gen.plug.docgen import GraphicsStyle

        graph_style = style_sheet.get_draw_style("AC2-box")
        graph_style.set_shadow(graph_style.get_shadow(),
                               graph_style.get_shadow_space() * scale)
        graph_style.set_line_width(graph_style.get_line_width() * scale)
        style_sheet.add_draw_style("AC2-box", graph_style)

        graph_style = style_sheet.get_draw_style("AC2-fam-box")
        graph_style.set_shadow(graph_style.get_shadow(),
                               graph_style.get_shadow_space() * scale)
        graph_style.set_line_width(graph_style.get_line_width() * scale)
        style_sheet.add_draw_style("AC2-fam-box", graph_style)

        para_style = style_sheet.get_paragraph_style("AC2-Normal")
        font = para_style.get_font()
        font.set_size(font.get_size() * scale)
        para_style.set_font(font)
        style_sheet.add_paragraph_style("AC2-Normal", para_style)
            
        para_style = style_sheet.get_paragraph_style("AC2-Title")
        font = para_style.get_font()
        font.set_size(font.get_size() * scale)
        para_style.set_font(font)
        style_sheet.add_paragraph_style("AC2-Title", para_style)
            
        graph_style = GraphicsStyle()
        width = graph_style.get_line_width()
        width = width * scale
        graph_style.set_line_width(width)
        style_sheet.add_draw_style("AC2-line", graph_style)

        self.doc.set_style_sheet(style_sheet)

#------------------------------------------------------------------------
#
# AncestorTreeOptions
#
#------------------------------------------------------------------------
class AncestorTreeOptions(MenuReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)
        
    def add_menu_options(self, menu):

        ##################
        category_name = _("Tree Options")

        pid = PersonOption(_("Center Person"))
        pid.set_help(_("The center person for the tree"))
        menu.add_option(category_name, "pid", pid)
        
        self.max_gen = NumberOption(_("Generations"), 10, 1, 50)
        self.max_gen.set_help(_("The number of generations to include "
                                "in the tree"))
        menu.add_option(category_name, "maxgen", self.max_gen)
        
        self.fillout = EnumeratedListOption(_("Display unknown\ngenerations"),
                                            0)
        self.fillout.set_help(_("The number of generations of empty "
                                "boxes that will be displayed"))
        menu.add_option(category_name, "fill_out", self.fillout)

        self.max_gen.connect('value-changed', self.__fillout_vals)
        self.__fillout_vals()

        compress = BooleanOption(_('Co_mpress tree'), True)
        compress.set_help(_("Whether to remove any extra blank spaces set "
            "aside for people that are unknown"))
        menu.add_option(category_name, "compress_tree", compress)
        
        #better to 'Show siblings of\nthe center person
        #Spouse_disp = EnumeratedListOption(_("Show spouses of\nthe center "
        #                                     "person"), 0)
        #Spouse_disp.add_item( 0, _("No.  Do not show Spouses"))
        #Spouse_disp.add_item( 1, _("Yes, and use the the Main Display Format"))
        #Spouse_disp.add_item( 2, _("Yes, and use the the Secondary "
        #                           "Display Format"))
        #Spouse_disp.set_help(_("Show spouses of the center person?"))
        #menu.add_option(category_name, "Spouse_disp", Spouse_disp)

        centerDisp = EnumeratedListOption(_("Center person uses\n"
                                        "which format"), 0)
        centerDisp.add_item( 0, _("Use Fathers Display format"))
        centerDisp.add_item( 1, _("Use Mothers display format"))
        centerDisp.set_help(_("Which Display format to use the center person"))
        menu.add_option(category_name, "center_uses", centerDisp)

        ##################
        category_name = _("Display")

        disp = TextOption(_("Father\nDisplay Format"), 
                           ["$n",
                            "%s $b" %_BORN,
                            "{%s $d}" %_DIED] )
        disp.set_help(_("Display format for the fathers box."))
        menu.add_option(category_name, "father_disp", disp)
        
        #Will add when libsubstkeyword supports it.
        #missing = EnumeratedListOption(_("Replace missing\nplaces\\dates \
        #                                 with"), 0)
        #missing.add_item( 0, _("Does not display anything"))
        #missing.add_item( 1, _("Displays '_____'"))
        #missing.set_help(_("What will print when information is not known"))
        #menu.add_option(category_name, "miss_val", missing)

        #category_name = _("Secondary")

        dispMom = TextOption(_("Mother\nDisplay Format"), 
                               ["$n",
                                "%s $b" %_BORN,
                                "%s $m" %_MARR,
                                "{%s $d}" %_DIED]
                            )
        dispMom.set_help(_("Display format for the mothers box."))
        menu.add_option(category_name, "mother_disp", dispMom)

        incmarr = BooleanOption(_('Include Marriage box'), False)
        incmarr.set_help(
            _("Whether to include a separate marital box in the report"))
        menu.add_option(category_name, "inc_marr", incmarr)

        marrdisp = StringOption(_("Marriage\nDisplay Format"), "%s $m" % _MARR) 
        marrdisp.set_help(_("Display format for the marital box."))
        menu.add_option(category_name, "marr_disp", marrdisp)

        ##################
        category_name = _("Size")

        self.scale = EnumeratedListOption(_("Scale tree to fit"), 0)
        self.scale.add_item( 0, _("Do not scale tree"))
        self.scale.add_item( 1, _("Scale tree to fit page width only"))
        self.scale.add_item( 2, _("Scale tree to fit the size of the page"))
        self.scale.set_help(
            _("Whether to scale the tree to fit a specific paper size")
            )
        menu.add_option(category_name, "scale_tree", self.scale)
        self.scale.connect('value-changed', self.__check_blank)

        if "BKI" not in self.name.split(","):
            self.__onepage = BooleanOption(_("Resize Page to Fit Tree size\n"
                "\n"
                "Note: Overrides options in the 'Paper Option' tab"
                ), 
                False)
            self.__onepage.set_help(
                _("Whether to resize the page to fit the size \n"
                "of the tree.  Note:  the page will have a \n"
                "non standard size.\n"
                "\n"
                "With this option selected, the following will happen:\n"
                "\n"
                "With the 'Do not scale tree' option the page\n"
                "  is resized to the height/width of the tree\n"
                "\n"
                "With 'Scale tree to fit page width only' the height of\n"
                "  the page is resized to the height of the tree\n"
                "\n"
                "With 'Scale tree to fit the size of the page' the page\n"
                "  is resized to remove any gap in either height or width"
                ))
            menu.add_option(category_name, "resize_page", self.__onepage)
            self.__onepage.connect('value-changed', self.__check_blank)
        else:
            self.__onepage = None

        ##################
        category_name = _("Include")

        self.title = EnumeratedListOption(_("Report Title"), 0)
        self.title.add_item( 0, _("Do not include a title"))
        self.title.add_item( 1, _("Include Report Title"))
        self.title.set_help(_("Choose a title for the report"))
        menu.add_option(category_name, "report_title", self.title)

        border = BooleanOption(_('Include a border'), False)
        border.set_help(_("Whether to make a border around the report."))
        menu.add_option(category_name, "inc_border", border)

        prnnum = BooleanOption(_('Include Page Numbers'), False)
        prnnum.set_help(_("Whether to print page numbers on each page."))
        menu.add_option(category_name, "inc_pagenum", prnnum)

        self.__blank = BooleanOption(_('Include Blank Pages'), True)
        self.__blank.set_help(_("Whether to include pages that are blank."))
        menu.add_option(category_name, "inc_blank", self.__blank)
        
        self.__check_blank()

        #category_name = _("Notes")

        self.usenote = BooleanOption(_('Include a note'), False)
        self.usenote.set_help(_("Whether to include a note on "
                                "the report."))
        menu.add_option(category_name, "inc_note", self.usenote)
        
        self.notedisp = TextOption(_("Note"), [])
        self.notedisp.set_help(_("Add a note\n\n"
                                 "$T inserts today's date"))
        menu.add_option(category_name, "note_disp", self.notedisp)
        
        locales = NoteType(0, 1)
        self.notelocal = EnumeratedListOption(_("Note Location"), 0)
        for num, text in locales.note_locals():
            self.notelocal.add_item( num, text )
        self.notelocal.set_help(_("Where to place the note."))
        menu.add_option(category_name, "note_place", self.notelocal)

    def __check_blank(self):
        if self.__onepage:
            value = not self.__onepage.get_value()
        else:
            value = True
        off = value and (self.scale.get_value() != 2)
        self.__blank.set_available( off )

    def __fillout_vals(self):
        max_gen = self.max_gen.get_value()
        old_val = self.fillout.get_value()
        item_list = []
        item_list.append([0, _("No generations of empty boxes "
                               "for unknown ancestors") ])
        if max_gen > 1:
            item_list.append([1, _("One Generation of empty boxes "
                                   "for unknown ancestors") ])

        item_list.extend([itr, str(itr) +
                _(" Generations of empty boxes for unknown ancestors")]
                    for itr in range(2, max_gen)
                )
            
        self.fillout.set_items(item_list)
        if old_val+2 > len(item_list):
            self.fillout.set_value(len(item_list) -2)


    def make_default_style(self, default_style):
        """Make the default output style for the Ancestor Tree."""
        
        from gen.plug.docgen import (FontStyle, ParagraphStyle, GraphicsStyle,
                            FONT_SANS_SERIF, PARA_ALIGN_CENTER)

        ## Paragraph Styles:
        font = FontStyle()
        font.set_size(9)
        font.set_type_face(FONT_SANS_SERIF)
        para_style = ParagraphStyle()
        para_style.set_font(font)
        para_style.set_description(_('The basic style used for the '
                                     'text display.'))
        default_style.add_paragraph_style("AC2-Normal", para_style)
        box_shadow = PT2CM(font.get_size()) * .6

        font = FontStyle()
        font.set_size(16)
        font.set_type_face(FONT_SANS_SERIF)
        para_style = ParagraphStyle()
        para_style.set_font(font)
        para_style.set_alignment(PARA_ALIGN_CENTER)
        para_style.set_description(_('The basic style used for the '
                                     'title display.'))
        default_style.add_paragraph_style("AC2-Title", para_style)

        ## Draw styles
        graph_style = GraphicsStyle()
        graph_style.set_paragraph_style("AC2-Normal")
        graph_style.set_shadow(1, box_shadow)  #shadow set by text size
        graph_style.set_fill_color((255, 255, 255))
        default_style.add_draw_style("AC2-box", graph_style)

        graph_style = GraphicsStyle()
        graph_style.set_paragraph_style("AC2-Normal")
        #graph_style.set_shadow(0, PT2CM(9))  #shadow set by text size
        graph_style.set_fill_color((255, 255, 255))
        default_style.add_draw_style("AC2-fam-box", graph_style)

        graph_style = GraphicsStyle()
        graph_style.set_paragraph_style("AC2-Title")
        graph_style.set_color((0, 0, 0))
        graph_style.set_fill_color((255, 255, 255))
        graph_style.set_line_width(0)
        default_style.add_draw_style("AC2-Title", graph_style)

        graph_style = GraphicsStyle()
        default_style.add_draw_style("AC2-line", graph_style)

#=====================================
#But even if you should suffer for what is right, you are blessed.
#"Do not fear what they fear ; do not be frightened."
#Take Courage
#1 Peter 3:14
