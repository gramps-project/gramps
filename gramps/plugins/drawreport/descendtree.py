#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2007-2012  Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2009-2010  Craig J. Anderson
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

"""
Reports/Graphical Reports/Familial Tree
Reports/Graphical Reports/Personal Tree
"""

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.sgettext
from gramps.gen.errors import ReportError
from gramps.gen.plug.menu import (
    TextOption,
    NumberOption,
    BooleanOption,
    EnumeratedListOption,
    StringOption,
    PersonOption,
    FamilyOption,
)
from gramps.gen.plug.report import Report, MenuReportOptions, stdoptions
from gramps.gen.plug.report import utils
from gramps.gen.plug.docgen import (
    FontStyle,
    ParagraphStyle,
    GraphicsStyle,
    FONT_SANS_SERIF,
    PARA_ALIGN_CENTER,
)
from gramps.plugins.lib.libtreebase import *
from gramps.gen.proxy import CacheProxyDb
from gramps.gen.display.name import displayer as _nd
from gramps.gen.utils.db import family_name

PT2CM = utils.pt2cm

# ------------------------------------------------------------------------
#
# Constants
#
# ------------------------------------------------------------------------
_BORN = (_("b.", "birth abbreviation"),)
_DIED = (_("d.", "death abbreviation"),)
_MARR = (_("m.", "marriage abbreviation"),)

_RPT_NAME = "descend_chart"


# ------------------------------------------------------------------------
#
# Box classes
#
# ------------------------------------------------------------------------
class DescendantBoxBase(BoxBase):
    """
    Base for all descendant boxes.
    Set the boxstr and some new attributes that are needed
    """

    def __init__(self, boxstr):
        BoxBase.__init__(self)
        self.boxstr = boxstr
        self.linked_box = None
        self.father = None

    def calc_text(self, database, person, family):
        """A single place to calculate box text"""

        gui = GuiConnect()
        calc = gui.calc_lines(database)
        self.text = calc.calc_lines(person, family, gui.working_lines(self))


class PersonBox(DescendantBoxBase):
    """
    Calculates information about the box that will print on a page
    """

    def __init__(self, level, boldable=0):
        DescendantBoxBase.__init__(self, "CG2-box")
        self.level = level

    def set_bold(self):
        """update me to a bolded box"""
        self.boxstr = "CG2b-box"


class FamilyBox(DescendantBoxBase):
    """
    Calculates information about the box that will print on a page
    """

    def __init__(self, level):
        DescendantBoxBase.__init__(self, "CG2-fam-box")
        self.level = level


class PlaceHolderBox(BoxBase):
    """
    I am a box that does not print.  I am used to make sure information
    does not run over areas that we don't want information (boxes)
    """

    def __init__(self, level):
        BoxBase.__init__(self)
        self.boxstr = "None"
        self.level = level
        self.line_to = None
        self.linked_box = None

    def calc_text(self, database, person, family):
        """move along.  Nothing to see here"""
        return


# ------------------------------------------------------------------------
#
# Titles Class(es)
#
# ------------------------------------------------------------------------
class DescendantTitleBase(TitleBox):
    def __init__(self, dbase, doc, locale, name_displayer, boxstr="CG2-Title-box"):
        self._nd = name_displayer
        TitleBox.__init__(self, doc, boxstr)
        self.database = dbase
        self._ = locale.translation.sgettext

    def descendant_print(self, person_list, person_list2=[]):
        """calculate the Descendant title
        Person_list will always be passed
        If in the Family reports and there are two families, person_list2
        will be used.
        """

        if len(person_list) == len(person_list2) == 1:
            person_list = person_list + person_list2
            person_list2 = []

        names = self._get_names(person_list, self._nd)

        if person_list2:
            names2 = self._get_names(person_list2, self._nd)
            if len(names) + len(names2) == 3:
                if len(names) == 1:
                    title = self._(
                        "Descendant Chart for %(person)s and "
                        "%(father1)s, %(mother1)s"
                    ) % {
                        "person": names[0],
                        "father1": names2[0],
                        "mother1": names2[1],
                    }
                else:  # Should be 2 items in names list
                    title = self._(
                        "Descendant Chart for %(person)s, "
                        "%(father1)s and %(mother1)s"
                    ) % {
                        "father1": names[0],
                        "mother1": names[1],
                        "person": names2[0],
                    }
            else:  # Should be 2 items in both names and names2 lists
                title = self._(
                    "Descendant Chart for %(father1)s, %(father2)s "
                    "and %(mother1)s, %(mother2)s"
                ) % {
                    "father1": names[0],
                    "mother1": names[1],
                    "father2": names2[0],
                    "mother2": names2[1],
                }
        else:  # No person_list2: Just one family
            if len(names) == 1:
                title = self._("Descendant Chart for %(person)s") % {"person": names[0]}
            else:  # Should be two items in names list
                title = self._("Descendant Chart for %(father)s and " "%(mother)s") % {
                    "father": names[0],
                    "mother": names[1],
                }
        return title

    def get_parents(self, family_id):
        """For a family_id, return the father and mother"""

        family1 = self.database.get_family_from_gramps_id(family_id)
        father_h = family1.get_father_handle()
        mother_h = family1.get_mother_handle()

        parents = [
            self.database.get_person_from_handle(handle)
            for handle in [father_h, mother_h]
            if handle
        ]

        return parents


class TitleNone(TitleNoDisplay):
    """No Title class for the report"""

    def __init__(self, dbase, doc, locale):
        TitleNoDisplay.__init__(self, doc, "CG2-Title-box")
        self._ = locale.translation.sgettext

    def calc_title(self, persons):
        """Calculate the title of the report"""
        # we want no text, but need a text for the TOC in a book!
        self.mark_text = self._("Descendant Graph")
        self.text = ""


class TitleDPY(DescendantTitleBase):
    """Descendant (Person yes start with parents) Chart
    Title class for the report"""

    def __init__(self, dbase, doc, locale, name_displayer):
        DescendantTitleBase.__init__(self, dbase, doc, locale, name_displayer)

    def calc_title(self, person_id):
        """Calculate the title of the report"""

        center = self.database.get_person_from_gramps_id(person_id)
        family2_h = center.get_main_parents_family_handle()
        if family2_h:
            family2 = self.database.get_family_from_handle(family2_h)
        else:
            family2 = None

        person_list = None
        if family2:
            father2_h = family2.get_father_handle()
            mother2_h = family2.get_mother_handle()
            person_list = [
                self.database.get_person_from_handle(handle)
                for handle in [father2_h, mother2_h]
                if handle
            ]

        if not person_list:
            person_list = [center]

        self.text = self.descendant_print(person_list)
        self.set_box_height_width()


class TitleDPN(DescendantTitleBase):
    """Descendant (Person no start with parents) Chart
    Title class for the report"""

    def __init__(self, dbase, doc, locale, name_displayer):
        DescendantTitleBase.__init__(self, dbase, doc, locale, name_displayer)

    def calc_title(self, person_id):
        """Calculate the title of the report"""

        center = self.database.get_person_from_gramps_id(person_id)

        title = self.descendant_print([center])
        self.text = title
        self.set_box_height_width()


class TitleDFY(DescendantTitleBase):
    """Descendant (Family yes start with parents) Chart
    Title class for the report"""

    def __init__(self, dbase, doc, locale, name_displayer):
        DescendantTitleBase.__init__(self, dbase, doc, locale, name_displayer)

    def get_parent_list(self, person):
        """return a list of my parents.  If none, return me"""
        if not person:
            return None

        parent_list = None
        family_h = person.get_main_parents_family_handle()
        if family_h:
            family = self.database.get_family_from_handle(family_h)
        else:
            family = None
        if family:  # family = fathers parents
            father_h = family.get_father_handle()
            mother_h = family.get_mother_handle()
            parent_list = [
                self.database.get_person_from_handle(handle)
                for handle in [father_h, mother_h]
                if handle
            ]

        return parent_list or [person]

    def calc_title(self, family_id):
        """Calculate the title of the report"""

        my_parents = self.get_parents(family_id)

        dad_parents = self.get_parent_list(my_parents[0])

        mom_parents = []
        if len(my_parents) > 1:
            if not dad_parents:
                dad_parents = self.get_parent_list(my_parents[1])
            else:
                mom_parents = self.get_parent_list(my_parents[1])

        self.text = self.descendant_print(dad_parents, mom_parents)
        self.set_box_height_width()


class TitleDFN(DescendantTitleBase):
    """Descendant (Family no start with parents) Chart
    Title class for the report"""

    def __init__(self, dbase, doc, locale, name_displayer):
        DescendantTitleBase.__init__(self, dbase, doc, locale, name_displayer)

    def calc_title(self, family_id):
        """Calculate the title of the report"""

        self.text = self.descendant_print(self.get_parents(family_id))
        self.set_box_height_width()


class TitleF(DescendantTitleBase):
    """Family Chart Title class for the report"""

    def __init__(self, dbase, doc, locale, name_displayer):
        DescendantTitleBase.__init__(self, dbase, doc, locale, name_displayer)

    def calc_title(self, family_id):
        """Calculate the title of the report"""
        parents = self.get_parents(family_id)

        names = self._get_names(parents, self._nd)

        if len(parents) == 1:
            title = self._("Family Chart for %(person)s") % {"person": names[0]}
        elif len(parents) == 2:
            title = self._("Family Chart for %(father1)s and %(mother1)s") % {
                "father1": names[0],
                "mother1": names[1],
            }
        # else:
        #    title = str(tmp) + " " + str(len(tmp))
        self.text = title
        self.set_box_height_width()


class TitleC(DescendantTitleBase):
    """Cousin Chart Title class for the report"""

    def __init__(self, dbase, doc, locale, name_displayer):
        DescendantTitleBase.__init__(self, dbase, doc, locale, name_displayer)

    def calc_title(self, family_id):
        """Calculate the title of the report"""

        family = self.database.get_family_from_gramps_id(family_id)

        kids = [
            self.database.get_person_from_handle(kid.ref)
            for kid in family.get_child_ref_list()
        ]

        # ok we have the children.  Make a title off of them
        # Translators: needed for Arabic, ignore otherwise
        cousin_names = self._(", ").join(self._get_names(kids, self._nd))

        self.text = self._("Cousin Chart for %(names)s") % {"names": cousin_names}

        self.set_box_height_width()


# ------------------------------------------------------------------------
#
# Class RecurseDown
#
# ------------------------------------------------------------------------
class RecurseDown:
    """
    The main recursive functions that will use add_person to make
    the tree of people (Descendants) to be included within the report.
    """

    def __init__(self, dbase, canvas):
        self.database = dbase
        self.canvas = canvas

        self.families_seen = set()
        self.cols = []
        self.__last_direct = []

        gui = GuiConnect()
        self.do_parents = gui.get_val("show_parents")
        self.max_generations = gui.get_val("maxgen")
        self.max_spouses = gui.get_val("maxspouse")
        self.inlc_marr = gui.get_val("inc_marr")
        if not self.max_spouses:
            self.inlc_marr = False
        self.spouse_indent = gui.get_val("ind_spouse")

        # is the option even available?
        self.bold_direct = gui.get_val("bolddirect")
        # can we bold direct descendants?
        # bold_now will have only three values
        # 0 - no bolding
        # 1 - Only bold the first person
        # 2 - Bold all direct descendants
        self.bold_now = 0
        gui = None

    def add_to_col(self, box):
        """
        Add the box to a column on the canvas.  we will do these things:
          set the .linked_box attrib for the boxs in this col
          get the height and width of this box and set it no the column
          also we set the .x_cm to any s_level (indentation) here
            we will calculate the real .x_cm later (with indentation)
        """

        level = box.level[0]
        # make the column list of people
        while len(self.cols) <= level:
            self.cols.append(None)
            self.__last_direct.append(None)

        if self.cols[level]:  # if (not the first box in this column)
            last_box = self.cols[level]
            last_box.linked_box = box

            # calculate the .y_cm for this box.
            box.y_cm = last_box.y_cm
            box.y_cm += last_box.height
            if last_box.boxstr in ["CG2-box", "CG2b-box"]:
                box.y_cm += self.canvas.report_opts.box_shadow

            if box.boxstr in ["CG2-box", "CG2b-box"]:
                box.y_cm += self.canvas.report_opts.box_pgap
            else:
                box.y_cm += self.canvas.report_opts.box_mgap

            if box.level[1] == 0 and self.__last_direct[level]:
                # ok, a new direct descendant.
                # print level, box.father is not None, \
                # self.__last_direct[level].father is not None, box.text[0], \
                # self.__last_direct[level].text[0]
                if (
                    box.father != self.__last_direct[level].father
                    and box.father != self.__last_direct[level]
                ):
                    box.y_cm += self.canvas.report_opts.box_pgap

        self.cols[level] = box
        if box.level[1] == 0:
            self.__last_direct[level] = box

        if self.spouse_indent:
            box.x_cm = self.canvas.report_opts.spouse_offset * box.level[1]
        else:
            box.x_cm = 0.0

        self.canvas.set_box_height_width(box)

    def add_person_box(self, level, indi_handle, fams_handle, father):
        """Makes a person box and add that person into the Canvas."""
        myself = PersonBox(level)
        myself.father = father

        if myself.level[1] == 0 and self.bold_direct and self.bold_now:
            if self.bold_now == 1:
                self.bold_now = 0
            myself.set_bold()

        if level[1] == 0 and father and myself.level[0] != father.level[0]:
            # I am a child
            if father.line_to:
                line = father.line_to
            else:
                line = LineBase(father)
                father.line_to = line
                # self.canvas.add_line(line)

            line.end.append(myself)

        # calculate the text.
        myself.calc_text(self.database, indi_handle, fams_handle)

        if indi_handle:
            myself.add_mark(
                self.database, self.database.get_person_from_handle(indi_handle)
            )

        self.add_to_col(myself)

        self.canvas.add_box(myself)

        return myself

    def add_marriage_box(self, level, indi_handle, fams_handle, father):
        """Makes a marriage box and add that person into the Canvas."""
        myself = FamilyBox(level)

        # if father is not None:
        #    myself.father = father
        # calculate the text.
        myself.calc_text(self.database, indi_handle, fams_handle)

        self.add_to_col(myself)

        self.canvas.add_box(myself)

        return myself

    def recurse(self, person_handle, x_level, s_level, father):
        """traverse the ancestors recursively until
        either the end of a line is found,
        or until we reach the maximum number of generations
        or we reach the max number of spouses
        that we want to deal with"""

        if not person_handle:
            return
        if x_level > self.max_generations:
            return
        if s_level > 0 and s_level == self.max_spouses:
            return
        if person_handle in self.families_seen:
            return

        myself = None
        person = self.database.get_person_from_handle(person_handle)
        family_handles = person.get_family_handle_list()
        if s_level == 0:
            val = family_handles[0] if family_handles else None
            myself = self.add_person_box((x_level, s_level), person_handle, val, father)

        marr = None
        spouse = None

        if s_level == 1:
            tmp_bold = self.bold_now
            self.bold_now = 0

        for family_handle in family_handles:
            if family_handle not in self.families_seen:
                self.families_seen.add(family_handle)

                family = self.database.get_family_from_handle(family_handle)

                # Marriage box if the option is there.
                if self.inlc_marr and self.max_spouses > 0:
                    marr = self.add_marriage_box(
                        (x_level, s_level + 1),
                        person_handle,
                        family_handle,
                        father if s_level else myself,
                    )

                spouse_handle = utils.find_spouse(person, family)
                if (
                    self.max_spouses > s_level
                    and spouse_handle not in self.families_seen
                ):

                    def _spouse_box(who):
                        return self.add_person_box(
                            (x_level, s_level + 1), spouse_handle, family_handle, who
                        )

                    if s_level > 0:
                        spouse = _spouse_box(father)
                    elif self.inlc_marr:
                        spouse = _spouse_box(marr)
                    else:
                        spouse = _spouse_box(myself)

                mykids = [kid.ref for kid in family.get_child_ref_list()]

                def _child_recurse(who):
                    self.recurse(child_ref, x_level + 1, 0, who)

                for child_ref in mykids:
                    if self.inlc_marr and self.max_spouses > 0:
                        _child_recurse(marr)
                    elif spouse:
                        _child_recurse(spouse)
                    else:
                        _child_recurse(myself)

                if (
                    self.max_spouses > s_level
                    and spouse_handle not in self.families_seen
                ):
                    # spouse_handle = utils.find_spouse(person,family)
                    self.recurse(spouse_handle, x_level, s_level + 1, spouse)

        if s_level == 1:
            self.bold_now = tmp_bold

    def add_family(self, level, family, father2):
        """
        Adds a family into the canvas.
        only will be used for my direct grandparents, and my parents only.
        """

        family_h = family.get_handle()
        father_h = family.get_father_handle()
        mother_h = family.get_mother_handle()

        self.bold_now = 2
        if father_h:
            father_b = self.add_person_box((level, 0), father_h, family_h, father2)
        else:
            father_b = self.add_person_box((level, 0), None, None, father2)
        retrn = [father_b]

        if self.inlc_marr:
            family_b = self.add_marriage_box((level, 1), father_h, family_h, father_b)
            retrn.append(family_b)
        self.families_seen.add(family_h)

        if mother_h:
            mother_b = self.add_person_box((level, 0), mother_h, family_h, father_b)
        else:
            mother_b = self.add_person_box((level, 0), None, None, father_b)
        retrn.append(mother_b)

        family_line = family_b if self.inlc_marr else father_b
        for child_ref in family.get_child_ref_list():
            self.recurse(child_ref.ref, level + 1, 0, family_line)

        self.bold_now = 0

        # Set up the lines for the family
        if not family_line.line_to:
            # no children.
            family_line.line_to = LineBase(family_line)
        if self.inlc_marr:
            family_line.line_to.start.append(father_b)
        family_line.line_to.start.append(mother_b)

        return retrn

    def has_children(self, person_handle):
        """
        Quickly check to see if this person has children
        still we want to respect the FamiliesSeen list
        """

        if not person_handle or person_handle in self.families_seen:
            return False

        person = self.database.get_person_from_handle(person_handle)

        for family_handle in person.get_family_handle_list():
            if family_handle not in self.families_seen:
                family = self.database.get_family_from_handle(family_handle)

                if family.get_child_ref_list():
                    return True
        return False

    def recurse_if(self, person_handle, level):
        """
        Quickly check to see if we want to continue recursion
        still we want to respect the FamiliesSeen list
        """

        person = self.database.get_person_from_handle(person_handle)

        show = False
        myfams = person.get_family_handle_list()
        if len(myfams) > 1:  # and self.max_spouses > 0
            show = True
            if not self.inlc_marr:
                # if the condition is true, we only want to show
                # this parent again IF s/he has other children
                show = self.has_children(person_handle)

        # if self.max_spouses == 0 and not self.has_children(person_handle):
        #    self.families_seen.add(person_handle)
        #    show = False

        if show:
            self.bold_now = 1
            self.recurse(person_handle, level, 0, None)


# ------------------------------------------------------------------------
#
# Class MakePersonTree (Personal Descendant Tree option)
#
# ------------------------------------------------------------------------
class MakePersonTree(RecurseDown):
    """
    The main procedure to use recursion to make the tree based off of a person.
    order of people inserted into Persons is important.
    makes sure that order is done correctly.
    """

    def __init__(self, dbase, canvas):
        RecurseDown.__init__(self, dbase, canvas)
        self.max_generations -= 1

    def start(self, person_id):
        """follow the steps to make a tree off of a person"""
        persons = []

        center1 = self.database.get_person_from_gramps_id(person_id)
        if center1 is None:
            raise ReportError(_("Person %s is not in the Database") % person_id)
        center1_h = center1.get_handle()  # could be mom too.

        family2 = family2_h = None
        if self.do_parents:
            family2_h = center1.get_main_parents_family_handle()
            if family2_h:
                family2 = self.database.get_family_from_handle(family2_h)

        mother2_h = father2_h = None
        if family2:
            father2_h = family2.get_father_handle()
            mother2_h = family2.get_mother_handle()

        #######################
        # don't do center person's parents family.
        if family2_h:
            self.families_seen.add(family2_h)

        #######################
        # Center person's Fathers OTHER wives
        #######################
        # update to only run if he HAD other wives!
        if father2_h:
            self.recurse_if(father2_h, 0)

        #######################
        # Center persons parents only!
        #######################
        # now it will ONLY be my fathers parents
        if family2:
            self.add_family(0, family2, None)
        else:
            self.bold_now = 2
            self.recurse(center1_h, 0, 0, None)
        self.bold_now = 0

        #######################
        # Center person's mothers OTHER husbands
        #######################
        # update to only run if she HAD other husbands!
        if mother2_h:
            self.recurse_if(mother2_h, 0)

        return persons


# ------------------------------------------------------------------------
#
# Class MakeFamilyTree (Familial Descendant Tree option)
#
# ------------------------------------------------------------------------
class MakeFamilyTree(RecurseDown):
    """
    The main procedure to use recursion to make the tree based off of a family.
    order of people inserted into Persons is important.
    makes sure that order is done correctly.
    """

    def __init__(self, dbase, canvas):
        RecurseDown.__init__(self, dbase, canvas)

    def start(self, family_id):
        """follow the steps to make a tree off of a family"""
        ## (my) referes to the children of family_id
        # Step 1 print out my fathers, fathers,
        # other wives families first (if needed)
        family1 = self.database.get_family_from_gramps_id(family_id)
        if family1 is None:
            raise ReportError(_("Family %s is not in the Database") % family_id)
        family1_h = family1.get_handle()

        #######################
        # Initial setup of variables
        #######################
        father1_h = family1.get_father_handle()
        mother1_h = family1.get_mother_handle()

        father1 = mother1 = family2 = family2_h = None
        if father1_h:
            father1 = self.database.get_person_from_handle(father1_h)
            if self.do_parents:  # b3 - remove grandparents?
                family2_h = father1.get_main_parents_family_handle()
                if family2_h:
                    family2 = self.database.get_family_from_handle(family2_h)
        if mother1_h:
            mother1 = self.database.get_person_from_handle(mother1_h)

        mother2_h = father2_h = father2 = mother2 = None
        if family2:  # family2 = fathers parents
            mother2_h = family2.get_mother_handle()
            if mother2_h:
                mother2 = self.database.get_person_from_handle(mother2_h)
            father2_h = family2.get_father_handle()
            if father2_h:
                father2 = self.database.get_person_from_handle(father2_h)

        # Helper variables.  Assigned in one section, used in another.
        father2_id = family2_id = None
        mother1_id = None

        #######################
        # don't do my fathers parents family.  will be done later
        if family2_h:
            self.families_seen.add(family2_h)

        #######################
        # my father mothers OTHER husbands
        #######################
        # update to only run if she HAD other husbands!
        if mother2_h:
            self.recurse_if(mother2_h, 0)

        #######################
        # father Fathers OTHER wives
        #######################
        # update to only run if he HAD other wives!
        if father2_h:
            self.recurse_if(father2_h, 0)

        #######################
        # don't do my parents family in recurse.  will be done later
        self.families_seen.add(family1_h)
        ##If dad has no other children from other marriages.  remove him
        if self.max_spouses == 0 and not self.has_children(father1_h):
            self.families_seen.add(father1_h)

        #######################
        # my fathers parents!
        #######################
        # now it will ONLY be my fathers parents
        # will print dads parents.  dad's other wifes will also print
        if family2:
            myfams = father1.get_family_handle_list()
            show = False
            if len(myfams) > 1:
                show = True
                if not self.inlc_marr and self.max_spouses == 0:
                    # if the condition is true, we only want to show
                    # this parent again IF s/he has children
                    show = self.has_children(father1_h)
            if not show:
                self.families_seen.add(father1_h)

            family2_l = self.add_family(0, family2, None)

        elif father1:
            #######################
            # my father other wives (if all of the above does nothing)
            # if my father does not have parents (he is the highest)
            #######################
            # do his OTHER wives first.
            self.recurse_if(father1_h, 1)

        #######################
        # my father, marriage info, mother, siblings, me
        #######################
        if family2:
            # We need to add dad to the family
            family2_line = family2_l[1] if self.inlc_marr else family2_l[0]
        else:
            family2_line = None

        family1_l = self.add_family(1, family1, family2_line)
        mother1_b = family1_l[-1]  # Mom's Box

        # make sure there is at least one child in this family.
        # if not put in a placeholder
        family1_line = family1_l[1] if self.inlc_marr else family1_l[0]
        if family1_line.line_to.end == []:
            box = PlaceHolderBox((mother1_b.level[0] + 1, 0))
            box.father = family1_l[0]
            self.add_to_col(box)
            family1_line.line_to.end = [box]

        #######################
        #######################
        # Lower half
        # This will be quite like the first half.
        # Just on the mothers side...
        # Mom has already been printed with the family
        #######################
        #######################

        #######################
        # Initial setup of variables
        #######################
        mother1_h = family1.get_mother_handle()
        family2_h = mother1 = family2 = None
        if mother1_h:
            mother1 = self.database.get_person_from_handle(mother1_h)
            if self.do_parents:  # b3 - remove grandparents?
                family2_h = mother1.get_main_parents_family_handle()
                if family2_h:
                    family2 = self.database.get_family_from_handle(family2_h)

        mother2_h = father2_h = mother2 = father2 = None
        if family2:
            mother2_h = family2.get_mother_handle()
            if mother2_h:
                mother2 = self.database.get_person_from_handle(mother2_h)
            father2_h = family2.get_father_handle()
            if father2_h:
                father2 = self.database.get_person_from_handle(father2_h)

        #######################
        # don't do my parents family.
        self.families_seen = set([family1_h])
        ##If mom has no other children from other marriages.  remove her
        if self.max_spouses == 0 and not self.has_children(mother1_h):
            self.families_seen.add(mother1_h)

        if mother1_h:
            myfams = mother1.get_family_handle_list()
            if len(myfams) < 2:
                # If mom didn't have any other families, don't even do her
                # she is already here with dad and will be added later
                self.families_seen.add(mother1_h)

        #######################
        # my mother other spouses (if no parents)
        #######################
        # if my mother does not have parents (she is the highest)
        # Then do her OTHER spouses.
        if not family2 and mother1:
            self.recurse_if(mother1_h, 1)

        #######################
        # my mothers parents!
        #######################
        if family2:
            family2_l = self.add_family(0, family2, None)
            family2_line = family2_l[1] if self.inlc_marr else family2_l[0]

            family2_line = family2_line.line_to
            if family2_line.end != []:
                family2_line.end.insert(0, mother1_b)
            else:
                family2_line.end = [mother1_b]

            # fix me.  Moms other siblings have been given an extra space
            # Because Moms-father is not siblings-father right now.

            mother1_b.father = family2_line

        #######################
        # my mother mothers OTHER husbands
        #######################
        # update to only run if she HAD other husbands!
        if mother2_h:
            self.recurse_if(mother2_h, 0)

        #######################
        # mother Fathers OTHER wives
        #######################
        # update to only run if he HAD other wives!
        if father2_h:
            self.recurse_if(father2_h, 0)


# ------------------------------------------------------------------------
#
# Class MakeReport
#
# ------------------------------------------------------------------------
class MakeReport:
    """
    Make a report out of a list of people.
    The list of people is already made.  Use this information to find where
    people will be placed on the canvas.
    """

    def __init__(self, dbase, canvas, ind_spouse, compress_tree):
        self.database = dbase
        self.canvas = canvas

        gui = GuiConnect()
        self.do_parents = gui.get_val("show_parents")
        self.inlc_marr = gui.get_val("inc_marr")
        self.max_spouses = gui.get_val("maxspouse")
        gui = None

        self.ind_spouse = ind_spouse
        self.compress_tree = compress_tree
        self.cols = [[]]
        # self.max_generations = 0

    # already done in recurse,
    # Some of this code needs to be moved up to RecurseDown.add_to_col()
    def calc_box(self, box):
        """calculate the max_box_width and max_box_height for the report"""
        width = box.x_cm + box.width
        if width > self.canvas.report_opts.max_box_width:
            self.canvas.report_opts.max_box_width = width

        if box.height > self.canvas.report_opts.max_box_height:
            self.canvas.report_opts.max_box_height = box.height

        while len(self.cols) <= box.level[0]:
            self.cols.append([])

        self.cols[box.level[0]].append(box)

        # tmp = box.level[0]
        # if tmp > self.max_generations:
        #    self.max_generations = tmp

    def __move_col_from_here_down(self, box, amount):
        """Move me and everyone below me in this column only down"""
        while box:
            box.y_cm += amount
            box = box.linked_box

    def __move_next_cols_from_here_down(self, box, amount):
        """Move me, everyone below me in this column,
        and all of our children (and childrens children) down."""
        col = [box]
        while col:
            if len(col) == 1 and col[0].line_to:
                col.append(col[0].line_to.end[0])

            col[0].y_cm += amount

            col[0] = col[0].linked_box
            if col[0] is None:
                col.pop(0)

    def __next_family_group(self, box):
        """a helper function.  Assume box is at the start of a family block.
        get this family block."""
        while box:
            left_group = []
            line = None

            # Form the parental (left) group.
            # am I a direct descendant?
            if box.level[1] == 0:
                # I am the father/mother.
                left_group.append(box)
                if box.line_to:
                    line = box.line_to
                box = box.linked_box

            if box and box.level[1] != 0 and self.inlc_marr:
                # add/start with the marriage box
                left_group.append(box)
                if box.line_to:
                    line = box.line_to
                box = box.linked_box

            if box and box.level[1] != 0 and self.max_spouses > 0:
                # add/start with the spousal box
                left_group.append(box)
                if box.line_to:
                    line = box.line_to
                box = box.linked_box

            if line:
                if len(line.start) > 1 and line.start[-1].level[1] == 0:
                    # a dad and mom family from RecurseDown.add_family. add mom
                    left_group.append(line.start[-1])
                    box = box.linked_box

                # we now have everyone we want
                return left_group, line.end
            # else
            #  no children, so no family.  go again until we find one to return.

        return None, None

    def __reverse_family_group(self):
        """go through the n-1 to 0 cols of boxes looking for families
        (parents with children) that may need to be moved."""
        for col in reversed(self.cols):
            box = col[0]  # The first person in this col
            while box:
                left_group, right_group = self.__next_family_group(box)
                if not left_group:
                    box = None  # we found the end of this col
                else:
                    yield left_group, right_group
                    box = left_group[-1].linked_box

    def __calc_movements(self, left_group, right_group):
        """for a family group, see if parents or children need to be
        moved down so everyone is to the right/left of each other.

        return a right y_cm and a left y_cm.  these points will be used
        to move parents/children down.
        """
        left_up = left_group[0].y_cm
        right_up = right_group[0].y_cm

        left_center = left_up
        right_center = right_up

        if self.compress_tree:
            # calculate a new left and right move points
            for left_line in left_group:
                if left_line.line_to:
                    break
            left_center = left_line.y_cm + (left_line.height / 2)

            left_down = left_group[-1].y_cm + left_group[-1].height
            right_down = right_group[-1].y_cm + right_group[-1].height

            # Lazy.  Move down either side only as much as we NEED to.
            if left_center < right_up:
                right_center = right_group[0].y_cm
            elif left_up == right_up:
                left_center = left_up  # Lets keep it.  top line.
            elif left_center > right_down:
                right_center = right_down
            else:
                right_center = left_center

        return right_center, left_center

    def Make_report(self):
        """
        Everyone on the page is as far up as they can go.
        Move them down to where they belong.

        We are going to go through everyone from right to left
        top to bottom moving everyone down as needed to make the report.
        """
        seen_parents = False

        for left_group, right_group in self.__reverse_family_group():
            right_y_cm, left_y_cm = self.__calc_movements(left_group, right_group)

            # 1.  Are my children too high?  if so move then down!
            if right_y_cm < left_y_cm:
                # we have to push our kids (and their kids) down.
                # We also need to push down all the kids (under)
                # these kids (in their column)
                amt = left_y_cm - right_y_cm
                self.__move_next_cols_from_here_down(right_group[0], amt)

            # 2.  Am I (and spouses) too high?  if so move us down!
            elif left_y_cm < right_y_cm:
                # Ok, I am too high.  Move me down
                amt = right_y_cm - left_y_cm
                self.__move_col_from_here_down(left_group[0], amt)

            # 6. now check to see if we are working with dad and mom.
            # if so we need to move down marriage information
            # and mom!
            left_line = left_group[0].line_to
            if not left_line:
                left_line = left_group[1].line_to
            # left_line = left_line.start

            if len(left_line.start) > 1 and not seen_parents:
                # only do Dad and Mom.  len(left_line) > 1
                seen_parents = True

                mom_cm = left_group[-1].y_cm + left_group[-1].height / 2
                last_child_cm = right_group[-1].y_cm
                if not self.compress_tree:
                    last_child_cm += right_group[-1].height / 2
                move_amt = last_child_cm - mom_cm

                # if the moms height is less than the last childs height
                # The 0.2 is to see if this is even worth it.
                if move_amt > 0.2:
                    # our children take up more space than us parents.
                    # so space mom out!
                    self.__move_col_from_here_down(left_group[-1], move_amt)

                    # move marriage info
                    if self.inlc_marr:
                        left_group[1].y_cm += move_amt / 2

                if left_line.end[0].boxstr == "None":
                    left_line.end = []

    def start(self):
        """Make the report"""
        # for person in self.persons.depth_first_gen():
        for box in self.canvas.boxes:
            self.calc_box(box)
        # At this point we know everything we need to make the report.
        # Width of each column of people - self.rept_opt.box_width
        # width of each column (or row) of lines - self.rept_opt.col_width

        if not self.cols[0]:
            # We wanted to print parents of starting person/family but
            # there were none!
            # remove column 0 and move everyone back one level
            self.cols.pop(0)
            for box in self.canvas.boxes:
                box.level = (box.level[0] - 1, box.level[1])

        # go ahead and set it now.
        width = self.canvas.report_opts.max_box_width
        for box in self.canvas.boxes:
            box.width = width - box.x_cm
            box.x_cm += self.canvas.report_opts.littleoffset
            box.x_cm += box.level[0] * (
                self.canvas.report_opts.col_width
                + self.canvas.report_opts.max_box_width
            )

            box.y_cm += self.canvas.report_opts.littleoffset
            box.y_cm += self.canvas.title.height

        self.Make_report()


class GuiConnect:
    """This is a BORG object.  There is ONLY one.
    This give some common routines that EVERYONE can use like
      get the value from a GUI variable
    """

    __shared_state = {}

    def __init__(self):  # We are BORG!
        self.__dict__ = self.__shared_state

    def set__opts(self, options, which, locale, name_displayer):
        self._opts = options
        self._which_report = which.split(",")[0]
        self._locale = locale
        self._nd = name_displayer

    def get_val(self, val):
        """Get a GUI value."""
        value = self._opts.get_option_by_name(val)
        if value:
            return value.get_value()
        else:
            False

    def Title_class(self, database, doc):
        Title_type = self.get_val("report_title")
        if Title_type == 0:  # None
            return TitleNone(database, doc, self._locale)

        if Title_type == 1:  # Descendant Chart
            if self._which_report == _RPT_NAME:
                if self.get_val("show_parents"):
                    return TitleDPY(database, doc, self._locale, self._nd)
                else:
                    return TitleDPN(database, doc, self._locale, self._nd)
            else:
                if self.get_val("show_parents"):
                    return TitleDFY(database, doc, self._locale, self._nd)
                else:
                    return TitleDFN(database, doc, self._locale, self._nd)

        if Title_type == 2:
            return TitleF(database, doc, self._locale, self._nd)
        else:  # Title_type == 3
            return TitleC(database, doc, self._locale, self._nd)

    def Make_Tree(self, database, canvas):
        if self._which_report == _RPT_NAME:
            return MakePersonTree(database, canvas)
        else:
            return MakeFamilyTree(database, canvas)

    def calc_lines(self, database):
        # calculate the printed lines for each box
        display_repl = self.get_val("replace_list")
        # str = ""
        # if self.get_val('miss_val'):
        #    str = "_____"
        return CalcLines(database, display_repl, self._locale, self._nd)

    def working_lines(self, box):
        display = self.get_val("descend_disp")
        # if self.get_val('diffspouse'):
        display_spou = self.get_val("spouse_disp")
        # else:
        #    display_spou = display
        display_marr = [self.get_val("marr_disp")]

        if box.boxstr == "CG2-fam-box":  # (((((
            workinglines = display_marr
        elif box.level[1] > 0 or (box.level[0] == 0 and box.father):
            workinglines = display_spou
        else:
            workinglines = display
        return workinglines


# ------------------------------------------------------------------------
#
# DescendTree
#
# ------------------------------------------------------------------------
class DescendTree(Report):
    def __init__(self, database, options, user):
        """
        Create DescendTree object that produces the report.
        The arguments are:

        database        - the Gramps database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        incl_private    - Whether to include private data
        living_people - How to handle living people
        years_past_death - Consider as living this many years after death
        """
        Report.__init__(self, database, options, user)

        self.options = options

        self.set_locale(options.menu.get_option_by_name("trans").get_value())
        stdoptions.run_date_format_option(self, options.menu)
        stdoptions.run_private_data_option(self, options.menu)
        stdoptions.run_living_people_option(self, options.menu, self._locale)
        self.database = CacheProxyDb(self.database)
        stdoptions.run_name_format_option(self, options.menu)
        self._nd = self._name_display

    def begin_report(self):
        """make the report in its full size and pages to print on
        scale one or both as needed/desired.
        """

        database = self.database

        self.Connect = GuiConnect()
        self.Connect.set__opts(
            self.options.menu, self.options.name, self._locale, self._nd
        )

        style_sheet = self.doc.get_style_sheet()
        font_normal = style_sheet.get_paragraph_style("CG2-Normal").get_font()

        # The canvas that we will put our report on and print off of
        self.canvas = Canvas(self.doc, ReportOptions(self.doc, font_normal, "CG2-line"))

        self.canvas.report_opts.box_shadow *= self.Connect.get_val("shadowscale")
        self.canvas.report_opts.box_pgap *= self.Connect.get_val("box_Yscale")
        self.canvas.report_opts.box_mgap *= self.Connect.get_val("box_Yscale")

        center_id = self.Connect.get_val("pid")

        # make the tree
        tree = self.Connect.Make_Tree(database, self.canvas)
        tree.start(center_id)
        tree = None

        # Title
        title = self.Connect.Title_class(database, self.doc)
        title.calc_title(center_id)
        self.canvas.add_title(title)

        # make the report as big as it wants to be.
        ind_spouse = self.Connect.get_val("ind_spouse")
        compress_tree = self.Connect.get_val("compress_tree")
        report = MakeReport(database, self.canvas, ind_spouse, compress_tree)
        report.start()
        report = None

        # note?
        if self.Connect.get_val("inc_note"):
            note_box = NoteBox(
                self.doc, "CG2-note-box", self.Connect.get_val("note_place")
            )
            subst = SubstKeywords(self.database, self._locale, self._nd, None, None)
            note_box.text = subst.replace_and_clean(self.Connect.get_val("note_disp"))
            self.canvas.add_note(note_box)

        # Now we have the report in its full size.
        # Do we want to scale the report?
        one_page = self.Connect.get_val("resize_page")
        scale_report = self.Connect.get_val("scale_tree")

        scale = self.canvas.scale_report(one_page, scale_report != 0, scale_report == 2)

        if scale != 1 or self.Connect.get_val("shadowscale") != 1.0:
            self.scale_styles(scale)

    def write_report(self):
        """Canvas now has everyone ready to print.  Get some misc stuff
        together and print."""

        one_page = self.Connect.get_val("resize_page")
        scale_report = self.Connect.get_val("scale_tree")

        # Inlc_marr = self.Connect.get_val("inc_marr")
        inc_border = self.Connect.get_val("inc_border")
        incblank = self.Connect.get_val("inc_blank")
        prnnum = self.Connect.get_val("inc_pagenum")
        # ind_spouse = self.Connect.get_val("ind_spouse")
        lines = self.Connect.get_val("note_disp")

        #####################
        # Setup page information

        colsperpage = self.doc.get_usable_width()
        colsperpage += self.canvas.report_opts.col_width
        tmp = self.canvas.report_opts.max_box_width
        tmp += self.canvas.report_opts.col_width
        colsperpage = int(colsperpage / tmp)
        colsperpage = colsperpage or 1

        #####################
        # Vars
        # p = self.doc.get_style_sheet().get_paragraph_style("CG2-Normal")
        # font = p.get_font()
        if prnnum:
            page_num_box = PageNumberBox(self.doc, "CG2-box", self._locale)

        #####################
        # ok, everyone is now ready to print on the canvas.  Paginate?
        self.canvas.sort_boxes_on_y_cm()
        self.canvas.paginate(colsperpage, one_page)

        #####################
        # Yeah!!!
        # lets finally make some pages!!!
        #####################
        for page in self.canvas.page_iter_gen(incblank):
            self.doc.start_page()

            # do we need to print a border?
            if inc_border:
                page.draw_border("CG2-line")

            # Do we need to print the page number?
            if prnnum:
                page_num_box.display(page)

            page.display()

            self.doc.end_page()

    def scale_styles(self, amount):
        """
        Scale the styles for this report. This must be done in the constructor.
        """
        style_sheet = self.doc.get_style_sheet()

        graph_style = style_sheet.get_draw_style("CG2-fam-box")
        graph_style.set_shadow(graph_style.get_shadow(), 0)
        graph_style.set_line_width(graph_style.get_line_width() * amount)
        style_sheet.add_draw_style("CG2-fam-box", graph_style)

        graph_style = style_sheet.get_draw_style("CG2-box")
        graph_style.set_shadow(
            graph_style.get_shadow(), self.canvas.report_opts.box_shadow * amount
        )
        graph_style.set_line_width(graph_style.get_line_width() * amount)
        style_sheet.add_draw_style("CG2-box", graph_style)

        graph_style = style_sheet.get_draw_style("CG2b-box")
        graph_style.set_shadow(
            graph_style.get_shadow(), self.canvas.report_opts.box_shadow * amount
        )
        graph_style.set_line_width(graph_style.get_line_width() * amount)
        style_sheet.add_draw_style("CG2b-box", graph_style)

        graph_style = style_sheet.get_draw_style("CG2-note-box")
        graph_style.set_shadow(graph_style.get_shadow(), 0)
        graph_style.set_line_width(graph_style.get_line_width() * amount)
        style_sheet.add_draw_style("CG2-note-box", graph_style)

        para_style = style_sheet.get_paragraph_style("CG2-Title")
        font = para_style.get_font()
        font.set_size(font.get_size() * amount)
        para_style.set_font(font)
        style_sheet.add_paragraph_style("CG2-Title", para_style)

        para_style = style_sheet.get_paragraph_style("CG2-Normal")
        font = para_style.get_font()
        font.set_size(font.get_size() * amount)
        para_style.set_font(font)
        style_sheet.add_paragraph_style("CG2-Normal", para_style)

        para_style = style_sheet.get_paragraph_style("CG2-Bold")
        font = para_style.get_font()
        font.set_bold(True)
        font.set_size(font.get_size() * amount)
        para_style.set_font(font)
        style_sheet.add_paragraph_style("CG2-Bold", para_style)

        para_style = style_sheet.get_paragraph_style("CG2-Note")
        font = para_style.get_font()
        font.set_size(font.get_size() * amount)
        para_style.set_font(font)
        style_sheet.add_paragraph_style("CG2-Note", para_style)

        self.doc.set_style_sheet(style_sheet)


# ------------------------------------------------------------------------
#
# DescendTreeOptions
#
# ------------------------------------------------------------------------
class DescendTreeOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        self.__pid = None
        self.__onepage = None
        self.__inc_title = None
        self.__title = None
        self.__blank = None
        self.scale = None
        self.__db = dbase
        self.name = name
        self.box_Y_sf = None
        self.box_shadow_sf = None
        MenuReportOptions.__init__(self, name, dbase)

    def get_subject(self):
        """Return a string that describes the subject of the report."""
        gid = self.__pid.get_value()
        if self.name.split(",")[0] == _RPT_NAME:
            person = self.__db.get_person_from_gramps_id(gid)
            if person:
                return _nd.display(person)
        else:
            family = self.__db.get_family_from_gramps_id(gid)
            if family:
                return family_name(family, self.__db)
        return ""

    def add_menu_options(self, menu):
        """
        Add options to the menu for the descendant report.
        """
        ##################
        category_name = _("Tree Options")

        if self.name.split(",")[0] == _RPT_NAME:
            self.__pid = PersonOption(_("Report for"))
            self.__pid.set_help(_("The main person for the report"))
            menu.add_option(category_name, "pid", self.__pid)
        else:  # if self.name == "familial_descend_tree":
            self.__pid = FamilyOption(_("Report for"))
            self.__pid.set_help(_("The main family for the report"))
            menu.add_option(category_name, "pid", self.__pid)

        max_gen = NumberOption(_("Generations"), 10, 1, 50)
        max_gen.set_help(_("The number of generations to include in the tree"))
        menu.add_option(category_name, "maxgen", max_gen)

        max_spouse = NumberOption(_("Level of Spouses"), 1, 0, 10)
        max_spouse.set_help(
            _(
                "0=no Spouses, 1=include Spouses, 2=include "
                "Spouses of the spouse, etc"
            )
        )
        menu.add_option(category_name, "maxspouse", max_spouse)

        self.showparents = BooleanOption(
            _("Start with the parent(s) of the selected first"), False
        )
        self.showparents.set_help(
            _("Will show the parents, brother and sisters of the " "selected person.")
        )
        menu.add_option(category_name, "show_parents", self.showparents)

        compresst = BooleanOption(_("Compress tree"), False)
        compresst.set_help(
            _(
                "Whether to move people up, where possible, "
                "resulting in a smaller tree"
            )
        )
        menu.add_option(category_name, "compress_tree", compresst)

        bold = BooleanOption(_("Bold direct descendants"), True)
        bold.set_help(
            _(
                "Whether to bold those people that are direct "
                "(not step or half) descendants."
            )
        )
        menu.add_option(category_name, "bolddirect", bold)

        indspouce = BooleanOption(_("Indent Spouses"), True)
        indspouce.set_help(_("Whether to indent the spouses in the tree."))
        menu.add_option(category_name, "ind_spouse", indspouce)

        ##################
        category_name = _("Report Options")

        self.title = EnumeratedListOption(_("Report Title"), 0)
        self.title.add_item(0, _("Do not include a title"))
        self.title.add_item(1, _("Descendant Chart for [selected person(s)]"))
        if self.name.split(",")[0] != _RPT_NAME:
            self.title.add_item(2, _("Family Chart for [names of chosen family]"))
            if self.showparents.get_value():
                self.title.add_item(3, _("Cousin Chart for [names of children]"))
        self.title.set_help(_("Choose a title for the report"))
        menu.add_option(category_name, "report_title", self.title)
        self.showparents.connect("value-changed", self.__Title_enum)

        border = BooleanOption(_("Include a border"), False)
        border.set_help(_("Whether to make a border around the report."))
        menu.add_option(category_name, "inc_border", border)

        prnnum = BooleanOption(_("Include Page Numbers"), False)
        prnnum.set_help(_("Whether to include page numbers on each page."))
        menu.add_option(category_name, "inc_pagenum", prnnum)

        self.scale = EnumeratedListOption(_("Scale tree to fit"), 0)
        self.scale.add_item(0, _("Do not scale tree"))
        self.scale.add_item(1, _("Scale tree to fit page width only"))
        self.scale.add_item(2, _("Scale tree to fit the size of the page"))
        self.scale.set_help(_("Whether to scale the tree to fit a specific paper size"))
        menu.add_option(category_name, "scale_tree", self.scale)
        self.scale.connect("value-changed", self.__check_blank)

        if "BKI" not in self.name.split(","):
            self.__onepage = BooleanOption(
                _(
                    "Resize Page to Fit Tree size\n"
                    "\n"
                    "Note: Overrides options in the 'Paper Option' tab"
                ),
                False,
            )
            self.__onepage.set_help(
                _(
                    "Whether to resize the page to fit the size \n"
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
                )
            )
            menu.add_option(category_name, "resize_page", self.__onepage)
            self.__onepage.connect("value-changed", self.__check_blank)
        else:
            self.__onepage = None

        self.__blank = BooleanOption(_("Include Blank Pages"), True)
        self.__blank.set_help(_("Whether to include pages that are blank."))
        menu.add_option(category_name, "inc_blank", self.__blank)

        ##################
        category_name = _("Report Options (2)")

        stdoptions.add_name_format_option(menu, category_name)

        stdoptions.add_private_data_option(menu, category_name)

        stdoptions.add_living_people_option(menu, category_name)

        locale_opt = stdoptions.add_localization_option(menu, category_name)

        stdoptions.add_date_format_option(menu, category_name, locale_opt)

        ##################
        category_name = _("Display")

        disp = TextOption(
            _("Descendant\nDisplay Format"), ["$n", "%s $b" % _BORN, "-{%s $d}" % _DIED]
        )
        disp.set_help(_("Display format for a descendant."))
        menu.add_option(category_name, "descend_disp", disp)

        # bug 4767
        # diffspouse = BooleanOption(
        #    _("Use separate display format for spouses"),
        #    True)
        # diffspouse.set_help(_("Whether spouses can have a different format."))
        # menu.add_option(category_name, "diffspouse", diffspouse)

        sdisp = TextOption(
            _("Spousal\nDisplay Format"), ["$n", "%s $b" % _BORN, "-{%s $d}" % _DIED]
        )
        sdisp.set_help(_("Display format for a spouse."))
        menu.add_option(category_name, "spouse_disp", sdisp)

        self.incmarr = BooleanOption(_("Include Marriage box"), True)
        self.incmarr.set_help(
            _("Whether to include a separate marital box in the report")
        )
        menu.add_option(category_name, "inc_marr", self.incmarr)
        self.incmarr.connect("value-changed", self._incmarr_changed)

        self.marrdisp = StringOption(_("Marriage\nDisplay Format"), "%s $m" % _MARR)
        self.marrdisp.set_help(_("Display format for the marital box."))
        menu.add_option(category_name, "marr_disp", self.marrdisp)
        self._incmarr_changed()

        ##################
        category_name = _("Advanced")

        repldisp = TextOption(
            _("Replace Display Format:\n'Replace this'/' with this'"), []
        )
        repldisp.set_help(_("i.e.\nUnited States of America/U.S.A."))
        menu.add_option(category_name, "replace_list", repldisp)

        self.usenote = BooleanOption(_("Include a note"), False)
        self.usenote.set_help(_("Whether to include a note on the report."))
        menu.add_option(category_name, "inc_note", self.usenote)
        self.usenote.connect("value-changed", self._usenote_changed)

        self.notedisp = TextOption(_("Note"), [])
        self.notedisp.set_help(_("Add a note\n\n" "$T inserts today's date"))
        menu.add_option(category_name, "note_disp", self.notedisp)

        locales = NoteType(0)
        self.notelocal = EnumeratedListOption(_("Note Location"), 2)
        for num, text in locales.note_locals():
            self.notelocal.add_item(num, text)
        self.notelocal.set_help(_("Where to place the note."))
        menu.add_option(category_name, "note_place", self.notelocal)
        self._usenote_changed()

        self.box_Y_sf = NumberOption(
            _("inter-box Y scale factor"), 1.00, 0.10, 2.00, 0.01
        )
        self.box_Y_sf.set_help(_("Make the inter-box Y bigger or smaller"))
        menu.add_option(category_name, "box_Yscale", self.box_Y_sf)

        self.box_shadow_sf = NumberOption(
            _("box shadow scale factor"), 1.00, 0.00, 2.00, 0.01
        )  # down to 0
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
        """dis/enables the 'print blank pages' checkbox"""
        if self.__onepage:
            value = not self.__onepage.get_value()
        else:
            value = True
        off = value and (self.scale.get_value() != 2)
        self.__blank.set_available(off)

    def __Title_enum(self):
        item_list = [
            [0, _("Do not include a title")],
            [1, _("Descendant Chart for [selected person(s)]")],
        ]
        if self.name.split(",")[0] != _RPT_NAME:
            item_list.append([2, _("Family Chart for [names of chosen family]")])
            if self.showparents.get_value():
                item_list.append([3, _("Cousin Chart for [names of children]")])
        self.title.set_items(item_list)

    def make_default_style(self, default_style):
        """Make the default output style for the Descendant Tree."""

        ## Paragraph Styles:
        font = FontStyle()
        font.set_size(16)
        font.set_type_face(FONT_SANS_SERIF)
        para_style = ParagraphStyle()
        para_style.set_font(font)
        para_style.set_alignment(PARA_ALIGN_CENTER)
        para_style.set_description(_("The style used for the title."))
        default_style.add_paragraph_style("CG2-Title", para_style)

        font = FontStyle()
        font.set_size(9)
        font.set_type_face(FONT_SANS_SERIF)
        para_style = ParagraphStyle()
        para_style.set_font(font)
        para_style.set_description(_("The basic style used for the text display."))
        default_style.add_paragraph_style("CG2-Normal", para_style)

        # Set the size of the shadow based on the font size!  Much better
        # will be set later too.
        box_shadow = PT2CM(font.get_size()) * 0.6

        font.set_bold(True)
        para_style = ParagraphStyle()
        para_style.set_font(font)
        para_style.set_description(_("The bold style used for the text display."))
        default_style.add_paragraph_style("CG2-Bold", para_style)

        font = FontStyle()
        font.set_size(9)
        font.set_type_face(FONT_SANS_SERIF)
        para_style = ParagraphStyle()
        para_style.set_font(font)
        para_style.set_description(_("The basic style used for the note display."))
        default_style.add_paragraph_style("CG2-Note", para_style)

        # TODO this seems meaningless, as only the text is displayed
        graph_style = GraphicsStyle()
        graph_style.set_paragraph_style("CG2-Title")
        graph_style.set_color((0, 0, 0))
        graph_style.set_fill_color((255, 255, 255))
        graph_style.set_line_width(0)
        graph_style.set_description(_("Cannot edit this reference"))
        default_style.add_draw_style("CG2-Title-box", graph_style)

        ## Draw styles
        graph_style = GraphicsStyle()
        graph_style.set_paragraph_style("CG2-Normal")
        graph_style.set_fill_color((255, 255, 255))
        graph_style.set_description(_("The style for the marriage box."))
        default_style.add_draw_style("CG2-fam-box", graph_style)

        graph_style = GraphicsStyle()
        graph_style.set_paragraph_style("CG2-Normal")
        graph_style.set_shadow(1, box_shadow)
        graph_style.set_fill_color((255, 255, 255))
        graph_style.set_description(_("The style for the spouse box."))
        default_style.add_draw_style("CG2-box", graph_style)

        graph_style = GraphicsStyle()
        graph_style.set_paragraph_style("CG2-Bold")
        graph_style.set_shadow(1, box_shadow)
        graph_style.set_fill_color((255, 255, 255))
        graph_style.set_description(_("The style for the direct descendant box."))
        default_style.add_draw_style("CG2b-box", graph_style)

        graph_style = GraphicsStyle()
        graph_style.set_paragraph_style("CG2-Note")
        graph_style.set_fill_color((255, 255, 255))
        graph_style.set_description(_("The style for the note box."))
        default_style.add_draw_style("CG2-note-box", graph_style)

        graph_style = GraphicsStyle()
        graph_style.set_description(
            _("The style for the connection lines and report border.")
        )
        default_style.add_draw_style("CG2-line", graph_style)
