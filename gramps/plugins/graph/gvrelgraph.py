#
# Gramps - a GTK+/GNOME based genealogy program
#
# Adapted from Graphviz.py (now deprecated)
#    Copyright (C) 2000-2007  Donald N. Allingham
#    Copyright (C) 2005-2006  Eero Tamminen
#    Copyright (C) 2007-2008  Brian G. Matherly
#    Copyright (C) 2007       Johan Gonqvist <johan.gronqvist@gmail.com>
#    Contributions by Lorenzo Cappelletti <lorenzo.cappelletti@email.it>
#    Copyright (C) 2008       Stephane Charette <stephanecharette@gmail.com>
#    Copyright (C) 2009       Gary Burton
#    Contribution 2009 by     Bob Ham <rah@bash.sh>
#    Copyright (C) 2010       Jakim Friant
#    Copyright (C) 2013       Fedir Zinchuk <fedikw@gmail.com>
#    Copyright (C) 2013-2015  Paul Franklin
#    Copyright (C) 2015       Fabrice <fobrice@laposte.net>
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
Create a relationship graph using Graphviz
"""

#------------------------------------------------------------------------
#
# python modules
#
#------------------------------------------------------------------------
from functools import partial
import html

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
from gramps.gen.plug.menu import (BooleanOption, EnumeratedListOption,
                                  FilterOption, PersonOption, ColorOption)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.gen.lib import ChildRefType, EventRoleType, EventType, Date
from gramps.gen.utils.file import media_path_full, find_file
from gramps.gen.utils.thumbnails import get_thumbnail_path
from gramps.gen.relationship import get_relationship_calculator
from gramps.gen.utils.db import (get_birth_or_fallback, get_death_or_fallback,
                                 find_parents)
from gramps.gen.display.place import displayer as _pd
from gramps.gen.proxy import CacheProxyDb
from gramps.gen.errors import ReportError

#------------------------------------------------------------------------
#
# Constant options items
#
#------------------------------------------------------------------------
_COLORS = [{'name' : _("B&W outline"),     'value' : 'outlined'},
           {'name' : _("Colored outline"), 'value' : 'colored'},
           {'name' : _("Color fill"),      'value' : 'filled'}]

_ARROWS = [{'name' : _("Descendants <- Ancestors"),  'value' : 'd'},
           {'name' : _("Descendants -> Ancestors"),  'value' : 'a'},
           {'name' : _("Descendants <-> Ancestors"), 'value' : 'da'},
           {'name' : _("Descendants - Ancestors"),   'value' : ''}]

#------------------------------------------------------------------------
#
# RelGraphReport class
#
#------------------------------------------------------------------------
class RelGraphReport(Report):

    def __init__(self, database, options, user):
        """
        Create RelGraphReport object that produces the report.

        The arguments are:

        database        - the Gramps database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        This report needs the following parameters (class variables)
        that come in the options class.

        filter     - Filter to be applied to the people of the database.
                     The option class carries its number, and the function
                     returning the list of filters.
        arrow      - Arrow styles for heads and tails.
        showfamily - Whether to show family nodes.
        inc_id     - Whether to include IDs.
        url        - Whether to include URLs.
        inclimg    - Include images or not
        imgpos     - Image position, above/beside name
        color      - Whether to use outline, colored outline or filled color
                     in graph
        color_males    - Colour to apply to males
        color_females  - Colour to apply to females
        color_unknown  - Colour to apply to unknown genders
        color_families - Colour to apply to families
        dashed         - Whether to use dashed lines for non-birth relationships
        use_roundedcorners - Whether to use rounded corners for females
        use_hexagons   - Whether to use hexagons for individuals of unknown gender
        name_format    - Preferred format to display names
        incl_private   - Whether to include private data
        event_choice   - Whether to include dates and/or places
        occupation     - Whether to include occupations
        living_people - How to handle living people
        years_past_death - Consider as living this many years after death
        """
        Report.__init__(self, database, options, user)

        menu = options.menu
        get_option_by_name = options.menu.get_option_by_name
        get_value = lambda name: get_option_by_name(name).get_value()

        self.set_locale(menu.get_option_by_name('trans').get_value())

        stdoptions.run_date_format_option(self, menu)

        stdoptions.run_private_data_option(self, menu)
        stdoptions.run_living_people_option(self, menu, self._locale)
        self.database = CacheProxyDb(self.database)
        self._db = self.database

        self.includeid = get_value('inc_id')
        self.includeurl = get_value('url')
        self.includeimg = get_value('includeImages')
        self.imgpos = get_value('imageOnTheSide')
        self.use_roundedcorners = get_value('useroundedcorners')
        self.use_hexagons = get_value('usehexagons')
        self.adoptionsdashed = get_value('dashed')
        self.show_families = get_value('showfamily')
        self.show_family_leaves = get_value('show_family_leaves')
        self.use_subgraphs = get_value('usesubgraphs')
        self.event_choice = get_value('event_choice')
        self.occupation = get_value('occupation')
        self.use_html_output = False

        self.colorize = get_value('color')
        color_males = get_value('colormales')
        color_females = get_value('colorfemales')
        color_unknown = get_value('colorunknown')
        color_families = get_value('colorfamilies')
        self.colors = {
            'male': color_males,
            'female': color_females,
            'unknown': color_unknown,
            'family': color_families
        }

        arrow_str = get_value('arrow')
        if 'd' in arrow_str:
            self.arrowheadstyle = 'normal'
        else:
            self.arrowheadstyle = 'none'
        if 'a' in arrow_str:
            self.arrowtailstyle = 'normal'
        else:
            self.arrowtailstyle = 'none'
        filter_option = get_option_by_name('filter')
        self._filter = filter_option.get_filter()

        stdoptions.run_name_format_option(self, menu)

        pid = get_value('pid')
        self.center_person = self._db.get_person_from_gramps_id(pid)
        if self.center_person is None:
            raise ReportError(_("Person %s is not in the Database") % pid)

        self.increlname = get_value('increlname')
        if self.increlname:
            self.rel_calc = get_relationship_calculator(reinit=True,
                                                        clocale=self._locale)

        if __debug__:
            self.advrelinfo = get_value('advrelinfo')
        else:
            self.advrelinfo = False

    def write_report(self):
        person_handles = self._filter.apply(self._db,
                                            self._db.iter_person_handles(),
                                            user=self._user)
        # Hash people in a dictionary for faster inclusion checking
        self.persons = set(person_handles)

        person_handles = self.sort_persons(person_handles)

        if len(person_handles) > 1:
            if self._user:
                self._user.begin_progress(_("Relationship Graph"),
                                          _("Generating report"),
                                          len(person_handles) * 2)
            self.add_persons_and_families(person_handles)
            self.add_child_links_to_families(person_handles)
            if self._user:
                self._user.end_progress()

    def sort_persons(self, person_handle_list):
        "sort persons by close relations"

        # first make a list of all persons who don't have any parents
        root_nodes = list()
        for person_handle in person_handle_list:
            person = self.database.get_person_from_handle(person_handle)
            has_parent = False
            for parent_handle in find_parents(self.database, person):
                if parent_handle not in self.persons:
                    continue
                has_parent = True
            if not has_parent:
                root_nodes.append(person_handle)

        # now start from all root nodes we found and traverse their trees
        outlist = list()
        p_done = set()
        for person_handle in root_nodes:
            todolist = list()
            todolist.append(person_handle)
            while len(todolist) > 0:
                # take the first person from todolist and do sanity check
                cur = todolist.pop(0)
                if cur in p_done:
                    continue
                if cur not in self.persons:
                    p_done.add(cur)
                    continue
                person = self.database.get_person_from_handle(cur)

                # first check whether both parents are added
                missing_parents = False
                for parent_handle in find_parents(self.database, person):
                    if not parent_handle or parent_handle in p_done:
                        continue
                    if parent_handle not in self.persons:
                        continue
                    todolist.insert(0, parent_handle)
                    missing_parents = True

                # if one of the parents is still missing, wait for them
                if missing_parents:
                    continue

                # add person to the sorted output
                outlist.append(cur)
                p_done.add(cur)

                # add all spouses and children to the todo list
                family_list = person.get_family_handle_list()
                for fam_handle in family_list:
                    family = self.database.get_family_from_handle(fam_handle)
                    if family is None:
                        continue
                    if (family.get_father_handle() and
                            family.get_father_handle() != cur):
                        todolist.insert(0, family.get_father_handle())
                    if (family.get_mother_handle() and
                            family.get_mother_handle() != cur):
                        todolist.insert(0, family.get_mother_handle())
                    for child_ref in family.get_child_ref_list():
                        todolist.append(child_ref.ref)

        # finally store the result
        assert len(person_handle_list) == len(outlist)
        return outlist

    def add_child_links_to_families(self, person_handles):
        """
        returns string of Graphviz edges linking parents to families or
        children
        """
        for person_handle in person_handles:
            if self._user:
                self._user.step_progress()
            person = self._db.get_person_from_handle(person_handle)
            p_id = person.get_gramps_id()
            for fam_handle in person.get_parent_family_handle_list():
                family = self._db.get_family_from_handle(fam_handle)
                father_handle = family.get_father_handle()
                mother_handle = family.get_mother_handle()
                sibling = False
                for child_ref in family.get_child_ref_list():
                    if child_ref.ref == person_handle:
                        frel = child_ref.frel
                        mrel = child_ref.mrel
                    elif child_ref.ref in self.persons:
                        sibling = True
                if (self.show_families and
                    ((father_handle and father_handle in self.persons) or
                     (mother_handle and mother_handle in self.persons) or
                     sibling)):
                    # Link to the family node if either parent is in graph
                    self.add_family_link(p_id, family, frel, mrel)
                else:
                    # Link to the parents' nodes directly, if they are in graph
                    if father_handle and father_handle in self.persons:
                        self.add_parent_link(p_id, father_handle, frel)
                    if mother_handle and mother_handle in self.persons:
                        self.add_parent_link(p_id, mother_handle, mrel)

    def add_family_link(self, p_id, family, frel, mrel):
        "Links the child to a family"
        style = 'solid'
        adopted = ((int(frel) != ChildRefType.BIRTH) or
                   (int(mrel) != ChildRefType.BIRTH))
        # If birth relation to father is NONE, meaning there is no father and
        # if birth relation to mother is BIRTH then solid line
        if (int(frel) == ChildRefType.NONE and
                int(mrel) == ChildRefType.BIRTH):
            adopted = False
        if adopted and self.adoptionsdashed:
            style = 'dotted'
        self.doc.add_link(family.get_gramps_id(), p_id, style,
                          self.arrowheadstyle, self.arrowtailstyle)

    def add_parent_link(self, p_id, parent_handle, rel):
        "Links the child to a parent"
        style = 'solid'
        if (int(rel) != ChildRefType.BIRTH) and self.adoptionsdashed:
            style = 'dotted'
        parent = self._db.get_person_from_handle(parent_handle)
        self.doc.add_link(parent.get_gramps_id(), p_id, style,
                          self.arrowheadstyle, self.arrowtailstyle)

    def add_persons_and_families(self, person_handles):
        "adds nodes for persons and their families"
        # variable to communicate with get_person_label
        self.use_html_output = False

        # The list of families for which we have output the node,
        # so we don't do it twice
        families_done = set()
        for person_handle in person_handles:
            if self._user:
                self._user.step_progress()
            # determine per person if we use HTML style label
            if self.includeimg:
                self.use_html_output = True
            person = self._db.get_person_from_handle(person_handle)
            if person is None:
                continue
            p_id = person.get_gramps_id()
            # Output the person's node
            label = self.get_person_label(person)
            (shape, style, color, fill) = self.get_gender_style(person)
            url = ""
            if self.includeurl:
                phan = person_handle
                dirpath = "ppl/%s/%s" % (phan[-1], phan[-2])
                dirpath = dirpath.lower()
                url = "%s/%s.html" % (dirpath, phan)

            self.doc.add_node(p_id, label, shape, color, style, fill, url)

            # Output families where person is a parent
            if self.show_families:
                family_list = person.get_family_handle_list()
                for fam_handle in family_list:
                    family = self._db.get_family_from_handle(fam_handle)
                    if family is None:
                        continue
                    if fam_handle not in families_done:
                        if not self.show_family_leaves:
                            family_members = {family.father_handle, family.mother_handle}.union(
                                child_ref.ref for child_ref in family.child_ref_list) - {None}
                            if len(family_members.intersection(person_handles)) < 2:
                                continue
                        self.__add_family(fam_handle)
                        families_done.add(fam_handle)
                    # If subgraphs are not chosen then each parent is linked
                    # separately to the family. This gives Graphviz greater
                    # control over the layout of the whole graph but
                    # may leave spouses not positioned together.
                    if not self.use_subgraphs and fam_handle in families_done:
                        self.doc.add_link(p_id, family.get_gramps_id(), "",
                                          self.arrowheadstyle,
                                          self.arrowtailstyle)

                # Output families where person is a sibling if another sibling
                # is present
                family_list = person.get_parent_family_handle_list()
                for fam_handle in family_list:
                    if fam_handle in families_done:
                        continue
                    family = self.database.get_family_from_handle(fam_handle)
                    if family is None:
                        continue
                    for child_ref in family.get_child_ref_list():
                        if (child_ref.ref != person_handle and
                                child_ref.ref in self.persons):
                            families_done.add(fam_handle)
                            self.__add_family(fam_handle)

    def __add_family(self, fam_handle):
        """Add a node for a family and optionally link the spouses to it"""
        fam = self._db.get_family_from_handle(fam_handle)
        if fam is None:
            return
        fam_id = fam.get_gramps_id()

        m_type = m_date = m_place = ""
        d_type = d_date = d_place = ""
        for event_ref in fam.get_event_ref_list():
            event = self._db.get_event_from_handle(event_ref.ref)
            if event is None:
                continue
            if (event.type == EventType.MARRIAGE and
                    (event_ref.get_role() == EventRoleType.FAMILY or
                     event_ref.get_role() == EventRoleType.PRIMARY)):
                m_type = event.type
                m_date = self.get_date_string(event)
                if not (self.event_choice == 3 and m_date):
                    m_place = self.get_place_string(event)
                break
            if (event.type == EventType.DIVORCE and
                    (event_ref.get_role() == EventRoleType.FAMILY or
                     event_ref.get_role() == EventRoleType.PRIMARY)):
                d_type = event.type
                d_date = self.get_date_string(event)
                if not (self.event_choice == 3 and d_date):
                    d_place = self.get_place_string(event)
                break

        labellines = list()
        if self.includeid == 2:
            # id on separate line
            labellines.append("(%s)" % fam_id)
        if self.event_choice == 7:
            if m_type:
                line = m_type.get_abbreviation()
                if m_date:
                    line += ' %s' % m_date
                if m_date and m_place:
                    labellines.append(line)
                    line = ''
                if m_place:
                    line += ' %s' % m_place
                labellines.append(line)
            if d_type:
                line = d_type.get_abbreviation()
                if d_date:
                    line += ' %s' % d_date
                if d_date and d_place:
                    labellines.append(line)
                    line = ''
                if d_place:
                    line += ' %s' % d_place
                labellines.append(line)
        else:
            if m_date:
                labellines.append("(%s)" % m_date)
            if m_place:
                labellines.append("(%s)" % m_place)

        label = "\\n".join(labellines)
        labellines = list()
        if self.includeid == 1:
            # id on same line
            labellines.append("(%s)" % fam_id)
        if len(label):
            labellines.append(label)
        label = ' '.join(labellines)

        color = ""
        fill = ""
        style = "solid"
        if self.colorize == 'colored':
            color = self.colors['family']
        elif self.colorize == 'filled':
            fill = self.colors['family']
            style = "filled"
        self.doc.add_node(fam_id, label, "ellipse", color, style, fill)

        # If subgraphs are used then we add both spouses here and Graphviz
        # will attempt to position both spouses closely together.
        # TODO: A person who is a parent in more than one family may only be
        #       positioned next to one of their spouses. The code currently
        #       does not take into account multiple spouses.
        if self.use_subgraphs:
            self.doc.start_subgraph(fam_id)
            f_handle = fam.get_father_handle()
            m_handle = fam.get_mother_handle()
            if f_handle and m_handle:
                father = self._db.get_person_from_handle(f_handle)
                mother = self._db.get_person_from_handle(m_handle)
                fcount = 0
                mcount = 0
                family_list = father.get_parent_family_handle_list()
                for fam_handle in family_list:
                    family = self._db.get_family_from_handle(fam_handle)
                    if family is not None:
                        fcount = fcount + 1
                family_list = mother.get_parent_family_handle_list()
                for fam_handle in family_list:
                    family = self._db.get_family_from_handle(fam_handle)
                    if family is not None:
                        mcount = mcount + 1
                first = father
                second = mother
                if fcount < mcount:
                    first = mother
                    second = father
                self.doc.add_link(first.get_gramps_id(),
                                  second.get_gramps_id(),
                                  "invis",
                                  "none",
                                  "none")
            if f_handle in self.persons:
                father = self._db.get_person_from_handle(f_handle)
                self.doc.add_link(father.get_gramps_id(),
                                  fam_id, "",
                                  self.arrowheadstyle,
                                  self.arrowtailstyle)
            if m_handle in self.persons:
                mother = self._db.get_person_from_handle(m_handle)
                self.doc.add_link(mother.get_gramps_id(),
                                  fam_id, "",
                                  self.arrowheadstyle,
                                  self.arrowtailstyle)
            self.doc.end_subgraph()

    def get_gender_style(self, person):
        "return gender specific person style"
        gender = person.get_gender()
        shape = "box"
        style = "solid"
        color = ""
        fill = ""

        if gender == person.FEMALE and self.use_roundedcorners:
            style = "rounded"
        elif gender == person.UNKNOWN and self.use_hexagons:
            shape = "hexagon"

        if person == self.center_person and self.increlname:
            shape = "octagon"

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

    def get_person_label(self, person):
        "return person label string"
        # see if we have an image to use for this person
        image_path = None
        if self.use_html_output:
            media_list = person.get_media_list()
            if len(media_list) > 0:
                media_handle = media_list[0].get_reference_handle()
                media = self._db.get_media_from_handle(media_handle)
                media_mime_type = media.get_mime_type()
                if media_mime_type[0:5] == "image":
                    image_path = get_thumbnail_path(
                        media_path_full(self._db, media.get_path()),
                        rectangle=media_list[0].get_rectangle())
                    # test if thumbnail actually exists in thumbs
                    # (import of data means media files might not be present
                    image_path = find_file(image_path)

        label = ""
        line_delimiter = '\\n'

        # If we have an image, then start an HTML table; remember to close
        # the table afterwards!
        #
        # This isn't a free-form HTML format here...just a few keywords that
        # happen to be
        # similar to keywords commonly seen in HTML.  For additional
        # information on what
        # is allowed, see:
        #
        #       http://www.graphviz.org/info/shapes.html#html
        #
        if self.use_html_output and image_path:
            line_delimiter = '<BR/>'
            label += '<TABLE BORDER="0" CELLSPACING="2" CELLPADDING="0" '
            label += 'CELLBORDER="0"><TR><TD></TD><TD>'
            label += '<IMG SRC="%s"/></TD><TD></TD>' % image_path
            if self.imgpos == 0:
                #trick it into not stretching the image
                label += '</TR><TR><TD COLSPAN="3">'
            else:
                label += '<TD>'
        else:
            #no need for html label with this person
            self.use_html_output = False

        # at the very least, the label must have the person's name
        p_name = self._name_display.display(person)
        label += html.escape(p_name)
        p_id = person.get_gramps_id()
        if self.includeid == 1: # same line
            label += " (%s)" % p_id
        elif self.includeid == 2: # own line
            label += "%s(%s)" % (line_delimiter, p_id)
        if self.event_choice != 0:
            b_date, d_date, b_place, d_place, b_type, d_type = \
                self.get_event_strings(person)
            if self.event_choice in [1, 2, 3, 4, 5] and (b_date or d_date):
                label += '%s(' % line_delimiter
                if b_date:
                    label += '%s' % b_date
                label += ' – '
                if d_date:
                    label += '%s' % d_date
                label += ')'
            if (self.event_choice in [2, 3, 5, 6] and
                    (b_place or d_place) and
                    not (self.event_choice == 3 and (b_date or d_date))
               ):
                label += '%s(' % line_delimiter
                if b_place:
                    label += '%s' % b_place
                label += ' – '
                if d_place:
                    label += '%s' % d_place
                label += ')'
        if self.event_choice == 7:
            if b_type:
                label += '%s%s' % (line_delimiter, b_type.get_abbreviation())
                if b_date:
                    label += ' %s' % b_date
                if b_place:
                    label += ' %s' % b_place

            if d_type:
                label += '%s%s' % (line_delimiter, d_type.get_abbreviation())
                if d_date:
                    label += ' %s' % d_date
                if d_place:
                    label += ' %s' % d_place

        if self.increlname and self.center_person != person:
            # display relationship info
            if self.advrelinfo:
                (relationship, _ga, _gb) = self.rel_calc.get_one_relationship(
                    self._db, self.center_person, person,
                    extra_info=True, olocale=self._locale)
                if relationship:
                    label += "%s(%s Ga=%d Gb=%d)" % (line_delimiter,
                                                     relationship, _ga, _gb)
            else:
                relationship = self.rel_calc.get_one_relationship(
                    self._db, self.center_person, person,
                    olocale=self._locale)
                if relationship:
                    label += "%s(%s)" % (line_delimiter, relationship)

        if self.occupation > 0:
            event_refs = person.get_primary_event_ref_list()
            events = [event for event in
                      [self._db.get_event_from_handle(ref.ref)
                       for ref in event_refs]
                      if event.get_type() == EventType(EventType.OCCUPATION)]
            if len(events) > 0:
                events.sort(key=lambda x: x.get_date_object())
                if self.occupation == 1:
                    occupation = events[-1].get_description()
                    if occupation:
                        label += "%s(%s)" % (line_delimiter, occupation)
                elif self.occupation == 2:
                    for evt in events:
                        date = self.get_date_string(evt)
                        place = self.get_place_string(evt)
                        desc = evt.get_description()
                        if not date and not desc and not place:
                            continue
                        label += '%s(' % line_delimiter
                        if date:
                            label += '%s' % date
                            if desc:
                                label += ' '
                        if desc:
                            label += '%s' % desc
                        if place:
                            if date or desc:
                                label += self._(', ') # Arabic OK
                            label += '%s' % place
                        label += ')'

        # see if we have a table that needs to be terminated
        if self.use_html_output:
            label += '</TD></TR></TABLE>'
            return label
        else:
            # non html label is enclosed by "" so escape other "
            return label.replace('"', '\\\"')

    def get_event_strings(self, person):
        "returns tuple of birth/christening and death/burying date strings"

        birth_date = birth_place = death_date = death_place = ""
        birth_type = death_type = ""

        birth_event = get_birth_or_fallback(self._db, person)
        if birth_event:
            birth_type = birth_event.type
            birth_date = self.get_date_string(birth_event)
            birth_place = self.get_place_string(birth_event)

        death_event = get_death_or_fallback(self._db, person)
        if death_event:
            death_type = death_event.type
            death_date = self.get_date_string(death_event)
            death_place = self.get_place_string(death_event)

        return (birth_date, death_date, birth_place,
                death_place, birth_type, death_type)

    def get_date_string(self, event):
        """
        return date string for an event label.

        Based on the data availability and preferences, we select one
        of the following for a given event:
            year only
            complete date
            empty string
        """
        if event and event.get_date_object() is not None:
            event_date = event.get_date_object()
            if event_date.get_year_valid():
                if self.event_choice in [4, 5]:
                    return self.get_date( # localized year
                        Date(event_date.get_year()))
                elif self.event_choice in [1, 2, 3, 7]:
                    return self.get_date(event_date)
        return ''

    def get_place_string(self, event):
        """
        return place string for an event label.

        Based on the data availability and preferences, we select one
        of the following for a given event:
            place name
            empty string
        """
        if event and self.event_choice in [2, 3, 5, 6, 7]:
            place = _pd.display_event(self._db, event)
            return html.escape(place)
        return ''
    def get_date(self, date):
        """ return a formatted date """
        return html.escape(self._get_date(date))

#------------------------------------------------------------------------
#
# RelGraphOptions class
#
#------------------------------------------------------------------------
class RelGraphOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """
    def __init__(self, name, dbase):
        self.__pid = None
        self.__filter = None
        self.__show_relships = None
        self.__show_ga_gb = None
        self.__include_images = None
        self.__image_on_side = None
        self.__db = dbase
        self._nf = None
        self.event_choice = None
        MenuReportOptions.__init__(self, name, dbase)

    def add_menu_options(self, menu):
        ################################
        category_name = _("Report Options")
        add_option = partial(menu.add_option, category_name)
        ################################

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
            _("Determines what people are included in the graph"))
        add_option("filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)

        self.__pid = PersonOption(_("Center Person"))
        self.__pid.set_help(_("The center person for the report"))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)

        arrow = EnumeratedListOption(_("Arrowhead direction"), 'd')
        for i in range(0, len(_ARROWS)):
            arrow.add_item(_ARROWS[i]["value"], _ARROWS[i]["name"])
        arrow.set_help(_("Choose the direction that the arrows point."))
        add_option("arrow", arrow)

        color = EnumeratedListOption(_("Graph coloring"), 'filled')
        for i in range(0, len(_COLORS)):
            color.add_item(_COLORS[i]["value"], _COLORS[i]["name"])
        color.set_help(_("Males will be shown with blue, females "
                         "with red.  If the sex of an individual "
                         "is unknown it will be shown with gray."))
        add_option("color", color)

        # see bug report #2180
        roundedcorners = BooleanOption(_("Use rounded corners"), False)
        roundedcorners.set_help(_("Use rounded corners to differentiate "
                                  "between women and men."))
        add_option("useroundedcorners", roundedcorners)

        # see bug report #11112
        hexagons = BooleanOption(_("Use hexagons"), False)
        hexagons.set_help(_("Use hexagons to differentiate "
                                  "those of unknown gender."))
        add_option("usehexagons", hexagons)

        stdoptions.add_gramps_id_option(menu, category_name, ownline=True)

        ################################
        category_name = _("Report Options (2)")
        add_option = partial(menu.add_option, category_name)
        ################################

        self._nf = stdoptions.add_name_format_option(menu, category_name)
        self._nf.connect('value-changed', self.__update_filters)

        self.__update_filters()

        stdoptions.add_private_data_option(menu, category_name)

        stdoptions.add_living_people_option(menu, category_name)

        locale_opt = stdoptions.add_localization_option(menu, category_name)

        stdoptions.add_date_format_option(menu, category_name, locale_opt)

        ################################
        add_option = partial(menu.add_option, _("Include"))
        ################################

        self.event_choice = EnumeratedListOption(_('Dates and/or Places'), 0)
        self.event_choice.add_item(0, _('Do not include any dates or places'))
        self.event_choice.add_item(1, _('Include (birth, marriage, death) '
                                        'dates, but no places'))
        self.event_choice.add_item(2, _('Include (birth, marriage, death) '
                                        'dates, and places'))
        self.event_choice.add_item(3, _('Include (birth, marriage, death) '
                                        'dates, and places if no dates'))
        self.event_choice.add_item(4, _('Include (birth, marriage, death) '
                                        'years, but no places'))
        self.event_choice.add_item(5, _('Include (birth, marriage, death) '
                                        'years, and places'))
        self.event_choice.add_item(6, _('Include (birth, marriage, death) '
                                        'places, but no dates'))
        self.event_choice.add_item(7, _('Include (birth, marriage, death) '
                                        'dates and places on same line'))
        self.event_choice.set_help(
            _("Whether to include dates and/or places"))
        add_option("event_choice", self.event_choice)

        show_family_leaves = BooleanOption(_("Show all family nodes"), True)
        show_family_leaves.set_help(_("Show family nodes even if the output "
                                      "contains only one member of the family."))
        add_option("show_family_leaves", show_family_leaves)

        url = BooleanOption(_("Include URLs"), False)
        url.set_help(_("Include a URL in each graph node so "
                       "that PDF and imagemap files can be "
                       "generated that contain active links "
                       "to the files generated by the 'Narrated "
                       "Web Site' report."))
        add_option("url", url)

        self.__show_relships = BooleanOption(
            _("Include relationship to center person"), False)
        self.__show_relships.set_help(_("Whether to show every person's "
                                        "relationship to the center person"))
        add_option("increlname", self.__show_relships)
        self.__show_relships.connect('value-changed',
                                     self.__show_relships_changed)

        self.__include_images = BooleanOption(
            _('Include thumbnail images of people'), False)
        self.__include_images.set_help(
            _("Whether to include thumbnails of people."))
        add_option("includeImages", self.__include_images)
        self.__include_images.connect('value-changed', self.__image_changed)

        self.__image_on_side = EnumeratedListOption(_("Thumbnail Location"), 0)
        self.__image_on_side.add_item(0, _('Above the name'))
        self.__image_on_side.add_item(1, _('Beside the name'))
        self.__image_on_side.set_help(
            _("Where the thumbnail image should appear relative to the name"))
        add_option("imageOnTheSide", self.__image_on_side)

        #occupation = BooleanOption(_("Include occupation"), False)
        occupation = EnumeratedListOption(_('Include occupation'), 0)
        occupation.add_item(0, _('Do not include any occupation'))
        occupation.add_item(1, _('Include description '
                                 'of most recent occupation'))
        occupation.add_item(2, _('Include date, description and place '
                                 'of all occupations'))
        occupation.set_help(_("Whether to include the last occupation"))
        add_option("occupation", occupation)

        if __debug__:
            self.__show_ga_gb = BooleanOption(_("Include relationship "
                                                "debugging numbers also"),
                                              False)
            self.__show_ga_gb.set_help(_("Whether to include 'Ga' and 'Gb' "
                                         "also, to debug the relationship "
                                         "calculator"))
            add_option("advrelinfo", self.__show_ga_gb)

        ################################
        add_option = partial(menu.add_option, _("Graph Style"))
        ################################

        color_males = ColorOption(_('Males'), '#e0e0ff')
        color_males.set_help(_('The color to use to display men.'))
        add_option('colormales', color_males)

        color_females = ColorOption(_('Females'), '#ffe0e0')
        color_females.set_help(_('The color to use to display women.'))
        add_option('colorfemales', color_females)

        color_unknown = ColorOption(_('Unknown'), '#e0e0e0')
        color_unknown.set_help(
            _('The color to use when the gender is unknown.')
            )
        add_option('colorunknown', color_unknown)

        color_family = ColorOption(_('Families'), '#ffffe0')
        color_family.set_help(_('The color to use to display families.'))
        add_option('colorfamilies', color_family)

        dashed = BooleanOption(
            _("Indicate non-birth relationships with dotted lines"), True)
        dashed.set_help(_("Non-birth relationships will show up "
                          "as dotted lines in the graph."))
        add_option("dashed", dashed)

        showfamily = BooleanOption(_("Show family nodes"), True)
        showfamily.set_help(_("Families will show up as ellipses, linked "
                              "to parents and children."))
        add_option("showfamily", showfamily)

    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        nfv = self._nf.get_value()
        filter_list = utils.get_person_filters(person,
                                               include_single=False,
                                               name_format=nfv)
        self.__filter.set_filters(filter_list)

    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the person option
        """
        if self.__show_relships and self.__show_relships.get_value():
            self.__pid.set_available(True)
        filter_value = self.__filter.get_value()
        if filter_value == 0: # "Entire Database" (as "include_single=False")
            self.__pid.set_available(False)
        else:
            # The other filters need a center person (assume custom ones too)
            self.__pid.set_available(True)

    def __image_changed(self):
        """
        Handle thumbnail change. If the image is not to be included, make the
        image location option unavailable.
        """
        self.__image_on_side.set_available(self.__include_images.get_value())

    def __show_relships_changed(self):
        """
        Enable/disable menu items if relationships are required
        """
        if self.__show_ga_gb:
            self.__show_ga_gb.set_available(self.__show_relships.get_value())
        self.__filter_changed()
