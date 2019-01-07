#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008-2010  Craig J. Anderson
# Copyright (C) 2014       Paul Franklin
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

"""Reports/Graphical Reports/Tree_Base"""

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.plug.report import utils
from gramps.plugins.lib.libsubstkeyword import SubstKeywords
from gramps.gen.plug.docgen import (IndexMark, INDEX_TYPE_TOC)

PT2CM = utils.pt2cm

#------------------------------------------------------------------------
#
# Class Calc_Lines
#
#------------------------------------------------------------------------
class CalcLines:
    """ wrapper for libsubstkeyword and added functionality for
    replacements.

    Receive:  Individual and family handle, and display format [string]
    return: [Text] ready for a box.
    """
    def __init__(self, dbase, repl, locale, name_displayer):
        self.database = dbase
        self.display_repl = repl
        #self.default_string = default_str
        self._locale = locale
        self._nd = name_displayer

    def calc_lines(self, _indi_handle, _fams_handle, workinglines):
        """
        In this pass we will:
        1. make our text and do our replacements
        2. remove any extra (unwanted) lines with the compres option
        """

        ####################
        #1.1  Get our line information here
        subst = SubstKeywords(self.database, self._locale, self._nd,
                              _indi_handle, _fams_handle)
        lines = subst.replace_and_clean(workinglines)

        ####################
        #1.2  do our replacements
        lns = []
        for line in lines:
            for pair in self.display_repl:
                if pair.count("/") == 1:
                    repl = pair.split("/", 1)
                    line = line.replace(repl[0], repl[1])
            lns.append(line)

        return lns


#------------------------------------------------------------------------
#
# Class Canvas/Pages
#
#------------------------------------------------------------------------
class Page:
    """ This class is a printable page.
        Offsets from the canvas, Page numbers
        boxes and lines
        """
    def __init__(self, canvas):
        #parts from canvas
        #self.doc = doc
        self.canvas = canvas

        #parts about the page
        self.page_x_offset = 0
        self.page_y_offset = 0
        self.x_page_num = 0
        self.y_page_num = 0
        self.boxes = []   #All object must derive from BoxBase
        self.lines = []   #All must derive form Linebase
        self.note = None

    def is_blank(self):
        """ Am I a blank page?  Notes and Titles are boxes too """
        return self.boxes == [] and self.lines == []

    def add_box(self, box):
        """ The box must derive from class Box_Base(Object): """
        self.boxes.append(box)
        box.page = self

    def add_line(self, line):
        """ Add a line onto this page """
        self.lines.append(line)

    def draw_border(self, line_name):
        doc = self.canvas.doc
        if self.y_page_num == 0:
            doc.draw_line(line_name, 0, 0,
                               doc.get_usable_width(), 0)
        if self.x_page_num == 0:
            doc.draw_line(line_name, 0, 0, 0,
                               doc.get_usable_height())
        if self.y_page_num == self.canvas.y_pages-1:
            doc.draw_line(line_name, 0,
                               doc.get_usable_height(),
                               doc.get_usable_width(),
                               doc.get_usable_height())
        if self.x_page_num == self.canvas.x_pages-1:
            doc.draw_line(line_name, doc.get_usable_width(),
                               0, doc.get_usable_width(),
                               doc.get_usable_height())

    def display(self):
        """ Display all boxes and lines that are on this page """
        for box in self.boxes:
            box.display()
        for line in self.lines:
            line.display(self)


class Canvas(Page):
    """ The Canvas is two things.
      The all in one canvas.  a canvas is a page of unlimited size
      a group of pages.  each page is set is size and shows only a
       part of what is on the entire canvas
    """
    def __init__(self, doc, report_opts):
        Page.__init__(self, self)
        self.doc = doc
        self.report_opts = report_opts

        #How many pages are there in the report.  one more than real.
        self.x_pages = 1
        self.y_pages = 1
        self.__pages = {(0, 0): self}  #set page 0,0 to me.
        self.__fonts = {}  #keep a list of fonts so we don't have to lookup.
        self.title = None
        self.note = None

    def __new_page(self, x_page, y_page, x_offset, y_offset):
        """ Make a new page.  This will only happen if we are
            paginating (making new pages to hold parts of the canvas) """
        if x_page >= self.x_pages:
            self.x_pages = x_page + 1
        new_page = Page(self)
        new_page.x_page_num = x_page
        new_page.y_page_num = y_page
        new_page.page_x_offset = x_offset
        new_page.page_y_offset = y_offset
        self.__pages[x_page, y_page] = new_page
        return new_page

    def sort_boxes_on_y_cm(self):
        """ sorts the list of boxes on the canvas by .y_cm (top down) """
        self.boxes.sort( key=lambda box: box.y_cm)

    def add_title(self, title):
        """ The title must derive from class TitleBox(BoxBase): """
        self.title = title
        self.title.cm_y = self.report_opts.littleoffset

    def add_note(self, note):
        """ The note must derive from class NoteBox(BoxBase, NoteType) """
        self.note = note
        self.set_box_height_width(self.note)

    def __get_font(self, box):
        """ returns the font used by a box.  makes a list of all seen fonts
        to be faster.  If a new is found, run through the process to get it """
        if box.boxstr not in self.__fonts:
            style_sheet = self.doc.get_style_sheet()
            style_name = style_sheet.get_draw_style(box.boxstr)
            style_name = style_name.get_paragraph_style()
            self.__fonts[box.boxstr] = \
                style_sheet.get_paragraph_style(style_name).get_font()

        return self.__fonts[box.boxstr]

    def get_report_height_width(self):
        """ returns the (max width, max height) of the report
        This does not take into account any shadows """
        max_width = 0
        max_height = 0
        for box in self.boxes:
            tmp = box.x_cm + box.width
            if tmp > max_width:
                max_width = tmp
            tmp = box.y_cm + box.height
            if tmp > max_height:
                max_height = tmp
        max_width += self.report_opts.box_shadow
        max_width += self.report_opts.littleoffset
        max_height += self.report_opts.box_shadow
        max_height += self.report_opts.littleoffset
        return (max_width, max_height)

    def __scale_canvas(self, scale_amount):
        """ scales everything up/down depending upon scale_amount """
        self.report_opts.scale_everything(scale_amount)
        self.title.scale(scale_amount)
        if self.note is not None:
            self.note.scale(scale_amount)
        #scale down everyone!
        for box in self.boxes:
            box.scale(scale_amount)

    def set_box_height_width(self, box):
        """ Sets the .width and .height of a box.  """
        if box.boxstr == "None":
            box.height = box.width = 0
            return

        font = self.__get_font(box)
        #####################
        #Get the width
        for line in box.text:
            width = self.doc.string_width(font, line)
            width = PT2CM(width)
            if width > box.width:
                box.width = width

        #####################
        #Get the height
        height = len(box.text) * font.get_size() * 1.5
        height += 1.0/2.0 * font.get_size() #funny number(s) based upon font.
        box.height = PT2CM(height)

    def page_count(self, incblank):
        count = 0
        if incblank:
            return self.y_pages * self.x_pages

        for y_p in range(self.y_pages):
            for x_p in range(self.x_pages):
                if (x_p, y_p) in self.__pages:
                    count += 1
        return count

    def page_iter_gen(self, incblank):
        """ generate the pages of the report.  do so in a left to right
        up down approach.  incblank asks to include blank pages """
        blank = Page(self)
        for y_p in range(self.y_pages):
            for x_p in range(self.x_pages):
                if (x_p, y_p) in self.__pages:
                    yield self.__pages[(x_p, y_p)]
                else:
                    if incblank:
                        blank.x_page_num = x_p
                        blank.y_page_num = y_p
                        yield blank

    def __add_box_to_page(self, x_page, y_page, x_offset, y_offset, box):
        """ adds a box to a page.  If the page is not there, make it first """
        if (x_page, y_page) not in self.__pages:
            #Add the new page into the dictionary
            self.__new_page(x_page, y_page, x_offset, y_offset)

        #Add the box into the page
        self.__pages[x_page, self.y_pages-1].add_box(box)

    def scale_report(self, one_page, scale_to_width, scale_to_height):
        """ We have a report in its full size (on the canvas
        and pages to print on.  scale one or both as needed/desired.

        - one_page, boolean.  Whether to make the page(or parts of) the size
            of the report
        - scale_to_width, boolean.  Scale the report width to the page size?
        - scale_to_height, boolean.  Scale the report height to page size?
        """

        if scale_to_width or scale_to_height:
            max_width, max_height = self.canvas.get_report_height_width()
            #max_width  += self.report_opts.littleoffset
            #max_height += self.report_opts.littleoffset

        """
        calc - Calculate the scale amount (if any).
          <1 everything is smaller to fit on the page
          1 == no scaling
          >1 make everything bigger to fill out the page
        """
        scale = 1
        scaled_report_to = None

        #####################
        #scale the report option - width
        if scale_to_width:
            #Check the width of the title
            title_width = self.title.width
            title_width += self.report_opts.littleoffset * 2

            max_width = max(title_width, max_width)

            #This will be our base amount and
            #then we will decrease only as needed from here.

            scale = self.doc.get_usable_width() / max_width
            scaled_report_to = "width"

        #####################
        #scale the report option - height
        if scale_to_height:
            tmp = self.doc.get_usable_height() / max_height
            if not scale_to_width or tmp < scale:
                scale = tmp
                scaled_report_to = "height"

        #Now I have the scale amount
        if scale != 1:  #scale everything on the canvas
            self.__scale_canvas(scale)

        #####################
        #Scale the page option
        if one_page:

            #user wants PAGE to be the size of the report.
            size = self.doc.paper.get_size()
            size.name = 'custom'

            max_width, max_height = \
                self.canvas.get_report_height_width()

            if scaled_report_to != "width":
                #calculate the width of the report
                #max_width  += self.report_opts.littleoffset
                max_width += self.doc.paper.get_left_margin()
                max_width += self.doc.paper.get_right_margin()

                #calculate the width of the title
                title_width = self.canvas.title.width
                title_width += self.doc.paper.get_left_margin()
                title_width += self.doc.paper.get_right_margin()
                title_width += self.report_opts.littleoffset
                max_width = max(title_width, max_width)

                size.set_width(max_width)

            if scaled_report_to != "height":
                #calculate the height of the report
                max_height += self.doc.paper.get_top_margin()
                max_height += self.doc.paper.get_bottom_margin()
                #max_height += self.report_opts.littleoffset
                size.set_height(max_height)

        return scale


    def __paginate_x_offsets(self, colsperpage):
        """ Go through the boxes and get the x page offsets """
        #fix soon.  should not use .level
        liloffset = self.report_opts.littleoffset
        x_page_offsets = {0:0}  #change me to [] ???
        for box in self.boxes:
            x_index = box.level[0]
            x_page = x_index // colsperpage
            if x_page not in x_page_offsets and x_index % colsperpage == 0:
                x_page_offsets[x_page] = box.x_cm - liloffset
                if x_page >= self.x_pages:
                    self.x_pages = x_page+1
        return x_page_offsets

    def __paginate_y_pages(self, colsperpage, x_page_offsets):
        """ Go through the boxes and put each one in a page
        note that the self.boxes needs to be sorted by .y_cm """
        page_y_top = [0]
        page_y_height = [self.doc.get_usable_height()]
        liloffset = self.report_opts.littleoffset

        for box in self.boxes:
            #check to see if this box cross over to the next (y) page
            height = box.y_cm + liloffset + box.height #+ box.shadow/2

            if height > page_y_height[-1]:
                #we went off the end
                page_y_height.append(box.y_cm - liloffset + page_y_height[0])
                page_y_top.append(box.y_cm - liloffset)
                self.y_pages = len(page_y_height)

            #Calculate my (x) page
            #fix soon.  should not use .level
            x_page = box.level[0] // colsperpage

            self.__add_box_to_page(x_page, self.y_pages-1,
                                   x_page_offsets[x_page],
                                   page_y_top[self.y_pages-1],
                                   box)
            #if not self.__pages.has_key((x_page, self.y_pages-1)):
            #    #Add the new page into the dictionary
            #    self.__new_page(x_page, self.y_pages-1,
            #                    )
            #
            ##Add the box into the page
            #self.__pages[x_page, self.y_pages-1].add_box(box)
        return page_y_top

    def __paginate_note(self, x_page_offsets, page_y_top):
        """ Put the note on first.  it can be overwritten by other
        boxes but it CAN NOT overwrite a box. """
        x_page, y_page = self.note.set_on_page(self)
        if (x_page, y_page) not in self.__pages:
            #Add the new page into the dictionary
            self.__new_page(x_page, y_page,
                            x_page_offsets[x_page], page_y_top[y_page])
        #Add the box into the page
        self.__pages[x_page, y_page].boxes.insert(0, self.note)
        self.note.doc = self.doc
        self.note.page = self

    def __paginate_lines(self, x_page_offsets, page_y_top):
        """ Step three go through the lines and put each in page(s) """
        for box1 in self.boxes:
            if not box1.line_to:
                continue

            line = box1.line_to

            pages = [box1.page.y_page_num]

            end = line.start + line.end

            x_page = box1.page.x_page_num
            start_y_page = end[0].page.y_page_num
            end_y_page = end[0].page.y_page_num

            for box in end:
                y_page = box.page.y_page_num
                if y_page not in pages:
                    if (x_page, y_page) not in self.__pages:
                        #Add the new page into the dictionary
                        self.__new_page(x_page, y_page,
                                        x_page_offsets[x_page],
                                        page_y_top[y_page])
                    self.__pages[x_page, y_page].add_line(box1.line_to)
                    pages.append(y_page)

                if y_page < start_y_page:
                    start_y_page = y_page
                if y_page > end_y_page:
                    end_y_page = y_page

            #if len(end) = 2 & end[0].y_page = 0 & end[1].y_page = 4
            #the line will not print on y_pages 1,2,3.  Fix that here.
            #x_page = start_x_page
            for y_page in range(start_y_page, end_y_page+1):
                if y_page not in pages:
                    if (x_page, y_page) not in self.__pages:
                        #Add the new page into the dictionary
                        self.__new_page(x_page, y_page,
                                        x_page_offsets[x_page],
                                        page_y_top[y_page])
                    self.__pages[x_page, y_page].add_line(box1.line_to)

    def __paginate_title(self, x_page_offsets):
        #step four work with the title
        if self.title.boxstr == "None":
            return
        #x_page_offsets[page] tells me the widths I can use
        if len(x_page_offsets) > 1:
            if self.title.mark_text and not self.title.text:
                self.title.width = self.doc.get_usable_width()
                self.__pages[list(self.__pages.keys())[0]].add_box(self.title)
                return
            title_list = self.title.text.split(" ")
            title_font = self.__get_font(self.title)
            #space_width = PT2CM(self.doc.string_width(title_font," "))

            list_title = [title_list.pop(0)]
            while len(title_list):
                tmp = list_title[-1] + " " + title_list[0]
                if PT2CM(self.doc.string_width(title_font, tmp)) > \
                   x_page_offsets[1]:
                    list_title.append("")
                if list_title[-1] != "":
                    list_title[-1] += " "
                list_title[-1] += title_list.pop(0)

            start_page = int((len(x_page_offsets) - len(list_title)) / 2)
            for tmp in range(start_page):
                list_title.insert(0, "")
                list_title.append("")
            #one extra for security.  doesn't hurt.
            list_title.append("")

            x_page = 0
            for title in list_title:
                if title == "":
                    x_page += 1
                    continue
                if (x_page, 0) not in self.__pages:
                    #Add the new page into the dictionary
                    self.__new_page(x_page, 0, x_page_offsets[1], 0)

                title_part = TitleBox(self.doc, self.title.boxstr)
                title_part.text = list_title[x_page]
                title_part.width = x_page_offsets[1]

                #Add the box into the page
                self.__pages[x_page, 0].add_box(title_part)
                x_page = x_page + 1
        else:
            self.title.width = self.doc.get_usable_width()
            self.__pages[0, 0].add_box(self.title)

    def __paginate(self, colsperpage):
        """ take the boxes on the canvas and put them into separate pages.
        The boxes need to be sorted by y_cm """
        liloffset = self.report_opts.littleoffset
        self.__pages = {}
        x_page_offsets = self.__paginate_x_offsets(colsperpage)
        page_y_top = self.__paginate_y_pages(colsperpage, x_page_offsets)

        if self.note is not None:
            self.__paginate_note(x_page_offsets, page_y_top)
        self.__paginate_lines(x_page_offsets, page_y_top)
        self.__paginate_title(x_page_offsets)


    def paginate(self, colsperpage, one_page_report):
        """ self.boxes must be sorted by box.y_cm for this to work.  """
        if one_page_report:
            #self.canvas.add_box(self.canvas.title)
            title_part = TitleBox(self.doc, self.title.boxstr)
            title_part.text = self.title.text
            title_part.width = self.doc.get_usable_width()
            self.add_box(title_part)

            if self.note is not None:
                self.note.set_on_page(self)
                self.boxes.insert(0, self.note)
                self.note.doc = self.doc
                self.note.page = self
        else:
            self.__paginate(colsperpage)


#------------------------------------------------------------------------
#
# Class Box_Base
#
#------------------------------------------------------------------------
class BoxBase:
    """ boxes are always in/on a Page
    Needed to print are: boxstr, text, x_cm, y_cm, width, height
    """
    def __init__(self):
        self.page = None

        #'None' will cause an error.  Sub-classes will init
        self.boxstr = "None"
        self.text = ""
        #level requires ...
        # (#  - which column am I in  (zero based)
        # ,#  - Am I a (0)direct descendant/ancestor or (>0)other
        # , ) - anything else the report needs to run
        self.__mark = None  #Database person object
        self.level = (0,0)
        self.x_cm = 0.0
        self.y_cm = 0.0
        self.width = 0.0
        self.height = 0.0
        self.line_to = None
        #if text in TOC needs to be different from text, set mark_text
        self.mark_text = None

    def scale(self, scale_amount):
        """ Scale the amounts """
        self.x_cm *= scale_amount
        self.y_cm *= scale_amount
        self.width *= scale_amount
        self.height *= scale_amount

    def add_mark(self, database, person):
        self.__mark = utils.get_person_mark(database, person)

    def display(self):
        """ display the box accounting for page x, y offsets
        Ignore any box with 'None' is boxstr """
        if self.boxstr == "None":
            return

        doc = self.page.canvas.doc
        report_opts = self.page.canvas.report_opts
        text = '\n'.join(self.text)
        xbegin = self.x_cm - self.page.page_x_offset
        ybegin = self.y_cm - self.page.page_y_offset

        doc.draw_box(self.boxstr,
                text,
                xbegin, ybegin,
                self.width, self.height, self.__mark)

        #I am responsible for my own lines. Do them here.
        if self.line_to:
            #draw my line out here.
            self.line_to.display(self.page)
        if self.page.x_page_num > 0 and self.level[1] == 0 and \
           xbegin < report_opts.littleoffset*2:
            #I am a child on the first column
            yme = ybegin + self.height/2
            doc.draw_line(report_opts.line_str, 0, yme, xbegin, yme)

class TitleNoDisplay(BoxBase):
    """
    Holds information about the Title that will print on a TOC
    and NOT on the report
    """
    def __init__(self, doc, boxstr):
        """ initialize the title box """
        BoxBase.__init__(self)
        self.doc = doc
        self.boxstr = boxstr

    def set_box_height_width(self):
        self.width = self.height = 0

    def display(self):
        """ display the title box.  """
        #Set up the Table of Contents here
        if self.mark_text is None:
            mark = IndexMark(self.text, INDEX_TYPE_TOC, 1)
        else:
            mark = IndexMark(self.mark_text, INDEX_TYPE_TOC, 1)
        self.doc.center_text(self.boxstr, '', 0, -100, mark)

class TitleBox(BoxBase):
    """
    Holds information about the Title that will print on a page
    """
    def __init__(self, doc, boxstr):
        """ initialize the title box """
        BoxBase.__init__(self)
        self.doc = doc
        self.boxstr = boxstr
        if boxstr == "None":
            return

        style_sheet = self.doc.get_style_sheet()
        style_name = style_sheet.get_draw_style(self.boxstr)
        style_name = style_name.get_paragraph_style()
        self.font = style_sheet.get_paragraph_style(style_name).get_font()

    def set_box_height_width(self):
        if self.boxstr == "None":
            return
        #fix me. width should be the printable area
        self.width = PT2CM(self.doc.string_width(self.font, self.text))
        self.height = PT2CM(self.font.get_size() * 2)

    def _get_names(self, persons, name_displayer):
        """  A helper function that receives a list of persons and
        returns their names in a list """
        return [name_displayer.display(person) for person in persons]

    def display(self):
        """ display the title box.  """
        if self.page.y_page_num or self.boxstr == "None":
            return

        #Set up the Table of Contents here
        mark = IndexMark(self.text, INDEX_TYPE_TOC, 1)

        if self.text:
            self.doc.center_text(self.boxstr, self.text,
                             self.width/2, self.y_cm, mark)

class PageNumberBox(BoxBase):
    """
    Calculates information about the page numbers that will print on a page
    do not put in a value for PageNumberBox.text.  this will be calculated for
    each page """

    def __init__(self, doc, boxstr, locale):
        """ initialize the page number box """
        BoxBase.__init__(self)
        self.doc = doc
        self.boxstr = boxstr
        self._ = locale.translation.sgettext

    def __calc_position(self, page):
        """ calculate where I am to print on the page(s) """
        # translators: needed for Arabic, ignore otherwise
        self.text = "(%d" + self._(',') + "%d)"

        style_sheet = self.doc.get_style_sheet()
        style_name = style_sheet.get_draw_style(self.boxstr)
        style_name = style_name.get_paragraph_style()
        font = style_sheet.get_paragraph_style(style_name).get_font()

        #calculate how much space is needed
        if page.canvas.x_pages > 10:
            tmp = "00"
        else:
            tmp = "0"
        if page.canvas.y_pages > 10:
            tmp += "00"
        else:
            tmp += "0"

        width = self.doc.string_width(font, '(,)'+tmp)
        width = PT2CM(width)
        self.width = width

        height = font.get_size() * 1.4
        height += 0.5/2.0 * font.get_size() #funny number(s) based upon font.
        self.height = PT2CM(height)

        self.x_cm = self.doc.get_usable_width() - self.width
        self.y_cm = self.doc.get_usable_height() - self.height

    def display(self, page):
        """ If this is the first time I am ran, get my position
        then display the page number """
        if self.text == "":
            self.__calc_position(page)

        self.doc.draw_text(self.boxstr,
                   self.text % (page.x_page_num+1, page.y_page_num+1),
                   self.x_cm, self.y_cm)

class NoteType:
    """  Provide the different options (corners) to place the note """

    TOPLEFT = 0
    TOPRIGHT = 1
    BOTTOMLEFT = 2
    BOTTOMRIGHT = 3

    _DEFAULT = BOTTOMRIGHT

    _DATAMAP = [
        (TOPLEFT,     _("Top Left"),     "Top Left"),
        (TOPRIGHT,    _("Top Right"),    "Top Right"),
        (BOTTOMLEFT,  _("Bottom Left"),  "Bottom Left"),
        (BOTTOMRIGHT, _("Bottom Right"), "Bottom Right"),
        ]

    def __init__(self, value, exclude=None):
        """ initialize GrampsType """
        self.value = value
        self.exclude = exclude
        #GrampsType.__init__(self, value)

    def note_locals(self, start=0):
        """ generates an int of all the options """
        for tuple  in self._DATAMAP:
            if tuple[0] != self.exclude:
                yield tuple[0], tuple[1]

class NoteBox(BoxBase, NoteType):
    """ Box that will hold the note to display on the page """

    def __init__(self, doc, boxstr, box_corner, exclude=None):
        """ initialize the NoteBox """
        BoxBase.__init__(self)
        NoteType.__init__(self, box_corner, exclude)
        self.doc = doc
        self.boxstr = boxstr

    def set_on_page(self, canvas):
        """ set the x_cm and y_cm given
        self.doc, leloffset, and title_height """

        liloffset = canvas.report_opts.littleoffset
        #left or right side
        if self.value == NoteType.BOTTOMLEFT or \
                           self.value == NoteType.TOPLEFT:
            self.x_cm = liloffset
        else:
            self.x_cm = self.doc.get_usable_width() - self.width - liloffset
        #top or bottom
        if self.value == NoteType.TOPRIGHT or \
                           self.value == NoteType.TOPLEFT:
            self.y_cm = canvas.title.height + liloffset*2
        else:
            self.y_cm = self.doc.get_usable_height() - self.height - liloffset

        """ helper function for canvas.paginate().
        return the (x, y) page I want to print on """
        if self.value == NoteType.TOPLEFT:
            return (0, 0)
        elif self.value == NoteType.TOPRIGHT:
            return (canvas.x_pages-1, 0)
        elif self.value == NoteType.BOTTOMLEFT:
            return (0, canvas.y_pages-1)
        elif self.value == NoteType.BOTTOMRIGHT:
            return (canvas.x_pages-1, canvas.y_pages-1)

    def display(self):
        """ position the box and display """
        title = self.page.canvas.title
        title_height = 0
        if title is not None:
            title_height = title.height
        text = '\n'.join(self.text)
        self.doc.draw_box(self.boxstr, text,
           self.x_cm, self.y_cm,
           self.width, self.height)


#------------------------------------------------------------------------
#
# Class Line_base
#
#------------------------------------------------------------------------
class LineBase:
    """ A simple line class.
    self.start is the box that we are drawing a line from
    self.end are the boxes that we are drawing lines to.
    """
    def __init__(self, start):
        #self.linestr = "None"
        self.start = [start]
        self.end = []

    def add_from(self, person):
        self.start.append(person)

    def add_to(self, person):
        """ add destination boxes to draw this line to """
        self.end.append(person)

    def display(self, page):
        """ display the line.  left to right line.  one start, multiple end.
        page will tell us what parts of the line we can print """
        if self.end == [] and len(self.start) == 1:
            return

        # y_cm and x_cm start points - take into account page offsets
        #yme = self.start.y_cm + self.start.height/2 - page.page_y_offset
        #if type(self.start) != type([]):
        #    self.start = [self.start]
        start = self.start[0]
        doc = start.page.canvas.doc
        report_opts = start.page.canvas.report_opts
        linestr = report_opts.line_str

        xbegin = start.x_cm + start.width - page.page_x_offset
        # out 3/4 of the way and x_cm end point(s)
        x34 = xbegin + (report_opts.col_width * 3/4)
        xend = xbegin + report_opts.col_width

        if x34 > 0:  # > 0 tell us we are printing on this page.
            usable_height = doc.get_usable_height()
            #1 - Line from start box out
            for box in self.start:
                yme = box.y_cm + box.height/2 - page.page_y_offset
                if box.page.y_page_num == page.y_page_num:
                    # and 0 < yme < usable_height and \
                    doc.draw_line(linestr, xbegin, yme, x34, yme)

            #2 - vertical line
            mid = []
            for box in self.start + self.end:
                tmp = box.y_cm + box.height/2
                mid.append(tmp)
            mid.sort()
            mid = [mid[0]-page.page_y_offset, mid[-1]-page.page_y_offset]
            if mid[0] < 0:
                mid[0] = 0
            if mid[1] > usable_height:
                mid[1] = usable_height
            #draw the connecting vertical line.
            doc.draw_line(linestr, x34, mid[0], x34, mid[1])
        else:
            x34 = 0

        #3 - horizontal line(s)
        for box in self.end:
            if box.page.y_page_num == page.y_page_num:
                yme = box.y_cm + box.height/2 - box.page.page_y_offset
                doc.draw_line(linestr, x34, yme, xend, yme)


#------------------------------------------------------------------------
#
# Class report_options
#
#------------------------------------------------------------------------
class ReportOptions:
    """
    A simple class to hold various report information
    Calculates
      the gap between persons,
      the column width, for lines,
      the left hand spacing for spouses (Descendant report only)
    """

    def __init__(self, doc, normal_font, normal_line):
        """ initialize various report variables that are used """
        self.box_pgap = PT2CM(1.25*normal_font.get_size()) #gap between persons
        self.box_mgap = self.box_pgap /2 #gap between marriage information
        self.box_shadow = PT2CM(normal_font.get_size()) * .6 #normal text
        self.spouse_offset = PT2CM(doc.string_width(normal_font, "0"))

        self.col_width = PT2CM(doc.string_width(normal_font, "(000,0)"))
        self.littleoffset = PT2CM(1)
        self.x_cm_cols = [self.littleoffset]

        self.line_str = normal_line

        #Things that will get added later
        self.max_box_width = 0
        self.max_box_height = 0

        self.scale = 1

    def scale_everything(self, amount):
        """ Scale the amounts that are needed to generate a report """
        self.scale = amount

        self.col_width *= amount
        self.littleoffset *= amount

        self.max_box_width *= amount  #box_width
        self.spouse_offset *= amount
        self.box_shadow *= amount

#=====================================
#"And Jesus said unto them ... , "If ye have faith as a grain of mustard
#seed, ye shall say unto this mountain, Remove hence to yonder place; and
#it shall remove; and nothing shall be impossible to you."
#Romans 1:17
