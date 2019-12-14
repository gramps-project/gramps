#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008 Brian G. Matherly
# Copyright (C) 2008      Stephane Charette <stephanecharette@gmail.com>
# Contribution 2009 by    Bob Ham <rah@bash.sh>
# Copyright (C) 2010      Jakim Friant
# Copyright (C) 2013-2014 Paul Franklin
# Copyright (C) 2015      Detlef Wolz <detlef.wolz@t-online.de>
# Copyright (C) 2018      Christophe aka khrys63
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
Generate an hourglass graph using the Graphviz generator.
"""
#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
import html

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.errors import ReportError
from gramps.gen.plug.menu import (PersonOption, BooleanOption, NumberOption,
                                  EnumeratedListOption, ColorOption)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.utils.db import get_birth_or_fallback, get_death_or_fallback
from gramps.gen.proxy import CacheProxyDb

#------------------------------------------------------------------------
#
# Constant options items
#
#------------------------------------------------------------------------
_COLORS = [{'name' : _("B&W outline"), 'value' : "outline"},
           {'name' : _("Colored outline"), 'value' : "colored"},
           {'name' : _("Color fill"), 'value' : "filled"}]

_ARROWS = [ { 'name' : _("Center -> Others"),  'value' : 'o' },
            { 'name' : _("Center <- Others"),  'value' : 'c' },
            { 'name' : _("Center <-> Other"), 'value' : 'co' },
            { 'name' : _("Center - Other"),   'value' : '' }]

#------------------------------------------------------------------------
#
# HourGlassReport
#
#------------------------------------------------------------------------
class HourGlassReport(Report):
    """
    An hourglass report displays ancestors and descendants of a center person.
    """
    def __init__(self, database, options, user):
        """
        Create HourGlass object that produces the report.

        name_format   - Preferred format to display names
        incl_private  - Whether to include private data
        inc_id        - Whether to include IDs.
        living_people - How to handle living people
        years_past_death - Consider as living this many years after death
        """
        Report.__init__(self, database, options, user)
        menu = options.menu

        self.set_locale(menu.get_option_by_name('trans').get_value())

        stdoptions.run_date_format_option(self, menu)

        stdoptions.run_private_data_option(self, menu)
        stdoptions.run_living_people_option(self, menu, self._locale)
        self.database = CacheProxyDb(self.database)
        self.__db = self.database

        self.__used_people = []
        self.__family_father = [] # links allocated from family to father
        self.__family_mother = [] # links allocated from family to mother

        self.__node_label = {} # labels of node for merge sosa number

        self.max_descend = menu.get_option_by_name('maxdescend').get_value()
        self.max_ascend = menu.get_option_by_name('maxascend').get_value()
        pid = menu.get_option_by_name('pid').get_value()
        self.center_person = self.__db.get_person_from_gramps_id(pid)
        if self.center_person is None:
            raise ReportError(_("Person %s is not in the Database") % pid)

        self.colorize = menu.get_option_by_name('color').get_value()
        self.colors = {'male': menu.get_option_by_name('colormales').get_value(),
            'female': menu.get_option_by_name('colorfemales').get_value(),
            'unknown': menu.get_option_by_name('colorunknown').get_value(),
            'family': menu.get_option_by_name('colorfamilies').get_value()
        }
        self.roundcorners = menu.get_option_by_name('roundcorners').get_value()

        self.ahnentafel = menu.get_option_by_name('ahnentafel').get_value()

        self.ahnentafelnum = menu.get_option_by_name('ahnentafelnum').get_value()

        self.includeid = menu.get_option_by_name('inc_id').get_value()

        arrow_str = menu.get_option_by_name('arrow').get_value()
        if 'o' in arrow_str:
            self.arrowheadstyle = 'normal'
        else:
            self.arrowheadstyle = 'none'
        if 'c' in arrow_str:
            self.arrowtailstyle = 'normal'
        else:
            self.arrowtailstyle = 'none'

        stdoptions.run_name_format_option(self, menu)

    def write_report(self):
        """
        Generate the report.
        """
        self.add_person(self.center_person, 1)
        self.traverse_up(self.center_person, 1, 1)
        self.traverse_down(self.center_person, 1)

    def traverse_down(self, person, gen):
        """
        Recursively find the descendants of the given person.
        """
        if gen > self.max_descend:
            return
        for family_handle in person.get_family_handle_list():
            family = self.__db.get_family_from_handle(family_handle)
            self.add_family(family)
            self.doc.add_link(person.get_gramps_id(), family.get_gramps_id(),
                               head=self.arrowheadstyle,
                               tail=self.arrowtailstyle)
            for child_ref in family.get_child_ref_list():
                child_handle = child_ref.get_reference_handle()
                if child_handle not in self.__used_people:
                    # Avoid going down paths twice when descendant cousins marry
                    self.__used_people.append(child_handle)
                    child = self.__db.get_person_from_handle(child_handle)
                    self.add_person(child, 0)
                    self.doc.add_link(family.get_gramps_id(),
                                      child.get_gramps_id(),
                                      head=self.arrowheadstyle,
                                      tail=self.arrowtailstyle)
                    self.traverse_down(child, gen+1)

    def traverse_up(self, person, gen, sosanumber):
        """
        Recursively find the ancestors of the given person.
        """
        fathersosanumber = sosanumber * 2
        mothersosanumber = fathersosanumber + 1
        if gen > self.max_ascend:
            return
        family_handle = person.get_main_parents_family_handle()
        person_id=person.get_gramps_id()
        if family_handle:
            family = self.__db.get_family_from_handle(family_handle)
            family_id = family.get_gramps_id()
            self.add_family(family)
            self.doc.add_link(family_id, person_id,
                              head=self.arrowtailstyle,
                              tail=self.arrowheadstyle )
            father_id = ''
            mother_id = ''

            # create link from family to father
            father_handle = family.get_father_handle()
            if father_handle and family_handle not in self.__family_father:
                # allocate only one father per family
                self.__family_father.append(family_handle)
                father = self.__db.get_person_from_handle(father_handle)
                self.add_person(father, fathersosanumber)
                father_id = father.get_gramps_id()
                self.doc.add_link(father.get_gramps_id(), family_id,
                                  head=self.arrowtailstyle,
                                  tail=self.arrowheadstyle )
                # update node with its father node id
                self.__node_label[person_id] = [self.__node_label[person_id][0], father_id, self.__node_label[person_id][2]]
                # no need to go up if he is a father in another family
                if father_handle not in self.__used_people:
                    self.__used_people.append(father_handle)
                    self.traverse_up(father, gen+1, fathersosanumber)
            elif family_handle in self.__family_father and self.ahnentafelnum:
                self.rewrite_sosa_number(self.__db.get_person_from_handle(father_handle).get_gramps_id(), fathersosanumber)

            # create link from family to mother
            mother_handle = family.get_mother_handle()
            if mother_handle and family_handle not in self.__family_mother:
                # allocate only one mother per family
                self.__family_mother.append(family_handle)
                mother = self.__db.get_person_from_handle(mother_handle)
                self.add_person(mother, mothersosanumber)
                mother_id = mother.get_gramps_id()
                self.doc.add_link(mother.get_gramps_id(), family_id,
                                  head=self.arrowtailstyle,
                                  tail=self.arrowheadstyle)
                # update node with its mother node id
                self.__node_label[person_id] = [self.__node_label[person_id][0], self.__node_label[person_id][1], mother_id]
                # no need to go up if she is a mother in another family
                if mother_handle not in self.__used_people:
                    self.__used_people.append(mother_handle)
                    self.traverse_up(mother, gen+1, mothersosanumber)
            elif family_handle in self.__family_mother and self.ahnentafelnum:
                self.rewrite_sosa_number(self.__db.get_person_from_handle(mother_handle).get_gramps_id(), mothersosanumber)

            if self.ahnentafel and mother_handle and father_handle and father_id != '' and mother_id != '':
                self.doc.add_link(father_id, mother_id,
                                  style='invis')
                self.doc.add_samerank(father_id, mother_id)

    def rewrite_sosa_number(self, pid, sosanumber):
        """
        Rewrite the Sosa number of a node for multiple sosa member in the tree.
        """
        self.__node_label[pid][0]+=" - #%s" % (sosanumber)
        self.doc.rewrite_label(pid,self.__node_label[pid][0])

        # Recursively rewrite for all ancestors
        if self.__node_label[pid][1] != '':
            self.rewrite_sosa_number(self.__node_label[pid][1], sosanumber*2)
        if self.__node_label[pid][2] != '':
            self.rewrite_sosa_number(self.__node_label[pid][2], sosanumber*2+1)

    def add_person(self, person, sosanumber):
        """
        Add a person to the Graph. The node id will be the person's gramps id.
        """
        p_id = person.get_gramps_id()
        name = self._name_display.display(person)
        name = html.escape(name)

        birth_evt = get_birth_or_fallback(self.__db, person)
        if birth_evt:
            birth = self.get_date(birth_evt.get_date_object())
        else:
            birth = ""

        death_evt = get_death_or_fallback(self.__db, person)
        if death_evt:
            death = self.get_date(death_evt.get_date_object())
        else:
            death = ""

        if death:
            death = " – %s" % death

        if self.includeid == 0: # no ID
            label = "%s \\n(%s%s)" % (name, birth, death)
        elif self.includeid == 1: # same line
            label = "%s (%s)\\n(%s%s)" % (name, p_id, birth, death)
        elif self.includeid == 2: # own line
            label = "%s \\n(%s%s)\\n(%s)" % (name, birth, death, p_id)

        if self.ahnentafelnum and sosanumber != 0:
            label +="\\n #%s" % (sosanumber)

        label = label.replace('"', '\\\"')

        (shape, style, color, fill) = self.get_gender_style(person)
        self.doc.add_node(p_id, label, shape, color, style, fill)

        # save node with them label, father node id, mother node id and sosanumber
        self.__node_label[p_id] = [label, '', '']

    def add_family(self, family):
        """
        Add a family to the Graph. The node id will be the family's gramps id.
        """
        family_id = family.get_gramps_id()
        label = ""
        marriage = utils.find_marriage(self.__db, family)
        if marriage:
            label = self.get_date(marriage.get_date_object())
        if self.includeid == 1 and label: # same line
            label = "%s (%s)" % (label, family_id)
        elif self.includeid == 1 and not label:
            label = "(%s)" % family_id
        elif self.includeid == 2 and label: # own line
            label = "%s\\n(%s)" % (label, family_id)
        elif self.includeid == 2 and not label:
            label = "(%s)" % family_id
        color = ""
        fill = ""
        style = "solid"
        if self.colorize == 'colored':
            color = self.colors['family']
        elif self.colorize == 'filled':
            fill = self.colors['family']
            style = "filled"
        self.doc.add_node(family_id, label, "ellipse", color, style, fill)

    def get_gender_style(self, person):
        "return gender specific person style"
        gender = person.get_gender()
        shape = "box"
        style = "solid"
        color = ""
        fill = ""

        if gender == person.FEMALE and self.roundcorners:
            style = "rounded"
        elif gender == person.UNKNOWN:
            shape = "hexagon"

        if self.colorize == 'colored':
            if gender == person.MALE:
                color = self.colors['male']
            elif gender == person.FEMALE:
                color = self.colors['female']
            else:
                color = self.colors['unknown']
        elif self.colorize == 'filled':
            style += ",filled"
            if gender == person.MALE:
                fill = self.colors['male']
            elif gender == person.FEMALE:
                fill = self.colors['female']
            else:
                fill = self.colors['unknown']
        return(shape, style, color, fill)
    def get_date(self, date):
        """ return a formatted date """
        return html.escape(self._get_date(date))

#------------------------------------------------------------------------
#
# HourGlassOptions
#
#------------------------------------------------------------------------
class HourGlassOptions(MenuReportOptions):
    """
    Defines options for the HourGlass report.
    """
    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)

    def add_menu_options(self, menu):
        """
        Create all the menu options for this report.
        """
        category_name = _("Report Options")

        pid = PersonOption(_("Center Person"))
        pid.set_help(_("The Center person for the graph"))
        menu.add_option(category_name, "pid", pid)

        max_gen_d = NumberOption(_('Max Descendant Generations'), 10, 1, 15)
        max_gen_d.set_help(_("The number of generations of descendants to "
                           "include in the graph"))
        menu.add_option(category_name, "maxdescend", max_gen_d)

        max_gen_a = NumberOption(_('Max Ancestor Generations'), 10, 1, 15)
        max_gen_a.set_help(_("The number of generations of ancestors to "
                           "include in the graph"))
        menu.add_option(category_name, "maxascend", max_gen_a)

        arrow = EnumeratedListOption(_("Arrowhead direction"), 'o')
        for i in range( 0, len(_ARROWS) ):
            arrow.add_item(_ARROWS[i]["value"], _ARROWS[i]["name"])
        arrow.set_help(_("Choose the direction that the arrows point."))
        menu.add_option(category_name, "arrow", arrow)

        color = EnumeratedListOption(_("Graph coloring"), "filled")
        for i in range(0, len(_COLORS)):
            color.add_item(_COLORS[i]["value"], _COLORS[i]["name"])
        color.set_help(_("Males will be shown with blue, females "
                         "with red.  If the sex of an individual "
                         "is unknown it will be shown with gray."))
        menu.add_option(category_name, "color", color)

        roundedcorners = BooleanOption(_("Use rounded corners"), False) # 2180
        roundedcorners.set_help(
            _("Use rounded corners to differentiate between women and men."))
        menu.add_option(category_name, "roundcorners", roundedcorners)

        stdoptions.add_gramps_id_option(menu, category_name, ownline=True)

        ################################
        category_name = _("Report Options (2)")
        ################################

        stdoptions.add_name_format_option(menu, category_name)

        stdoptions.add_private_data_option(menu, category_name)

        stdoptions.add_living_people_option(menu, category_name)

        locale_opt = stdoptions.add_localization_option(menu, category_name)

        stdoptions.add_date_format_option(menu, category_name, locale_opt)

        ################################
        category_name = _("Graph Style")
        ################################

        color_males = ColorOption(_('Males'), '#e0e0ff')
        color_males.set_help(_('The color to use to display men.'))
        menu.add_option(category_name, 'colormales', color_males)

        color_females = ColorOption(_('Females'), '#ffe0e0')
        color_females.set_help(_('The color to use to display women.'))
        menu.add_option(category_name, 'colorfemales', color_females)

        color_unknown = ColorOption(_('Unknown'), '#e0e0e0')
        color_unknown.set_help(_('The color to use '
                                 'when the gender is unknown.'))
        menu.add_option(category_name, 'colorunknown', color_unknown)

        color_family = ColorOption(_('Families'), '#ffffe0')
        color_family.set_help(_('The color to use to display families.'))
        menu.add_option(category_name, 'colorfamilies', color_family)

        ahnentafelorder = BooleanOption(_("Force Ahnentafel order"), False) # 10826
        ahnentafelorder.set_help(
            _("Force Sosa / Sosa-Stradonitz / Ahnentafel layout order for all ancestors, so that fathers are always on the left branch and mothers are on the right branch."))
        menu.add_option(category_name, "ahnentafel", ahnentafelorder)

        ahnentafelnumvisible = BooleanOption(_("Ahnentafel number visible"), False) # 10826
        ahnentafelnumvisible.set_help(
            _("Show Sosa / Sosa-Stradonitz / Ahnentafel number under all others informations."))
        menu.add_option(category_name, "ahnentafelnum", ahnentafelnumvisible)
