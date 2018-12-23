#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007 Donald N. Allingham
# Copyright (C) 2007-2012 Brian G. Matherly
# Copyright (C) 2009      Nick Hall
# Copyright (C) 2009      Benny Malengier
# Copyright (C) 2010      Jakim Friant
# Copyright (C) 2011      Tim G L Lyons
# Copyright (C) 2012      Mathieu MD
# Copyright (C) 2013-2016 Paul Franklin
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

""" Complete Individual Report """

#------------------------------------------------------------------------
#
# standard python modules
#
#------------------------------------------------------------------------
import os
from collections import defaultdict

#------------------------------------------------------------------------
#
# Gramps modules
#
#------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.lib import EventRoleType, EventType, Person, NoteType
from gramps.gen.plug.docgen import (IndexMark, FontStyle, ParagraphStyle,
                                    TableStyle, TableCellStyle,
                                    FONT_SANS_SERIF, INDEX_TYPE_TOC,
                                    PARA_ALIGN_CENTER, PARA_ALIGN_RIGHT)
from gramps.gen.display.place import displayer as _pd
from gramps.gen.plug.menu import (BooleanOption, FilterOption, PersonOption,
                                  BooleanListOption)
from gramps.gen.plug.report import Report
from gramps.gen.plug.report import utils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import Bibliography
from gramps.gen.plug.report import endnotes as Endnotes
from gramps.gen.plug.report import stdoptions
from gramps.gen.utils.file import media_path_full
from gramps.gen.utils.lds import TEMPLES
from gramps.gen.proxy import CacheProxyDb
from gramps.gen.errors import ReportError

#------------------------------------------------------------------------
#
# Global variables (ones used in both classes here, that is)
#
#------------------------------------------------------------------------

# _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh
def _T_(value): # enable deferred translations (see Python docs 22.1.3.4)
    return value

CUSTOM = _T_("Custom")

# Construct section list and type to group map
SECTION_LIST = []
TYPE2GROUP = {}
for event_group, type_list in EventType().get_menu_standard_xml():
    SECTION_LIST.append(event_group)
    for event_type in type_list:
        TYPE2GROUP[event_type] = event_group
SECTION_LIST.append(CUSTOM)
TYPE2GROUP[EventType.CUSTOM] = CUSTOM
TYPE2GROUP[EventType.UNKNOWN] = _T_("Unknown")

#------------------------------------------------------------------------
#
# IndivCompleteReport
#
#------------------------------------------------------------------------
class IndivCompleteReport(Report):
    """ the Complete Individual Report """

    def __init__(self, database, options, user):
        """
        Create the IndivCompleteReport object that produces the report.

        The arguments are:

        database        - the Gramps database instance
        options         - instance of the Options class for this report
        user            - a gen.user.User() instance

        This report needs the following parameters (class variables)
        that come in the options class.

        filter    - Filter to be applied to the people of the database.
                    The option class carries its number, and the function
                    returning the list of filters.
        cites     - Whether or not to include source information.
        sort      - Whether or not to sort events into chronological order.
        grampsid  - Whether or not to include any Gramps IDs
        images    - Whether or not to include images.
        sections  - Which event groups should be given separate sections.
        name_format   - Preferred format to display names
        incl_private  - Whether to include private data
        incl_attrs    - Whether to include attributes
        incl_census   - Whether to include census events
        incl_notes    - Whether to include person and family notes
        incl_tags     - Whether to include tags
        incl_relname  - Whether to include relationship to home person
        living_people - How to handle living people
        years_past_death - Consider as living this many years after death
        """

        Report.__init__(self, database, options, user)
        self._user = user
        menu = options.menu

        self.set_locale(menu.get_option_by_name('trans').get_value())

        stdoptions.run_date_format_option(self, menu)

        stdoptions.run_private_data_option(self, menu)
        stdoptions.run_living_people_option(self, menu, self._locale)
        self.database = CacheProxyDb(self.database)
        self._db = self.database

        self.use_pagebreak = menu.get_option_by_name('pageben').get_value()

        self.sort = menu.get_option_by_name('sort').get_value()

        self.use_attrs = menu.get_option_by_name('incl_attrs').get_value()
        self.use_census = menu.get_option_by_name('incl_census').get_value()
        self.use_gramps_id = menu.get_option_by_name('inc_id').get_value()
        self.use_images = menu.get_option_by_name('images').get_value()
        self.use_notes = menu.get_option_by_name('incl_notes').get_value()
        self.use_srcs = menu.get_option_by_name('cites').get_value()
        self.use_src_notes = menu.get_option_by_name('incsrcnotes').get_value()
        self.use_tags = menu.get_option_by_name('incl_tags').get_value()

        filter_option = options.menu.get_option_by_name('filter')
        self.filter = filter_option.get_filter()

        self.section_list = menu.get_option_by_name('sections').get_selected()

        stdoptions.run_name_format_option(self, menu)

        self.place_format = menu.get_option_by_name("place_format").get_value()

        self.home_person = self._db.get_default_person() # might be None
        self.increlname = menu.get_option_by_name('incl_relname').get_value()
        if self.increlname and self.home_person:
            from gramps.gen.relationship import get_relationship_calculator
            self.rel_calc = get_relationship_calculator(reinit=True,
                                                        clocale=self._locale)

        self.bibli = None
        self.family_notes_list = []
        self.names_notes_list = []
        self.mime0 = None
        self.person = None

    def write_fact(self, event_ref, event, show_type=True):
        """
        Writes a single event.
        """
        role = event_ref.get_role()
        description = event.get_description()

        date = self._get_date(event.get_date_object())
        place_name = ''
        place_endnote = ''
        place_handle = event.get_place_handle()
        if place_handle:
            place = self._db.get_place_from_handle(place_handle)
            place_name = _pd.display_event(self._db, event, self.place_format)
            place_endnote = self._cite_endnote(place)
        # make sure it's translated, so it can be used below, in "combine"
        ignore = _('%(str1)s in %(str2)s. ') % {'str1' : '', 'str2' : ''}
        date_place = self.combine('%(str1)s in %(str2)s. ', '%s. ',
                                  date, place_name)

        if show_type:
            # Groups with more than one type
            column_1 = self._(self._get_type(event.get_type()))
            if role not in (EventRoleType.PRIMARY, EventRoleType.FAMILY):
                column_1 = column_1 + ' (' + self._(role.xml_str()) + ')'
            # translators: needed for Arabic, ignore otherwise
            # make sure it's translated, so it can be used below, in "combine"
            ignore = _('%(str1)s, %(str2)s') % {'str1' : '', 'str2' : ''}
            column_2 = self.combine('%(str1)s, %(str2)s', '%s',
                                    description, date_place)
        else:
            # Groups with a single type (remove event type from first column)
            column_1 = date
            # translators: needed for Arabic, ignore otherwise
            # make sure it's translated, so it can be used below, in "combine"
            ignore = _('%(str1)s, %(str2)s') % {'str1' : '', 'str2' : ''}
            column_2 = self.combine('%(str1)s, %(str2)s', '%s',
                                    description, place_name)

        endnotes = self._cite_endnote(event, prior=place_endnote)

        self.doc.start_row()
        self.write_cell(column_1)
        self.doc.start_cell('IDS-NormalCell')
        self.doc.start_paragraph('IDS-Normal')
        self.doc.write_text(column_2)
        if endnotes:
            self.doc.start_superscript()
            self.doc.write_text(endnotes)
            self.doc.end_superscript()
        self.doc.end_paragraph()

        self.do_attributes(event.get_attribute_list() +
                           event_ref.get_attribute_list())

        for notehandle in event.get_note_list():
            note = self._db.get_note_from_handle(notehandle)
            text = note.get_styledtext()
            if self.use_gramps_id:
                text = text + ' [%s]' % note.get_gramps_id()
            note_format = note.get_format()
            self.doc.write_styled_note(
                text, note_format, 'IDS-Normal',
                contains_html=(note.get_type() == NoteType.HTML_CODE))

        self.doc.end_cell()
        self.doc.end_row()

    def write_p_entry(self, label, parent_name, rel_type, pmark=None):
        """ write parent entry """
        self.doc.start_row()
        self.write_cell(label)
        if parent_name:
            # for example (a stepfather): John Smith, relationship: Step
            text = self._('%(parent-name)s, relationship: %(rel-type)s'
                         ) % {'parent-name' : parent_name,
                              'rel-type'    : self._(rel_type)}
            self.write_cell(text, mark=pmark)
        else:
            self.write_cell('')
        self.doc.end_row()

    def write_note(self):
        """ write a note """
        notelist = self.person.get_note_list()[:]  # we don't want to modify cached original
        notelist += self.family_notes_list
        if self.names_notes_list:
            for note_handle in self.names_notes_list:
                if note_handle not in notelist:
                    notelist += [note_handle]
        if not notelist or not self.use_notes:
            return
        self.doc.start_table('note', 'IDS-IndTable')
        self.doc.start_row()
        self.doc.start_cell('IDS-TableHead', 2)
        self.write_paragraph(self._('Notes'), style='IDS-SectionTitle')
        self.doc.end_cell()
        self.doc.end_row()

        for notehandle in notelist:
            note = self._db.get_note_from_handle(notehandle)
            text = note.get_styledtext()
            if self.use_gramps_id:
                text = text + ' [%s]' % note.get_gramps_id()
            note_format = note.get_format()
            self.doc.start_row()
            self.doc.start_cell('IDS-NormalCell', 2)
            self.doc.write_styled_note(
                text, note_format, 'IDS-Normal',
                contains_html=(note.get_type() == NoteType.HTML_CODE))

            self.doc.end_cell()
            self.doc.end_row()

        self.doc.end_table()
        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

    def write_alt_parents(self):
        """ write any alternate parents """

        family_handle_list = self.person.get_parent_family_handle_list()
        if len(family_handle_list) < 2:
            return

        self.doc.start_table("altparents", "IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.write_paragraph(self._('Alternate Parents'),
                             style='IDS-SectionTitle')
        self.doc.end_cell()
        self.doc.end_row()

        for family_handle in family_handle_list:
            if family_handle == self.person.get_main_parents_family_handle():
                continue

            family = self._db.get_family_from_handle(family_handle)

            # Get the mother and father relationships
            frel = ""
            mrel = ""
            child_handle = self.person.get_handle()
            child_ref_list = family.get_child_ref_list()
            for child_ref in child_ref_list:
                if child_ref.ref == child_handle:
                    frel = str(child_ref.get_father_relation())
                    mrel = str(child_ref.get_mother_relation())

            father_handle = family.get_father_handle()
            if father_handle:
                father = self._db.get_person_from_handle(father_handle)
                fname = self._name_display.display(father)
                mark = utils.get_person_mark(self._db, father)
                self.write_p_entry(self._('Father'), fname, frel, mark)
            else:
                self.write_p_entry(self._('Father'), '', '')

            mother_handle = family.get_mother_handle()
            if mother_handle:
                mother = self._db.get_person_from_handle(mother_handle)
                mname = self._name_display.display(mother)
                mark = utils.get_person_mark(self._db, mother)
                self.write_p_entry(self._('Mother'), mname, mrel, mark)
            else:
                self.write_p_entry(self._('Mother'), '', '')

        self.doc.end_table()
        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

    def get_name(self, person):
        """ prepare the name to display """
        name = self._name_display.display(person)
        if self.use_gramps_id:
            return '%(name)s [%(gid)s]' % {'name': name,
                                           'gid': person.get_gramps_id()}
        else:
            return name

    def write_home_relationship(self):
        """ write the person's relationship to the home/default person """

        if not (self.increlname
                and self.home_person
                and self.home_person != self.person):
            return
        home_relationship = self.rel_calc.get_one_relationship(
            self._db, self.home_person, self.person, olocale=self._locale)
        if not home_relationship:
            return

        self.doc.start_table("homerelation", "IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.write_paragraph(self._('Relationship to home person'),
                             style='IDS-SectionTitle')
        self.doc.end_cell()
        self.doc.end_row()
        self.doc.start_row()
        self.write_cell(home_relationship, span=2)
        self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()

    def write_alt_names(self):
        """ write any alternate names of the person """

        alt_names = self.person.get_alternate_names()
        if len(alt_names) < 1:
            return

        self.doc.start_table("altnames", "IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.write_paragraph(self._('Alternate Names'),
                             style='IDS-SectionTitle')
        self.doc.end_cell()
        self.doc.end_row()

        for name in alt_names:
            self.names_notes_list += name.get_note_list()
            name_type = self._(self._get_type(name.get_type()))
            self.doc.start_row()
            self.write_cell(name_type)
            text = self._name_display.display_name(name)
            endnotes = self._cite_endnote(name)
            self.write_cell(text, endnotes)
            self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()

    def write_addresses(self):
        """ write any addresses of the person """

        alist = self.person.get_address_list()

        if len(alist) == 0:
            return

        self.doc.start_table("addresses", "IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.write_paragraph(self._('Addresses'), style='IDS-SectionTitle')
        self.doc.end_cell()
        self.doc.end_row()

        for addr in alist:
            text = utils.get_address_str(addr)
            date = self._get_date(addr.get_date_object())
            endnotes = self._cite_endnote(addr)
            self.doc.start_row()
            self.write_cell(date)
            self.write_cell(text, endnotes)
            self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()

    def write_associations(self):
        """ write any associations of the person """

        if len(self.person.get_person_ref_list()) < 1:
            return

        self.doc.start_table("associations", "IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.write_paragraph(self._('Associations'), style='IDS-SectionTitle')
        self.doc.end_cell()
        self.doc.end_row()
        for person_ref in self.person.get_person_ref_list():
            endnotes = self._cite_endnote(person_ref)
            relationship = person_ref.get_relation()
            associate = self._db.get_person_from_handle(person_ref.ref)
            associate_name = self._name_display.display(associate)
            self.doc.start_row()
            self.write_cell(self._(relationship))
            self.write_cell(associate_name, endnotes)
            self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()

    def write_attributes(self):
        """ write any attributes of the person """

        attr_list = self.person.get_attribute_list()

        if len(attr_list) == 0 or not self.use_attrs:
            return

        self.doc.start_table("attributes", "IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.write_paragraph(self._('Attributes'), style='IDS-SectionTitle')
        self.doc.end_cell()
        self.doc.end_row()

        for attr in attr_list:
            attr_type = attr.get_type().type2base()
            self.doc.start_row()
            self.write_cell(self._(attr_type))
            text = attr.get_value()
            endnotes = self._cite_endnote(attr)
            self.write_cell(text, endnotes)
            self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()

    def write_LDS_ordinances(self):
        """ write any LDS ordinances of the person """

        ord_list = self.person.get_lds_ord_list()

        if len(ord_list) == 0:
            return

        self.doc.start_table("ordinances", "IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.write_paragraph(self._('LDS Ordinance'), style='IDS-SectionTitle')
        self.doc.end_cell()
        self.doc.end_row()
        self.doc.end_table()

        self.doc.start_table("ordinances3", "IDS-OrdinanceTable")
        self.doc.start_row()
        self.write_cell(self._('Type'), style='IDS-TableSection')
        self.write_cell(self._('Date'), style='IDS-TableSection')
        self.write_cell(self._('Status'), style='IDS-TableSection')
        self.write_cell(self._('Temple'), style='IDS-TableSection')
        self.write_cell(self._('Place'), style='IDS-TableSection')
        self.doc.end_row()

        for lds_ord in ord_list:
            otype = self._(lds_ord.type2str())
            date = self._get_date(lds_ord.get_date_object())
            status = self._(lds_ord.status2str())
            temple = TEMPLES.name(lds_ord.get_temple())
            place_name = ''
            place_endnote = ''
            place_handle = lds_ord.get_place_handle()
            if place_handle:
                place = self._db.get_place_from_handle(place_handle)
                place_name = _pd.display_event(self._db, lds_ord,
                                               self.place_format)
                place_endnote = self._cite_endnote(place)
            endnotes = self._cite_endnote(lds_ord, prior=place_endnote)
            self.doc.start_row()
            self.write_cell(otype, endnotes)
            self.write_cell(date)
            self.write_cell(status)
            self.write_cell(temple)
            self.write_cell(place_name)
            self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()

    def write_tags(self):
        """ write any tags the person has """

        thlist = self.person.get_tag_list()
        if len(thlist) == 0 or not self.use_tags:
            return
        tags = []

        self.doc.start_table("tags", "IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.write_paragraph(self._('Tags'), style='IDS-SectionTitle')
        self.doc.end_cell()
        self.doc.end_row()
        for tag_handle in thlist:
            tag = self._db.get_tag_from_handle(tag_handle)
            tags.append(tag.get_name())
        for text in sorted(tags):
            self.doc.start_row()
            self.write_cell(text, span=2)
            self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()

    def write_images(self):
        """ write any images the person has """

        media_list = self.person.get_media_list()
        if (not self.use_images) or (not media_list):
            return

        i_total = 0
        for media_ref in media_list:
            media_handle = media_ref.get_reference_handle()
            if media_handle:
                media = self._db.get_media_from_handle(media_handle)
                if media and media.get_mime_type():
                    if media.get_mime_type().startswith("image"):
                        i_total += 1
        if i_total == 0:
            return
        # if there is only one image, and it is the first Gallery item, it
        # will be shown up at the top, so there's no reason to show it here;
        # but if there's only one image and it is not the first Gallery
        # item (maybe the first is a PDF, say), then we need to show it
        if (i_total == 1) and self.mime0 and self.mime0.startswith("image"):
            return

        self.doc.start_table("images", "IDS-GalleryTable")
        cells = 3 # the GalleryTable has 3 cells
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", cells)
        self.write_paragraph(self._('Images'), style='IDS-SectionTitle')
        self.doc.end_cell()
        self.doc.end_row()
        media_count = 0
        image_count = 0
        while media_count < len(media_list):
            media_ref = media_list[media_count]
            media_handle = media_ref.get_reference_handle()
            media = self._db.get_media_from_handle(media_handle)
            if media is None:
                self._user.notify_db_repair(
                    _('Non existing media found in the Gallery'))
                self.doc.end_table()
                self.doc.start_paragraph('IDS-Normal')
                self.doc.end_paragraph()
                return
            mime_type = media.get_mime_type()
            if not mime_type or not mime_type.startswith("image"):
                media_count += 1
                continue
            description = media.get_description()
            if image_count % cells == 0:
                self.doc.start_row()
            self.doc.start_cell('IDS-NormalCell')
            self.write_paragraph(description, style='IDS-ImageCaption')
            utils.insert_image(self._db, self.doc, media_ref, self._user,
                                     align='center', w_cm=5.0, h_cm=5.0)
            self.do_attributes(media.get_attribute_list() +
                               media_ref.get_attribute_list())
            self.doc.end_cell()
            if image_count % cells == cells - 1:
                self.doc.end_row()
            media_count += 1
            image_count += 1
        if image_count % cells != 0:
            self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()

    def write_families(self):
        """ write any families the person has """

        family_handle_list = self.person.get_family_handle_list()
        if not len(family_handle_list):
            return

        self.doc.start_table("three", "IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.write_paragraph(self._('Families'),
                             style='IDS-SectionTitle')
        self.doc.end_cell()
        self.doc.end_row()
        self.doc.end_table()

        for family_handle in family_handle_list:
            self.doc.start_table("three", "IDS-IndTable")
            family = self._db.get_family_from_handle(family_handle)
            self.family_notes_list += family.get_note_list()
            if self.person.get_handle() == family.get_father_handle():
                spouse_id = family.get_mother_handle()
            else:
                spouse_id = family.get_father_handle()
            self.doc.start_row()
            self.doc.start_cell("IDS-NormalCell", 2)
            if spouse_id:
                spouse = self._db.get_person_from_handle(spouse_id)
                text = self.get_name(spouse)
                mark = utils.get_person_mark(self._db, spouse)
            else:
                spouse = None
                text = self._("unknown")
                mark = None
            endnotes = self._cite_endnote(family)
            self.write_paragraph(text, endnotes=endnotes, mark=mark,
                                 style='IDS-Spouse')
            self.doc.end_cell()
            self.doc.end_row()

            event_ref_list = family.get_event_ref_list()
            for event_ref, event in self.get_event_list(event_ref_list):
                self.write_fact(event_ref, event)

            child_ref_list = family.get_child_ref_list()
            if len(child_ref_list):
                self.doc.start_row()
                self.write_cell(self._("Children"))
                self.doc.start_cell("IDS-ListCell")
                for child_ref in child_ref_list:
                    child = self._db.get_person_from_handle(child_ref.ref)
                    name = self.get_name(child)
                    mark = utils.get_person_mark(self._db, child)
                    endnotes = self._cite_endnote(child_ref)
                    self.write_paragraph(name, endnotes=endnotes, mark=mark)
                self.doc.end_cell()
                self.doc.end_row()

            attr_list = family.get_attribute_list()
            if len(attr_list) and self.use_attrs:
                self.doc.start_row()
                self.write_cell(self._("Attributes"))
                self.doc.start_cell("IDS-ListCell")
                self.do_attributes(attr_list)
                self.doc.end_cell()
                self.doc.end_row()

            self.doc.end_table()

            ord_list = family.get_lds_ord_list()
            if len(ord_list):
                self.doc.start_table("ordinances2", "IDS-OrdinanceTable2")
                self.doc.start_row()
                self.write_cell(self._('LDS Ordinance'))
                self.write_cell(self._('Type'), style='IDS-TableSection')
                self.write_cell(self._('Date'), style='IDS-TableSection')
                self.write_cell(self._('Status'), style='IDS-TableSection')
                self.write_cell(self._('Temple'), style='IDS-TableSection')
                self.write_cell(self._('Place'), style='IDS-TableSection')
                self.doc.end_row()

                for lds_ord in ord_list:
                    otype = self._(lds_ord.type2str())
                    date = self._get_date(lds_ord.get_date_object())
                    status = self._(lds_ord.status2str())
                    temple = TEMPLES.name(lds_ord.get_temple())
                    place_name = ''
                    place_endnote = ''
                    place_handle = lds_ord.get_place_handle()
                    if place_handle:
                        place = self._db.get_place_from_handle(place_handle)
                        place_name = _pd.display_event(self._db, lds_ord,
                                                       self.place_format)
                        place_endnote = self._cite_endnote(place)
                    endnotes = self._cite_endnote(lds_ord, prior=place_endnote)
                    self.doc.start_row()
                    self.write_cell('')
                    self.write_cell(otype, endnotes)
                    self.write_cell(date)
                    self.write_cell(status)
                    self.write_cell(temple)
                    self.write_cell(place_name)
                    self.doc.end_row()
                self.doc.end_table()

        self.doc.start_paragraph('IDS-Normal')
        self.doc.end_paragraph()

    def get_event_list(self, event_ref_list):
        """
        Return a list of (EventRef, Event) pairs.  Order by event date
        if the user option is set.
        """
        event_list = []
        for ind, event_ref in enumerate(event_ref_list):
            if event_ref:
                event = self._db.get_event_from_handle(event_ref.ref)
                if event:
                    if (event.get_type() == EventType.CENSUS
                            and not self.use_census):
                        continue
                    sort_value = event.get_date_object().get_sort_value()
                    #first sort on date, equal dates, then sort as in GUI.
                    event_list.append((str(sort_value) + "%04i" % ind,
                                       event_ref, event))

        if self.sort:
            event_list.sort()

        return [(item[1], item[2]) for item in event_list]

    def write_section(self, event_ref_list, event_group_sect):
        """
        Writes events in a single event group.
        """
        self.doc.start_table(event_group_sect, "IDS-IndTable")
        self.doc.start_row()
        self.doc.start_cell("IDS-TableHead", 2)
        self.write_paragraph(self._(event_group_sect), style='IDS-SectionTitle')
        self.doc.end_cell()
        self.doc.end_row()

        for event_ref, event in self.get_event_list(event_ref_list):
            self.write_fact(event_ref, event)

        self.doc.end_table()
        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

    def write_events(self):
        """
        Write events.  The user can create separate sections for a
        pre-defined set of event groups.  When an event has a type
        contained within a group it is moved from the Individual Facts
        section into its own section.
        """
        event_dict = defaultdict(list)
        event_ref_list = self.person.get_event_ref_list()
        for event_ref in event_ref_list:
            if event_ref:
                event = self._db.get_event_from_handle(event_ref.ref)
                group = TYPE2GROUP[event.get_type().value]
                if _(group) not in self.section_list:
                    group = SECTION_LIST[0]
                event_dict[group].append(event_ref)

        # Write separate event group sections
        for group in SECTION_LIST:
            if group in event_dict:
                self.write_section(event_dict[group], group)

    def write_cell(self, text,
                   endnotes=None, mark=None, style='IDS-Normal', span=1):
        """ write a cell """
        self.doc.start_cell('IDS-NormalCell', span)
        self.write_paragraph(text, endnotes=endnotes, mark=mark, style=style)
        self.doc.end_cell()

    def write_paragraph(self, text,
                        endnotes=None, mark=None, style='IDS-Normal'):
        """ write a paragraph """
        self.doc.start_paragraph(style)
        self.doc.write_text(text, mark)
        if endnotes:
            self.doc.start_superscript()
            self.doc.write_text(endnotes)
            self.doc.end_superscript()
        self.doc.end_paragraph()

    def write_report(self):
        """ write the report """
        plist = self._db.get_person_handles(sort_handles=True,
                                            locale=self._locale)
        if self.filter:
            ind_list = self.filter.apply(self._db, plist, user=self._user)
        else:
            ind_list = plist
        if not ind_list:
            raise ReportError(_('Empty report'),
                              _('You did not specify anybody'))

        if self._user:
            self._user.begin_progress(_("Complete Individual Report"),
                                      _("Generating report"),
                                      len(ind_list))
        for count, person_handle in enumerate(ind_list):
            if self._user:
                self._user.step_progress()
            self.person = self._db.get_person_from_handle(person_handle)
            if self.person is None:
                continue
            self.family_notes_list = []
            self.names_notes_list = []
            self.write_person(count)
        if self._user:
            self._user.end_progress()


    def write_person(self, count):
        """ write a person """
        if count != 0:
            self.doc.page_break()
        self.bibli = Bibliography(
            Bibliography.MODE_DATE|Bibliography.MODE_PAGE)

        title1 = self._("Complete Individual Report")
        text2 = self._name_display.display(self.person)
        mark1 = IndexMark(title1, INDEX_TYPE_TOC, 1)
        mark2 = IndexMark(text2, INDEX_TYPE_TOC, 2)
        self.doc.start_paragraph("IDS-Title")
        self.doc.write_text(title1, mark1)
        self.doc.end_paragraph()
        self.doc.start_paragraph("IDS-Title")
        self.doc.write_text(text2, mark2)
        self.doc.end_paragraph()

        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

        name = self.person.get_primary_name()
        text = self.get_name(self.person)
        mark = utils.get_person_mark(self._db, self.person)
        endnotes = self._cite_endnote(self.person)
        endnotes = self._cite_endnote(name, prior=endnotes)

        family_handle = self.person.get_main_parents_family_handle()
        if family_handle:
            family = self._db.get_family_from_handle(family_handle)
            father_inst_id = family.get_father_handle()
            if father_inst_id:
                father_inst = self._db.get_person_from_handle(
                    father_inst_id)
                father = self.get_name(father_inst)
                fmark = utils.get_person_mark(self._db, father_inst)
            else:
                father = ""
                fmark = None
            mother_inst_id = family.get_mother_handle()
            if mother_inst_id:
                mother_inst = self._db.get_person_from_handle(mother_inst_id)
                mother = self.get_name(mother_inst)
                mmark = utils.get_person_mark(self._db, mother_inst)
            else:
                mother = ""
                mmark = None
        else:
            father = ""
            fmark = None
            mother = ""
            mmark = None

        media_list = self.person.get_media_list()
        p_style = 'IDS-PersonTable2'
        self.mime0 = None
        if self.use_images and len(media_list) > 0:
            media0 = media_list[0]
            media_handle = media0.get_reference_handle()
            media = self._db.get_media_from_handle(media_handle)
            self.mime0 = media.get_mime_type()
            if self.mime0 and self.mime0.startswith("image"):
                image_filename = media_path_full(self._db, media.get_path())
                if os.path.exists(image_filename):
                    p_style = 'IDS-PersonTable' # this is tested for, also
                else:
                    self._user.warn(_("Could not add photo to page"),
                                    # translators: for French, else ignore
                                    _("%(str1)s: %(str2)s"
                                     ) % {'str1' : image_filename,
                                          'str2' : _('File does not exist')})

        self.doc.start_table('person', p_style)
        self.doc.start_row()

        # translators: needed for French, ignore otherwise
        ignore = self._("%s:")
        self.doc.start_cell('IDS-NormalCell')
        self.write_paragraph(self._("%s:") % self._("Name"))
        self.write_paragraph(self._("%s:") % self._("Gender"))
        self.write_paragraph(self._("%s:") % self._("Father"))
        self.write_paragraph(self._("%s:") % self._("Mother"))
        self.doc.end_cell()

        self.doc.start_cell('IDS-NormalCell')
        self.write_paragraph(text, endnotes, mark)
        if self.person.get_gender() == Person.MALE:
            self.write_paragraph(self._("Male"))
        elif self.person.get_gender() == Person.FEMALE:
            self.write_paragraph(self._("Female"))
        else:
            self.write_paragraph(self._("Unknown"))
        self.write_paragraph(father, mark=fmark)
        self.write_paragraph(mother, mark=mmark)
        self.doc.end_cell()

        if p_style == 'IDS-PersonTable':
            self.doc.start_cell('IDS-NormalCell')
            self.doc.add_media(image_filename, "right", 4.0, 4.0,
                               crop=media0.get_rectangle())
            endnotes = self._cite_endnote(media0)
            attr_list = media0.get_attribute_list()
            if len(attr_list) == 0 or not self.use_attrs:
                text = _('(image)')
            else:
                for attr in attr_list:
                    attr_type = attr.get_type().type2base()
                    # translators: needed for French, ignore otherwise
                    text = self._("%(str1)s: %(str2)s"
                                 ) % {'str1' : self._(attr_type),
                                      'str2' : attr.get_value()}
                    endnotes = self._cite_endnote(attr, prior=endnotes)
                    self.write_paragraph("(%s)" % text,
                                         endnotes=endnotes,
                                         style='IDS-ImageNote')
                    endnotes = ''
            if endnotes and len(attr_list) == 0:
                self.write_paragraph(text, endnotes=endnotes,
                                     style='IDS-ImageNote')
            self.doc.end_cell()

        self.doc.end_row()
        self.doc.end_table()

        self.doc.start_paragraph("IDS-Normal")
        self.doc.end_paragraph()

        self.write_home_relationship()
        self.write_alt_names()
        self.write_events()
        self.write_alt_parents()
        self.write_families()
        self.write_addresses()
        self.write_associations()
        self.write_attributes()
        self.write_LDS_ordinances()
        self.write_tags()
        self.write_images()
        self.write_note()
        if self.use_srcs:
            if self.use_pagebreak and self.bibli.get_citation_count():
                self.doc.page_break()
            Endnotes.write_endnotes(self.bibli, self._db, self.doc,
                                    printnotes=self.use_src_notes,
                                    elocale=self._locale)

    def combine(self, format_both, format_single, str1, str2):
        """ Combine two strings with a given format. """
        text = ""
        if str1 and str2:
            text = self._(format_both) % {'str1' : str1, 'str2' : str2}
        elif str1 and not str2:
            text = format_single % str1
        elif str2 and not str1:
            text = format_single % str2
        return text

    def _cite_endnote(self, obj, prior=''):
        """ cite any endnotes the person has """
        if not self.use_srcs:
            return ""
        if not obj:
            return prior

        txt = Endnotes.cite_source(self.bibli, self._db, obj, self._locale)
        if not txt:
            return prior
        if prior:
            # translators: needed for Arabic, ignore otherwise
            txt = self._('%(str1)s, %(str2)s') % {'str1':prior, 'str2':txt}
        return txt

    def do_attributes(self, attr_list):
        """ a convenience method """
        if not self.use_attrs:
            return
        for attr in attr_list:
            attr_type = attr.get_type().type2base()
            # translators: needed for French, ignore otherwise
            text = self._("%(str1)s: %(str2)s"
                         ) % {'str1' : self._(attr_type),
                              'str2' : attr.get_value()}
            endnotes = self._cite_endnote(attr)
            self.write_paragraph(text, endnotes)

#------------------------------------------------------------------------
#
# IndivCompleteOptions
#
#------------------------------------------------------------------------
class IndivCompleteOptions(MenuReportOptions):
    """
    Defines options and provides handling interface.
    """
    def __init__(self, name, dbase):
        self.__db = dbase
        self.__pid = None
        self.__filter = None
        self.__cites = None
        self.__incsrcnotes = None
        self._nf = None
        self.__show_relships = None
        MenuReportOptions.__init__(self, name, dbase)

    def get_subject(self):
        """ Return a string that describes the subject of the report. """
        return self.__filter.get_filter().get_name()

    def add_menu_options(self, menu):
        ################################
        category_name = _("Report Options")
        ################################

        self.__filter = FilterOption(_("Filter"), 0)
        self.__filter.set_help(
            _("Select the filter to be applied to the report."))
        menu.add_option(category_name, "filter", self.__filter)
        self.__filter.connect('value-changed', self.__filter_changed)

        self.__pid = PersonOption(_("Filter Person"))
        self.__pid.set_help(_("The center person for the filter."))
        menu.add_option(category_name, "pid", self.__pid)
        self.__pid.connect('value-changed', self.__update_filters)

        sort = BooleanOption(_("List events chronologically"), True)
        sort.set_help(_("Whether to sort events into chronological order."))
        menu.add_option(category_name, "sort", sort)

        pageben = BooleanOption(_("Page break before end notes"), False)
        pageben.set_help(
            _("Whether to start a new page before the end notes."))
        menu.add_option(category_name, "pageben", pageben)

        ################################
        category_name = _("Report Options (2)")
        ################################

        self._nf = stdoptions.add_name_format_option(menu, category_name)
        self._nf.connect('value-changed', self.__update_filters)

        self.__update_filters()

        stdoptions.add_place_format_option(menu, category_name)

        stdoptions.add_private_data_option(menu, category_name)

        stdoptions.add_living_people_option(menu, category_name)

        locale_opt = stdoptions.add_localization_option(menu, category_name)

        stdoptions.add_date_format_option(menu, category_name, locale_opt)

        ################################
        category_name = _("Include")
        ################################

        incl_notes = BooleanOption(_("Include Notes"), True)
        incl_notes.set_help(_("Whether to include Person and Family Notes."))
        menu.add_option(category_name, "incl_notes", incl_notes)

        self.__cites = BooleanOption(_("Include Source Information"), True)
        self.__cites.set_help(_("Whether to cite sources."))
        menu.add_option(category_name, "cites", self.__cites)
        self.__cites.connect('value-changed', self.__sources_changed)

        self.__incsrcnotes = BooleanOption(_("Include sources notes"), False)
        self.__incsrcnotes.set_help(
            _("Whether to include source notes in the Endnotes section. "
              "Only works if Include sources is selected."))
        menu.add_option(category_name, "incsrcnotes", self.__incsrcnotes)
        self.__incsrcnotes.connect('value-changed', self.__sources_changed)
        self.__sources_changed()

        images = BooleanOption(_("Include Photo/Images from Gallery"), True)
        images.set_help(_("Whether to include images."))
        menu.add_option(category_name, "images", images)

        ################################
        category_name = _("Include (2)")
        ################################

        stdoptions.add_gramps_id_option(menu, category_name)

        tags = BooleanOption(_("Include Tags"), True)
        tags.set_help(_("Whether to include tags."))
        menu.add_option(category_name, "incl_tags", tags)

        attributes = BooleanOption(_("Include Attributes"), True)
        attributes.set_help(_("Whether to include attributes."))
        menu.add_option(category_name, "incl_attrs", attributes)

        census = BooleanOption(_("Include Census Events"), True)
        census.set_help(_("Whether to include Census Events."))
        menu.add_option(category_name, "incl_census", census)

        self.__show_relships = BooleanOption(
            _("Include relationship to center person"), False)
        self.__show_relships.set_help(
            _("Whether to include relationships to the center person"))
        menu.add_option(category_name, "incl_relname", self.__show_relships)

        ################################
        category_name = _("Sections")
        ################################

        opt = BooleanListOption(_("Event groups"))
        opt.set_help(_("Check if a separate section is required."))
        for section in SECTION_LIST:
            if section != SECTION_LIST[0]:
                opt.add_button(_(section), True)

        menu.add_option(category_name, "sections", opt)

    def __update_filters(self):
        """
        Update the filter list based on the selected person
        """
        gid = self.__pid.get_value()
        person = self.__db.get_person_from_gramps_id(gid)
        nfv = self._nf.get_value()
        filter_list = utils.get_person_filters(person,
                                               include_single=True,
                                               name_format=nfv)
        self.__filter.set_filters(filter_list)

    def __filter_changed(self):
        """
        Handle filter change. If the filter is not specific to a person,
        disable the person option
        """
        filter_value = self.__filter.get_value()
        if filter_value == 1: # "Entire Database" (as "include_single=True")
            self.__pid.set_available(False)
        else:
            # The other filters need a center person (assume custom ones too)
            self.__pid.set_available(True)

    def __sources_changed(self):
        """
        If Endnotes are not enabled, disable sources in the Endnotes.
        """
        cites_value = self.__cites.get_value()
        self.__incsrcnotes.set_available(cites_value)

    def make_default_style(self, default_style):
        """Make the default output style for the Individual Complete Report."""
        # Paragraph Styles
        font = FontStyle()
        font.set_bold(1)
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(16)
        para = ParagraphStyle()
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_top_margin(utils.pt2cm(8))
        para.set_bottom_margin(utils.pt2cm(8))
        para.set_font(font)
        para.set_description(_("The style used for the title."))
        default_style.add_paragraph_style("IDS-Title", para)

        font = FontStyle()
        font.set_bold(1)
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(12)
        font.set_italic(1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_top_margin(utils.pt2cm(3))
        para.set_bottom_margin(utils.pt2cm(3))
        para.set_description(_("The style used for the section headers."))
        default_style.add_paragraph_style("IDS-SectionTitle", para)

        font = FontStyle()
        font.set_bold(1)
        font.set_type_face(FONT_SANS_SERIF)
        font.set_size(12)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_top_margin(utils.pt2cm(3))
        para.set_bottom_margin(utils.pt2cm(3))
        para.set_description(_("The style used for the spouse's name."))
        default_style.add_paragraph_style("IDS-Spouse", para)

        font = FontStyle()
        font.set_size(12)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_top_margin(utils.pt2cm(3))
        para.set_bottom_margin(utils.pt2cm(3))
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("IDS-Normal", para)

        font = FontStyle()
        font.set_size(12)
        font.set_italic(1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_top_margin(utils.pt2cm(3))
        para.set_bottom_margin(utils.pt2cm(3))
        para.set_description(_('The basic style used for table headings.'))
        default_style.add_paragraph_style('IDS-TableSection', para)

        font = FontStyle()
        font.set_size(8)
        para = ParagraphStyle()
        para.set_alignment(PARA_ALIGN_RIGHT)
        para.set_font(font)
        para.set_top_margin(utils.pt2cm(3))
        para.set_bottom_margin(utils.pt2cm(3))
        para.set_description(_('The style used for image notes.'))
        default_style.add_paragraph_style("IDS-ImageNote", para)

        font = FontStyle()
        font.set_size(8)
        para = ParagraphStyle()
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_font(font)
        para.set_top_margin(utils.pt2cm(3))
        para.set_bottom_margin(utils.pt2cm(3))
        para.set_description(_('The style used for image descriptions.'))
        default_style.add_paragraph_style("IDS-ImageCaption", para)

        # Table Styles
        tbl = TableStyle()
        tbl.set_width(100)
        tbl.set_columns(2)
        tbl.set_column_width(0, 20)
        tbl.set_column_width(1, 80)
        default_style.add_table_style("IDS-IndTable", tbl)

        tbl = TableStyle()
        tbl.set_width(100)
        tbl.set_columns(2)
        tbl.set_column_width(0, 50)
        tbl.set_column_width(1, 50)
        default_style.add_table_style("IDS-ParentsTable", tbl)

        cell = TableCellStyle()
        cell.set_top_border(1)
        cell.set_bottom_border(1)
        default_style.add_cell_style("IDS-TableHead", cell)

        cell = TableCellStyle()
        default_style.add_cell_style("IDS-NormalCell", cell)

        cell = TableCellStyle()
        cell.set_longlist(1)
        default_style.add_cell_style("IDS-ListCell", cell)

        tbl = TableStyle()
        tbl.set_width(100)
        tbl.set_columns(3)
        tbl.set_column_width(0, 20)
        tbl.set_column_width(1, 50)
        tbl.set_column_width(2, 30)
        default_style.add_table_style('IDS-PersonTable', tbl)

        tbl = TableStyle()
        tbl.set_width(100)
        tbl.set_columns(2)
        tbl.set_column_width(0, 20)
        tbl.set_column_width(1, 80)
        default_style.add_table_style('IDS-PersonTable2', tbl)

        tbl = TableStyle()
        tbl.set_width(100)
        tbl.set_columns(5)
        tbl.set_column_width(0, 22) # Type
        tbl.set_column_width(1, 22) # Date
        tbl.set_column_width(2, 16) # Status
        tbl.set_column_width(3, 22) # Temple
        tbl.set_column_width(4, 18) # Place
        default_style.add_table_style('IDS-OrdinanceTable', tbl)

        tbl = TableStyle()
        tbl.set_width(100)
        tbl.set_columns(6)
        tbl.set_column_width(0, 20) # empty
        tbl.set_column_width(1, 18) # Type
        tbl.set_column_width(2, 18) # Date
        tbl.set_column_width(3, 14) # Status
        tbl.set_column_width(4, 18) # Temple
        tbl.set_column_width(5, 12) # Place
        default_style.add_table_style('IDS-OrdinanceTable2', tbl)

        tbl = TableStyle()
        tbl.set_width(100)
        tbl.set_columns(3)
        tbl.set_column_width(0, 33)
        tbl.set_column_width(1, 33)
        tbl.set_column_width(2, 34)
        default_style.add_table_style("IDS-GalleryTable", tbl)

        Endnotes.add_endnote_styles(default_style)
