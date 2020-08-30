# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2012  Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2014       Paul Franklin
# Copyright (C) 2010-2015  Craig J. Anderson
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Reports/Graphical Reports/Ancestor Tree"""

#------------------------------------------------------------------------
#
# Python modules
#
#------------------------------------------------------------------------

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------

from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.errors import ReportError
from gramps.gen.plug.menu import (TextOption, NumberOption, BooleanOption,
                                  EnumeratedListOption, StringOption,
                                  PersonOption)
from gramps.gen.plug.report import Report, MenuReportOptions, stdoptions
from gramps.gen.plug.docgen import (FontStyle, ParagraphStyle, GraphicsStyle,
                                    FONT_SANS_SERIF, PARA_ALIGN_CENTER)
from gramps.plugins.lib.libtreebase import *
from gramps.plugins.lib.librecurse import AscendPerson
from gramps.gen.proxy import CacheProxyDb
from gramps.gen.display.name import displayer as _nd

PT2CM = utils.pt2cm
#cm2pt = utils.cm2pt

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------
_BORN = _("b.", "birth abbreviation"),
_DIED = _("d.", "death abbreviation"),
_MARR = _("m.", "marriage abbreviation"),

LVL_GEN, LVL_INDX, LVL_Y = range(3)


#------------------------------------------------------------------------
#
# Box classes
#
#------------------------------------------------------------------------
class PersonBox(BoxBase):
    """
    Calculates information about the box that will print on a page
    """
    def __init__(self, level):
        BoxBase.__init__(self)
        self.boxstr = "AC2-box"
        #self.level = (level[0]-1, level[1])
        self.level = level

    def __lt__(self, other):
        return self.level[LVL_Y] < other.level[LVL_Y]


class FamilyBox(BoxBase):
    """
    Calculates information about the box that will print on a page
    """
    def __init__(self, level):
        BoxBase.__init__(self)
        self.boxstr = "AC2-fam-box"
        #self.level = (level[0]-1, level[1])
        self.level = level

    def __lt__(self, other):
        return self.level[LVL_Y] < other.level[LVL_Y]


#------------------------------------------------------------------------
#
# Titles Class(es)
#
#------------------------------------------------------------------------
class TitleN(TitleNoDisplay):
    """No Title class for the report """

    def __init__(self, doc, locale):
        TitleNoDisplay.__init__(self, doc, "AC2-Title-box")
        self._ = locale.translation.sgettext

    def calc_title(self, center):
        """Calculate the title of the report"""
        #we want no text, but need a text for the TOC in a book!
        self.mark_text = self._("Ancestor Graph")
        self.text = ''


class TitleA(TitleBox):
    """Title class for the report """
    def __init__(self, doc, locale, name_displayer):
        self._nd = name_displayer
        TitleBox.__init__(self, doc, "AC2-Title-box")
        self._ = locale.translation.sgettext

    def calc_title(self, center):
        """Calculate the title of the report"""
        name = ""
        if center is not None:
            name = self._nd.display(center)

        # feature request 2356: avoid genitive form
        self.text = self._("Ancestor Graph for %s") % name
        self.set_box_height_width()


#------------------------------------------------------------------------
#
# CalcItems           (helper class to calculate text)
# make_ancestor_tree  (main recursive functions)
#
#------------------------------------------------------------------------
class CalcItems:
    """ A helper class to calculate the default box text
    and text for each person / marriage
    """
    def __init__(self, dbase):
        _gui = GUIConnect()
        self._gui = _gui

        #calculate the printed lines for each box
        #str = ""
        #if self.get_val('miss_val'):
        #    str = "_____"
        display_repl = _gui.get_val("replace_list")
        self.__calc_l = CalcLines(dbase, display_repl, _gui.locale, _gui.n_d)

        self.__blank_father = None
        self.__blank_mother = None

        self.__blank_father = \
            self.__calc_l.calc_lines(None, None, _gui.get_val("father_disp"))
        self.__blank_mother = \
            self.__calc_l.calc_lines(None, None, _gui.get_val("mother_disp"))

        self.center_use = _gui.get_val("center_uses")
        self.disp_father = _gui.get_val("father_disp")
        self.disp_mother = _gui.get_val("mother_disp")

        self.disp_marr = [_gui.get_val("marr_disp")]
        self.__blank_marriage = \
            self.__calc_l.calc_lines(None, None, self.disp_marr)

    def calc_person(self, index, indi_handle, fams_handle):
        working_lines = ""
        if index[1] % 2 == 0 or (index[1] == 1 and self.center_use == 0):
            if indi_handle == fams_handle is None:
                working_lines = self.__calc_l.calc_lines(
                    None, None, self._gui.get_val("father_disp"))
            else:
                working_lines = self.disp_father
        else:
            if indi_handle == fams_handle is None:
                working_lines = self.__calc_l.calc_lines(
                    None, None, self._gui.get_val("mother_disp"))
            else:
                working_lines = self.disp_mother

        if indi_handle == fams_handle is None:
            return working_lines
        else:
            return self.__calc_l.calc_lines(indi_handle, fams_handle,
                                            working_lines)

    def calc_marriage(self, indi_handle, fams_handle):
        if indi_handle == fams_handle is None:
            return self.__blank_marriage
        else:
            return self.__calc_l.calc_lines(indi_handle, fams_handle,
                                            self.disp_marr)


class MakeAncestorTree(AscendPerson):
    """
    The main procedure to use recursion to make the tree based off of a person.
    order of people inserted into Persons is important.
    makes sure that order is done correctly.
    """
    def __init__(self, dbase, canvas):
        _gui = GUIConnect()

        AscendPerson.__init__(self, dbase, _gui.maxgen(), _gui.fill_out())
        self.database = dbase
        self.canvas = canvas
        self.inlc_marr = _gui.inc_marr()
        self.inc_sib = _gui.inc_sib()
        self.compress_tree = _gui.compress_tree()
        self.center_family = None
        self.lines = [None] * (_gui.maxgen() + 1)

        self.max_generation = 0

        self.calc_items = CalcItems(self.database)

    def add_person(self, index, indi_handle, fams_handle):
        """ Makes a person box and add that person into the Canvas. """

        #print str(index) + " add_person " + str(indi_handle)
        myself = PersonBox((index[0] - 1,) + index[1:])

        if index[LVL_GEN] == 1:  # Center Person
            self.center_family = fams_handle

        if index[LVL_GEN] > self.max_generation:
            self.max_generation = index[LVL_GEN]

        myself.text = self.calc_items.calc_person(index,
                                                  indi_handle, fams_handle)
        # myself.text[0] = myself.text[0] + ' ' + repr(index) # for debugging

        if indi_handle is not None:  # None is legal for an empty box
            myself.add_mark(self.database,
                            self.database.get_person_from_handle(indi_handle))

        self.canvas.add_box(myself)

        #make the lines
        indx = index[LVL_GEN]
        self.lines[indx] = myself
        if indx > 1:
            if self.lines[indx - 1].line_to is None:
                line = LineBase(self.lines[indx - 1])
                self.lines[indx - 1].line_to = line
                self.canvas.add_line(line)
            else:
                line = self.lines[indx - 1].line_to
            line.add_to(myself)

        return myself

    def add_person_again(self, index, indi_handle, fams_handle):
        self.add_person(index, indi_handle, fams_handle)

    def add_marriage(self, index, indi_handle, fams_handle):
        """ Makes a marriage box and add that person into the Canvas. """

        if not self.inlc_marr:
            return

        myself = FamilyBox((index[0] - 1,) + index[1:])

        #calculate the text.
        myself.text = self.calc_items.calc_marriage(indi_handle, fams_handle)

        self.canvas.add_box(myself)

    def y_index(self, x_level, index):
        """ Calculate the column or generation that this person is in.
        x_level  -> 0 to max_gen-1
        index    -> 1 to (self.max_generation**2)-1
        """
        #Calculate which row in the column of people.
        tmp_y = index - (2**x_level)
        #Calculate which row in the table (yes table) of people.
        delta = (2**self.max_generation) // (2**(x_level))
        return int((delta / 2) + (tmp_y * delta)) - 1

    def do_y_indx(self):
        ''' Make the y_index for all boxes
        first off of a forumula, then remove blank areas around the edges,
        then compress the tree if desired
        '''
        min_y = self.y_index(self.canvas.boxes[0].level[LVL_GEN],
                             self.canvas.boxes[0].level[LVL_INDX])
        for box in self.canvas.boxes:
            if "fam" in box.boxstr:
                box.level = box.level + \
                    (self.y_index(box.level[LVL_GEN] - 1,
                                  int(box.level[LVL_INDX] / 2)),)
            else:
                box.level = box.level + \
                    (self.y_index(box.level[LVL_GEN], box.level[LVL_INDX]),)
            min_y = min(min_y, box.level[LVL_Y])
            #print (str(box.level))

        #if a last father (of fathers) does not have a father/parents
        #Then there could be a gap.  Remove this gap
        if min_y > 0:
            for box in self.canvas.boxes:
                box.level = box.level[:LVL_Y] + (box.level[LVL_Y] - min_y,)

        #Now that we have y_index, lets see if we need to squish the tree
        self.canvas.boxes.sort()  # Sort them on the y_index
        if not self.compress_tree:
            return
        #boxes are already in top down [LVL_Y] form so lets
        #set the box in the correct y level depending on compress_tree
        y_level = 0
        current_y = self.canvas.boxes[0].level[LVL_Y]
        for box in self.canvas.boxes:
            y_index = box.level[LVL_Y]
            if y_index > current_y:
                current_y = y_index
                y_level += 1
            box.level = box.level[:LVL_Y] + (y_level,)

    def do_sibs(self):
        if not self.inc_sib or self.center_family is None:
            return

        family = self.database.get_family_from_handle(self.center_family)
        mykids = [kid.ref for kid in family.get_child_ref_list()]

        if len(mykids) == 1:  # No other siblings.  Don't do anything.
            return

        # The first person is the center person had he/she has our information
        center = self.canvas.boxes.pop(self.canvas.boxes.index(self.lines[1]))
        line = center.line_to
        level = center.level[LVL_Y]

        move = level - (len(mykids) // 2) + ((len(mykids) + 1) % 2)

        if move < 0:
            # more kids than parents.  ran off the page.  Move them all down
            for box in self.canvas.boxes:
                box.level = (box.level[0], box.level[1], box.level[2] - move)
            move = 0

        line.start = []
        rrr = -1  # if len(mykids)%2 == 1 else 0
        for kid in mykids:
            rrr += 1
            mee = self.add_person((1, 1, move + rrr), kid, self.center_family)
            line.add_from(mee)
            #mee.level = (0, 1, level - (len(mykids)//2)+rrr)
        mee.line_to = line

    def start(self, person_id):
        """ go ahead and make it happen """
        center = self.database.get_person_from_gramps_id(person_id)
        if center is None:
            raise ReportError(
                _("Person %s is not in the Database") % person_id)
        center_h = center.get_handle()

        #Step 1.  Get the people
        self.recurse(center_h)

        #Step 2.  Calculate the y_index for everyone
        self.do_y_indx()

        #Step 3.  Siblings of the center person
        self.do_sibs()


#------------------------------------------------------------------------
#
# Transform Classes
#
#------------------------------------------------------------------------
#------------------------------------------------------------------------
# Class lr_Transform
#------------------------------------------------------------------------
class LRTransform:
    """
    setup all of the boxes on the canvas in for a left/right report
    """
    def __init__(self, canvas, max_generations):
        self.canvas = canvas
        self.rept_opts = canvas.report_opts
        self.y_offset = (self.rept_opts.littleoffset * 2 +
                         self.canvas.title.height)

    def _place(self, box):
        """ put the box in it's correct spot """
        #1. cm_x
        box.x_cm = self.rept_opts.littleoffset
        box.x_cm += (box.level[LVL_GEN] *
                     (self.rept_opts.col_width + self.rept_opts.max_box_width))
        #2. cm_y
        box.y_cm = self.rept_opts.max_box_height + self.rept_opts.box_pgap
        box.y_cm *= box.level[LVL_Y]
        box.y_cm += self.y_offset
        #if box.height < self.rept_opts.max_box_height:
        #    box.y_cm += ((self.rept_opts.max_box_height - box.height) /2)

    def place(self):
        """ Step through boxes so they can be put in the right spot """
        #prime the pump
        self.__last_y_level = self.canvas.boxes[0].level[LVL_Y]
        #go
        for box in self.canvas.boxes:
            self._place(box)


#------------------------------------------------------------------------
#
# class make_report
#
#------------------------------------------------------------------------
class MakeReport:

    def __init__(self, dbase, doc, canvas, font_normal):

        self.database = dbase
        self.doc = doc
        self.canvas = canvas
        self.font_normal = font_normal

        _gui = GUIConnect()
        self.inlc_marr = _gui.inc_marr()
        self.compress_tree = _gui.compress_tree()

        self.mother_ht = self.father_ht = 0

        self.max_generations = 0

    def get_height_width(self, box):
        """
        obtain width information for each level (x)
        obtain height information for each item
        """

        self.canvas.set_box_height_width(box)

        if box.width > self.canvas.report_opts.max_box_width:
            self.canvas.report_opts.max_box_width = box.width  # + box.shadow

        if box.level[LVL_Y] > 0:
            if box.level[LVL_INDX] % 2 == 0 and box.height > self.father_ht:
                self.father_ht = box.height
            elif box.level[LVL_INDX] % 2 == 1 and box.height > self.mother_ht:
                self.mother_ht = box.height

        if box.level[LVL_GEN] > self.max_generations:
            self.max_generations = box.level[LVL_GEN]

    def get_generations(self):
        return self.max_generations

    def start(self):
        # __gui = GUIConnect()
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
        transform = LRTransform(self.canvas, self.max_generations)
        transform.place()


class GUIConnect:
    """ This is a BORG object.  There is ONLY one.
    This give some common routines that EVERYONE can use like
      get the value from a GUI variable
    """

    __shared_state = {}

    def __init__(self):  # We are BORG!
        self.__dict__ = self.__shared_state

    def set__opts(self, options, locale, name_displayer):
        """ Set only once as we are BORG.  """
        self.__opts = options
        self.locale = locale
        self.n_d = name_displayer

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
        if title_type:
            return TitleA(doc, self.locale, self.n_d)
        else:
            return TitleN(doc, self.locale)

    def inc_marr(self):
        return self.get_val("inc_marr")

    def inc_sib(self):
        return self.get_val("inc_siblings")

    def maxgen(self):
        return self.get_val("maxgen")

    def fill_out(self):
        return self.get_val("fill_out")

    def compress_tree(self):
        return self.get_val("compress_tree")


#------------------------------------------------------------------------
#
# AncestorTree
#
#------------------------------------------------------------------------
class AncestorTree(Report):
    """ AncestorTree Report """

    def __init__(self, database, options, user):
        """
        Create AncestorTree object that produces the report.

        The arguments are:

        database        - the Gramps database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance
        """
        Report.__init__(self, database, options, user)

        self.options = options
        self._user = user

        self.set_locale(options.menu.get_option_by_name('trans').get_value())
        stdoptions.run_date_format_option(self, options.menu)
        stdoptions.run_private_data_option(self, options.menu)
        stdoptions.run_living_people_option(self, options.menu, self._locale)
        self.database = CacheProxyDb(self.database)
        stdoptions.run_name_format_option(self, options.menu)
        self._nd = self._name_display

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
        incl_private - Whether to include private data
        living_people - How to handle living people
        years_past_death - Consider as living this many years after death

        We will
        1. a canvas in its full one-page size
        2. a page that we wish to print on
        scale up/down either or both of the above as needed/desired.
        almost all of this should be moved into Canvas!
        """

        database = self.database

        self.connect = GUIConnect()
        self.connect.set__opts(self.options.menu, self._locale, self._nd)

        #Set up the canvas that we will print on.
        style_sheet = self.doc.get_style_sheet()
        font_normal = style_sheet.get_paragraph_style("AC2-Normal").get_font()

        #The canvas that we will put our report on and print off of
        self.canvas = Canvas(self.doc,
                             ReportOptions(self.doc, font_normal, 'AC2-line'))

        self.canvas.report_opts.box_shadow *= \
            self.connect.get_val('shadowscale')
        self.canvas.report_opts.box_pgap *= self.connect.get_val('box_Yscale')
        self.canvas.report_opts.box_mgap *= self.connect.get_val('box_Yscale')

        with self._user.progress(_('Ancestor Tree'),
                                 _('Making the Tree...'), 4) as step:

            #make the tree onto the canvas
            # inlc_marr = self.connect.get_val("inc_marr")
            self.max_generations = self.connect.get_val('maxgen')
            tree = MakeAncestorTree(database, self.canvas)
            tree.start(self.connect.get_val('pid'))
            tree = None

            step()

            #Title
            title = self.connect.title_class(self.doc)
            center = self.database.get_person_from_gramps_id(
                self.connect.get_val('pid'))
            title.calc_title(center)
            self.canvas.add_title(title)

            #make the report as big as it wants to be.
            report = MakeReport(database, self.doc, self.canvas, font_normal)
            report.start()
            self.max_generations = report.get_generations()  # already know
            report = None

            step()

            #Note?
            if self.connect.get_val("inc_note"):
                note_box = NoteBox(self.doc, "AC2-note-box",
                                   self.connect.get_val("note_place"))
                subst = SubstKeywords(self.database, self._locale, self._nd,
                                      None, None)
                note_box.text = subst.replace_and_clean(
                    self.connect.get_val('note_disp'))
                self.canvas.add_note(note_box)

            #Now we have the report in its full size.
            #Do we want to scale the report?
            one_page = self.connect.get_val("resize_page")
            scale_report = self.connect.get_val("scale_tree")

            scale = self.canvas.scale_report(one_page,
                                             scale_report != 0,
                                             scale_report == 2)

            step()

            if scale != 1 or self.connect.get_val('shadowscale') != 1.0:
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
        colsperpage = int(
            colsperpage / (self.canvas.report_opts.max_box_width +
                           self.canvas.report_opts.col_width))
        colsperpage = colsperpage or 1

        #####################
        #Vars
        if prnnum:
            page_num_box = PageNumberBox(self.doc, 'AC2-box', self._locale)

        #TODO - Here

        #####################
        #ok, everyone is now ready to print on the canvas.  Paginate?
        self.canvas.paginate(colsperpage, one_page)

        #####################
        #Yeah!!!
        #lets finally make some pages!!!
        #####################
        pages = self.canvas.page_count(incblank)
        with self._user.progress(_('Ancestor Tree'),
                                 _('Printing the Tree...'), pages) as step:

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

                step()
                self.doc.end_page()

    def scale_styles(self, scale):
        """
        Scale the styles for this report.
        """
        style_sheet = self.doc.get_style_sheet()

        graph_style = style_sheet.get_draw_style("AC2-box")
        graph_style.set_shadow(graph_style.get_shadow(),
                               self.canvas.report_opts.box_shadow * scale)
        graph_style.set_line_width(graph_style.get_line_width() * scale)
        style_sheet.add_draw_style("AC2-box", graph_style)

        graph_style = style_sheet.get_draw_style("AC2-fam-box")
        graph_style.set_shadow(graph_style.get_shadow(),
                               self.canvas.report_opts.box_shadow * scale)
        graph_style.set_line_width(graph_style.get_line_width() * scale)
        style_sheet.add_draw_style("AC2-fam-box", graph_style)

        graph_style = style_sheet.get_draw_style("AC2-note-box")
        #graph_style.set_shadow(graph_style.get_shadow(),
        #                       self.canvas.report_opts.box_shadow * scale)
        graph_style.set_line_width(graph_style.get_line_width() * scale)
        style_sheet.add_draw_style("AC2-note-box", graph_style)

        para_style = style_sheet.get_paragraph_style("AC2-Normal")
        font = para_style.get_font()
        font.set_size(font.get_size() * scale)
        para_style.set_font(font)
        style_sheet.add_paragraph_style("AC2-Normal", para_style)

        para_style = style_sheet.get_paragraph_style("AC2-Note")
        font = para_style.get_font()
        font.set_size(font.get_size() * scale)
        para_style.set_font(font)
        style_sheet.add_paragraph_style("AC2-Note", para_style)

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
        self.__db = dbase
        self.__pid = None
        self.box_Y_sf = None
        self.box_shadow_sf = None
        MenuReportOptions.__init__(self, name, dbase)

    def get_subject(self):
        """ Return a string that describes the subject of the report. """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        return _nd.display(person)

    def add_menu_options(self, menu):

        ##################
        category_name = _("Tree Options")

        self.__pid = PersonOption(_("Center Person"))
        self.__pid.set_help(_("The center person for the tree"))
        menu.add_option(category_name, "pid", self.__pid)

        siblings = BooleanOption(
            _('Include siblings of the center person'), False)
        siblings.set_help(
            _("Whether to only display the center person or all "
              "of his/her siblings too"))
        menu.add_option(category_name, "inc_siblings", siblings)

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

        compress = BooleanOption(_('Compress tree'), True)
        compress.set_help(
            _("Whether to remove any extra blank spaces set "
              "aside for people that are unknown"))
        menu.add_option(category_name, "compress_tree", compress)

        #better to 'Show siblings of\nthe center person
        #Spouse_disp = EnumeratedListOption(_("Show spouses of\nthe center "
        #                                     "person"), 0)
        #Spouse_disp.add_item(0, _("No.  Do not show Spouses"))
        #Spouse_disp.add_item(1, _("Yes, and use the Main Display Format"))
        #Spouse_disp.add_item(2, _("Yes, and use the Secondary "
        #                           "Display Format"))
        #Spouse_disp.set_help(_("Show spouses of the center person?"))
        #menu.add_option(category_name, "Spouse_disp", Spouse_disp)

        ##################
        category_name = _("Report Options")

        self.title = EnumeratedListOption(_("Report Title"), 0)
        self.title.add_item(0, _("Do not include a title"))
        self.title.add_item(1, _("Include Report Title"))
        self.title.set_help(_("Choose a title for the report"))
        menu.add_option(category_name, "report_title", self.title)

        border = BooleanOption(_('Include a border'), False)
        border.set_help(_("Whether to make a border around the report."))
        menu.add_option(category_name, "inc_border", border)

        prnnum = BooleanOption(_('Include Page Numbers'), False)
        prnnum.set_help(_("Whether to print page numbers on each page."))
        menu.add_option(category_name, "inc_pagenum", prnnum)

        self.scale = EnumeratedListOption(_("Scale tree to fit"), 0)
        self.scale.add_item(0, _("Do not scale tree"))
        self.scale.add_item(1, _("Scale tree to fit page width only"))
        self.scale.add_item(2, _("Scale tree to fit the size of the page"))
        self.scale.set_help(
            _("Whether to scale the tree to fit a specific paper size"))
        menu.add_option(category_name, "scale_tree", self.scale)
        self.scale.connect('value-changed', self.__check_blank)

        if "BKI" not in self.name.split(","):
            self.__onepage = BooleanOption(
                _("Resize Page to Fit Tree size\n"
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

        self.__blank = BooleanOption(_('Include Blank Pages'), True)
        self.__blank.set_help(_("Whether to include pages that are blank."))
        menu.add_option(category_name, "inc_blank", self.__blank)

        self.__check_blank()

        ##################
        category_name = _("Report Options (2)")

        stdoptions.add_name_format_option(menu, category_name)

        stdoptions.add_living_people_option(menu, category_name)

        stdoptions.add_private_data_option(menu, category_name)

        locale_opt = stdoptions.add_localization_option(menu, category_name)

        stdoptions.add_date_format_option(menu, category_name, locale_opt)

        ##################
        category_name = _("Display")

        disp = TextOption(_("Father\nDisplay Format"),
                          ["$n",
                           "%s $b" % _BORN,
                           "-{%s $d}" % _DIED])
        disp.set_help(_("Display format for the fathers box."))
        menu.add_option(category_name, "father_disp", disp)

        #Will add when libsubstkeyword supports it.
        #missing = EnumeratedListOption(_("Replace missing\nplaces\\dates \
        #                                 with"), 0)
        #missing.add_item(0, _("Does not display anything"))
        #missing.add_item(1, _("Displays '_____'"))
        #missing.set_help(_("What will print when information is not known"))
        #menu.add_option(category_name, "miss_val", missing)

        disp_mom = TextOption(_("Mother\nDisplay Format"),
                              ["$n",
                               "%s $b" % _BORN,
                               "%s $m" % _MARR,
                               "-{%s $d}" % _DIED])
        disp_mom.set_help(_("Display format for the mothers box."))
        menu.add_option(category_name, "mother_disp", disp_mom)

        center_disp = EnumeratedListOption(_("Center person uses\n"
                                             "which format"), 0)
        center_disp.add_item(0, _("Use Fathers Display format"))
        center_disp.add_item(1, _("Use Mothers display format"))
        center_disp.set_help(_("The display format for the center person"))
        menu.add_option(category_name, "center_uses", center_disp)

        self.incmarr = BooleanOption(_('Include Marriage box'), False)
        self.incmarr.set_help(
            _("Whether to include a separate marital box in the report"))
        menu.add_option(category_name, "inc_marr", self.incmarr)
        self.incmarr.connect('value-changed', self._incmarr_changed)

        self.marrdisp = StringOption(_("Marriage\nDisplay Format"),
                                     "%s $m" % _MARR)
        self.marrdisp.set_help(_("Display format for the marital box."))
        menu.add_option(category_name, "marr_disp", self.marrdisp)
        self._incmarr_changed()

        ##################
        category_name = _("Advanced")

        repldisp = TextOption(
            _("Replace Display Format:\n'Replace this'/' with this'"),
            [])
        repldisp.set_help(_("i.e.\nUnited States of America/U.S.A"))
        menu.add_option(category_name, "replace_list", repldisp)

        # TODO this code is never used and so I conclude it is for future use
        # self.__include_images = BooleanOption(
        #                       _('Include thumbnail images of people'), False)
        # self.__include_images.set_help(
        #                       _("Whether to include thumbnails of people."))
        # menu.add_option(category_name, "includeImages",
        #                 self.__include_images)

        self.usenote = BooleanOption(_('Include a note'), False)
        self.usenote.set_help(_("Whether to include a note on the report."))
        menu.add_option(category_name, "inc_note", self.usenote)
        self.usenote.connect('value-changed', self._usenote_changed)

        self.notedisp = TextOption(_("Note"), [])
        self.notedisp.set_help(_("Add a note\n\n"
                                 "$T inserts today's date"))
        menu.add_option(category_name, "note_disp", self.notedisp)

        locales = NoteType(0, 1)
        self.notelocal = EnumeratedListOption(_("Note Location"), 0)
        for num, text in locales.note_locals():
            self.notelocal.add_item(num, text)
        self.notelocal.set_help(_("Where to place the note."))
        menu.add_option(category_name, "note_place", self.notelocal)
        self._usenote_changed()

        self.box_Y_sf = NumberOption(_("inter-box scale factor"),
                                     1.00, 0.10, 2.00, 0.01)
        self.box_Y_sf.set_help(
            _("Make the inter-box spacing bigger or smaller"))
        menu.add_option(category_name, "box_Yscale", self.box_Y_sf)

        self.box_shadow_sf = NumberOption(_("box shadow scale factor"),
                                          1.00, 0.00, 2.00, 0.01)  # down to 0
        self.box_shadow_sf.set_help(_("Make the box shadow bigger or smaller"))
        menu.add_option(category_name, "shadowscale", self.box_shadow_sf)

    def _incmarr_changed(self):
        """
        If Marriage box is not enabled, disable Marriage Display Format box
        """
        value = self.incmarr.get_value()
        self.marrdisp.set_available(value)

    def _usenote_changed(self):
        """
        If Note box is not enabled, disable Note Location box
        """
        value = self.usenote.get_value()
        self.notelocal.set_available(value)

    def __check_blank(self):
        if self.__onepage:
            value = not self.__onepage.get_value()
        else:
            value = True
        off = value and (self.scale.get_value() != 2)
        self.__blank.set_available(off)

    def __fillout_vals(self):
        max_gen = self.max_gen.get_value()
        old_val = self.fillout.get_value()
        item_list = []
        item_list.append([0, _("No generations of empty boxes "
                               "for unknown ancestors")])
        if max_gen > 1:
            item_list.append([1, _("One Generation of empty boxes "
                                   "for unknown ancestors")])

        item_list.extend(
            [itr, str(itr) +
             _(" Generations of empty boxes for unknown ancestors")]
            for itr in range(2, max_gen))

        self.fillout.set_items(item_list)
        if old_val + 2 > len(item_list):
            self.fillout.set_value(len(item_list) - 2)

    def make_default_style(self, default_style):
        """Make the default output style for the Ancestor Tree."""

        # Paragraph Styles:
        font = FontStyle()
        font.set_size(9)
        font.set_type_face(FONT_SANS_SERIF)
        para_style = ParagraphStyle()
        para_style.set_font(font)
        para_style.set_description(
            _('The basic style used for the text display.'))
        default_style.add_paragraph_style("AC2-Normal", para_style)
        box_shadow = PT2CM(font.get_size()) * .6

        font = FontStyle()
        font.set_size(9)
        font.set_type_face(FONT_SANS_SERIF)
        para_style = ParagraphStyle()
        para_style.set_font(font)
        para_style.set_description(
            _('The basic style used for the note display.'))
        default_style.add_paragraph_style("AC2-Note", para_style)

        font = FontStyle()
        font.set_size(16)
        font.set_type_face(FONT_SANS_SERIF)
        para_style = ParagraphStyle()
        para_style.set_font(font)
        para_style.set_alignment(PARA_ALIGN_CENTER)
        para_style.set_description(_('The style used for the title.'))
        default_style.add_paragraph_style("AC2-Title", para_style)

        # Draw styles
        graph_style = GraphicsStyle()
        graph_style.set_paragraph_style("AC2-Normal")
        graph_style.set_shadow(1, box_shadow)  # shadow set by text size
        graph_style.set_fill_color((255, 255, 255))
        default_style.add_draw_style("AC2-box", graph_style)

        graph_style = GraphicsStyle()
        graph_style.set_paragraph_style("AC2-Normal")
        #graph_style.set_shadow(0, PT2CM(9))  # shadow set by text size
        graph_style.set_fill_color((255, 255, 255))
        default_style.add_draw_style("AC2-fam-box", graph_style)

        graph_style = GraphicsStyle()
        graph_style.set_paragraph_style("AC2-Note")
        graph_style.set_fill_color((255, 255, 255))
        default_style.add_draw_style("AC2-note-box", graph_style)

        # TODO this seems meaningless, as only the text is displayed
        graph_style = GraphicsStyle()
        graph_style.set_paragraph_style("AC2-Title")
        graph_style.set_color((0, 0, 0))
        graph_style.set_fill_color((255, 255, 255))
        graph_style.set_line_width(0)
        graph_style.set_description(_("Cannot edit this reference"))
        default_style.add_draw_style("AC2-Title-box", graph_style)

        graph_style = GraphicsStyle()
        default_style.add_draw_style("AC2-line", graph_style)

#=====================================
#But even if you should suffer for what is right, you are blessed.
#"Do not fear what they fear ; do not be frightened."
#Take Courage
#1 Peter 3:14
