# encoding: utf-8
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Martin Hawlisch, Donald N. Allingham
# Copyright (C) 2008       Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Tim G L Lyons
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

"""Tools/Debug/Generate Testcases for Persons and Families"""
# pylint: disable=too-many-statements,too-many-locals,too-many-branches
# pylint: disable=wrong-import-position,too-many-public-methods,no-self-use
# pylint: disable=too-many-arguments
# ------------------------------------------------------------------------
#
# standard python modules
#
# ------------------------------------------------------------------------
import sys
import os
import random
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

# ------------------------------------------------------------------------
#
# GNOME libraries
#
# ------------------------------------------------------------------------
from gi.repository import Gtk

# ------------------------------------------------------------------------
#
# Gramps modules
#
# ------------------------------------------------------------------------
from gramps.gen.lib import (
    Address, Attribute, AttributeType, ChildRef,
    ChildRefType, Citation, Date, Event, EventRef, EventRoleType,
    EventType, Family, FamilyRelType, GrampsType, LdsOrd, Location,
    Media, MediaRef, Name, NameOriginType, NameType, Note,
    NoteType, Person, PersonRef, Place, PlaceType, PlaceRef, PlaceName,
    RepoRef, Repository, RepositoryType, Source, SourceMediaType,
    SrcAttribute, SrcAttributeType, Surname, Tag, Url, UrlType)
from gramps.gen.lib.addressbase import AddressBase
from gramps.gen.lib.attrbase import AttributeBase
from gramps.gen.lib.primaryobj import BasicPrimaryObject
from gramps.gen.lib.citationbase import CitationBase
from gramps.gen.lib.date import Today
from gramps.gen.lib.datebase import DateBase
from gramps.gen.lib.ldsordbase import LdsOrdBase
from gramps.gen.lib.locationbase import LocationBase
from gramps.gen.lib.mediabase import MediaBase
from gramps.gen.lib.notebase import NoteBase
from gramps.gen.lib.placebase import PlaceBase
from gramps.gen.lib.privacybase import PrivacyBase
from gramps.gen.lib.tagbase import TagBase
from gramps.gen.lib.urlbase import UrlBase
from gramps.gen.lib import StyledText, StyledTextTag, StyledTextTagType
from gramps.gen.db import DbTxn
from gramps.gen.mime import get_type
from gramps.gui.plug import tool
from gramps.gen.utils.string import conf_strings
from gramps.gen.utils.lds import TEMPLES
from gramps.gen.db.dbconst import *
from gramps.gen.const import ICON, LOGO, SPLASH
from gramps.gui.display import display_help
from gramps.gen.const import URL_MANUAL_PAGE

# ------------------------------------------------------------------------
#
# Constants
#
# ------------------------------------------------------------------------
WIKI_HELP_PAGE = '%s_-_Tools' % URL_MANUAL_PAGE
WIKI_HELP_SEC = _('Generate_Testcases_for_Persons_and_Families')

# the following allows test code to access a private copy of the random
# number generator.  The access is typically used for seeding the generator
# to make it repeatable across runs.  The private copy is unaffected by other
# uses of the global random() functions.
try:
    from gramps.gen.const import myrand
except (NameError, ImportError):
    myrand = random.Random()
except:
    print("Unexpected error:", sys.exc_info()[0])
_random = myrand.random
_choice = myrand.choice
_randint = myrand.randint


LDS_ORD_BAPT_STATUS = (
    LdsOrd.STATUS_NONE,
    LdsOrd.STATUS_CHILD, LdsOrd.STATUS_CLEARED,
    LdsOrd.STATUS_COMPLETED, LdsOrd.STATUS_INFANT,
    LdsOrd.STATUS_PRE_1970, LdsOrd.STATUS_QUALIFIED,
    LdsOrd.STATUS_STILLBORN, LdsOrd.STATUS_SUBMITTED,
    LdsOrd.STATUS_UNCLEARED)

LDS_ORD_CHILD_SEALING_STATUS = (
    LdsOrd.STATUS_NONE,
    LdsOrd.STATUS_BIC, LdsOrd.STATUS_CLEARED,
    LdsOrd.STATUS_COMPLETED, LdsOrd.STATUS_DNS,
    LdsOrd.STATUS_PRE_1970, LdsOrd.STATUS_QUALIFIED,
    LdsOrd.STATUS_STILLBORN, LdsOrd.STATUS_SUBMITTED,
    LdsOrd.STATUS_UNCLEARED)

LDS_ENDOWMENT_DATE_STATUS = (
    LdsOrd.STATUS_NONE,
    LdsOrd.STATUS_CHILD, LdsOrd.STATUS_CLEARED,
    LdsOrd.STATUS_COMPLETED, LdsOrd.STATUS_INFANT,
    LdsOrd.STATUS_PRE_1970, LdsOrd.STATUS_QUALIFIED,
    LdsOrd.STATUS_STILLBORN, LdsOrd.STATUS_SUBMITTED,
    LdsOrd.STATUS_UNCLEARED)

LDS_SPOUSE_SEALING_DATE_STATUS = (
    LdsOrd.STATUS_NONE,
    LdsOrd.STATUS_CANCELED, LdsOrd.STATUS_CLEARED,
    LdsOrd.STATUS_COMPLETED, LdsOrd.STATUS_DNS,
    LdsOrd.STATUS_DNS_CAN, LdsOrd.STATUS_PRE_1970,
    LdsOrd.STATUS_QUALIFIED, LdsOrd.STATUS_SUBMITTED,
    LdsOrd.STATUS_UNCLEARED)

LDS_INDIVIDUAL_ORD = [(LdsOrd.BAPTISM, LDS_ORD_BAPT_STATUS),
                      (LdsOrd.CONFIRMATION, LDS_ORD_BAPT_STATUS),
                      (LdsOrd.ENDOWMENT, LDS_ENDOWMENT_DATE_STATUS),
                      (LdsOrd.SEAL_TO_PARENTS, LDS_ORD_CHILD_SEALING_STATUS)]

LDS_SPOUSE_SEALING = [(LdsOrd.SEAL_TO_SPOUSE,
                       LDS_SPOUSE_SEALING_DATE_STATUS)]


# ------------------------------------------------------------------------

class TestcaseGenerator(tool.BatchTool):
    '''
    This tool generates various test cases for problems that have occured.
    The issues it generates can be corrected via the 'Check and Repair' tool.
    '''
    NUMERIC = 0
    FIRSTNAME = 1
    FIRSTNAME_FEMALE = 2
    FIRSTNAME_MALE = 3
    LASTNAME = 4
    NOTE = 5
    SHORT = 6
    LONG = 7
    TAG = 8
    STYLED_TEXT = 9

#    GEDCON definition:
#
#    FAMILY_EVENT_STRUCTURE:=
#    [
#    n [ ANUL | CENS | DIV | DIVF ] [Y|<NULL>] {1:1}
#    +1 <<EVENT_DETAIL>> {0:1} p.29
#    |
#    n [ ENGA | MARR | MARB | MARC ] [Y|<NULL>] {1:1}
#    +1 <<EVENT_DETAIL>> {0:1} p.29
#    |
#    n [ MARL | MARS ] [Y|<NULL>] {1:1}
#    +1 <<EVENT_DETAIL>> {0:1} p.29
#    |
#    n EVEN {1:1}
#    +1 <<EVENT_DETAIL>> {0:1} p.29
#    ]

    FAMILY_EVENTS = set([
        EventType.ANNULMENT,
        EventType.CENSUS,
        EventType.DIVORCE,
        EventType.DIV_FILING,
        EventType.ENGAGEMENT,
        EventType.MARRIAGE,
        EventType.MARR_BANNS,
        EventType.MARR_CONTR,
        EventType.MARR_LIC,
        EventType.MARR_SETTL,
        EventType.CUSTOM])

    def __init__(self, dbstate, user, options_class, name, callback=None):
        uistate = user.uistate
        if uistate:
            parent_window = uistate.window
        else:
            parent_window = None
        self.progress = user.progress

# ******** This ensures that a chunk of code below never executes!!!!
        self.person = None

        if dbstate.db.readonly:
            return

        tool.BatchTool.__init__(self, dbstate, user, options_class, name,
                                parent=parent_window)

        if self.fail:
            return

        self.options_dict = self.options.handler.options_dict
        self.person_count = 0
        self.max_person_count = self.options_dict['person_count']
        self.persons_todo = []
        self.parents_todo = []
        self.person_dates = {}
        self.generated_repos = []
        self.generated_sources = []
        self.generated_citations = []
        self.generated_media = []
        self.generated_places = []
        self.generated_events = []
        self.generated_families = []
        self.generated_notes = []
        self.generated_tags = []
        self.text_serial_number = 1
        self.trans = None

        self.parent_places = {}
        for type_num in range(1, 8):
            self.parent_places[type_num] = []

        # If an active persons exists the generated tree is connected to that
        # person
        if self.person:
            # try to get birth and death year
            try:
                birth_h = self.person.get_birth_handle()
                birth_e = self.db.get_event_from_handle(birth_h)
                dat_o = birth_e.get_date_object()
                birth = dat_o.get_year()
            except AttributeError:
                birth = None
            try:
                death_h = self.person.get_death_handle()
                death_e = self.db.get_event_from_handle(death_h)
                dat_o = death_e.get_date_object()
                death = dat_o.get_year()
            except AttributeError:
                death = None
            if not birth and not death:
                birth = _randint(1700, 1900)
            if birth and not death:
                death = birth + _randint(20, 90)
            if death and not birth:
                birth = death - _randint(20, 90)
            self.person_dates[self.person.get_handle()] = (birth, death)

            self.persons_todo.append(self.person.get_handle())
            self.parents_todo.append(self.person.get_handle())

        if uistate:
            self.init_gui(uistate)
        else:
            self.run_tool(cli=True)

    def init_gui(self, uistate):
        title = "%s - Gramps" % _("Generate testcases")
        self.top = Gtk.Dialog(title, parent=uistate.window)
        self.window = uistate.window
        self.top.set_default_size(400, 150)
        self.top.vbox.set_spacing(5)
        label = Gtk.Label(label='<span size="larger" weight="bold">%s</span>'
                          % _("Generate testcases"))
        label.set_use_markup(True)
        self.top.vbox.pack_start(label, 0, 0, 5)

        self.check_lowlevel = Gtk.CheckButton(label=_(
            "Generate low level database "
            "errors\nCorrection needs database reload"))
        self.check_lowlevel.set_active(self.options_dict['lowlevel'])
        self.top.vbox.pack_start(self.check_lowlevel, 0, 0, 5)

        self.check_bugs = Gtk.CheckButton(label=_("Generate database errors"))
        self.check_bugs.set_active(self.options_dict['bugs'])
        self.top.vbox.pack_start(self.check_bugs, 0, 0, 5)

        self.check_persons = Gtk.CheckButton(label=_("Generate dummy data"))
        self.check_persons.set_active(self.options_dict['persons'])
        self.check_persons.connect('clicked', self.on_dummy_data_clicked)
        self.top.vbox.pack_start(self.check_persons, 0, 0, 5)

        self.check_longnames = Gtk.CheckButton(label=_("Generate long names"))
        self.check_longnames.set_active(self.options_dict['long_names'])
        self.top.vbox.pack_start(self.check_longnames, 0, 0, 5)

        self.check_specialchars = Gtk.CheckButton(label=_(
            "Add special characters"))
        self.check_specialchars.set_active(self.options_dict['specialchars'])
        self.top.vbox.pack_start(self.check_specialchars, 0, 0, 5)

        self.check_serial = Gtk.CheckButton(label=_("Add serial number"))
        self.check_serial.set_active(self.options_dict['add_serial'])
        self.top.vbox.pack_start(self.check_serial, 0, 0, 5)

        self.check_linebreak = Gtk.CheckButton(label=_("Add line break"))
        self.check_linebreak.set_active(self.options_dict['add_linebreak'])
        self.top.vbox.pack_start(self.check_linebreak, 0, 0, 5)

        self.label = Gtk.Label(label=_(
            "Number of people to generate\n"
            "(Number is approximate because families are generated)"))
        self.label.set_halign(Gtk.Align.START)
        self.top.vbox.pack_start(self.label, 0, 0, 5)

        self.entry_count = Gtk.Entry()
        self.entry_count.set_text(str(self.max_person_count))
        self.on_dummy_data_clicked(self.check_persons)
        self.top.vbox.pack_start(self.entry_count, 0, 0, 5)

        self.top.add_button(_('_Cancel'), Gtk.ResponseType.CANCEL)
        self.top.add_button(_('_OK'), Gtk.ResponseType.OK)
        self.top.add_button(_('_Help'), Gtk.ResponseType.HELP)
        self.top.show_all()

        while True:
            response = self.top.run()
            if response == Gtk.ResponseType.HELP:
                display_help(webpage=WIKI_HELP_PAGE,
                             section=WIKI_HELP_SEC)
            else:
                break
        self.options_dict['lowlevel'] = int(
            self.check_lowlevel.get_active())
        self.options_dict['bugs'] = int(
            self.check_bugs.get_active())
        self.options_dict['persons'] = int(
            self.check_persons.get_active())
        self.options_dict['long_names'] = int(
            self.check_longnames.get_active())
        self.options_dict['specialchars'] = int(
            self.check_specialchars.get_active())
        self.options_dict['add_serial'] = int(
            self.check_serial.get_active())
        self.options_dict['add_linebreak'] = int(
            self.check_linebreak.get_active())
        self.options_dict['person_count'] = int(
            self.entry_count.get_text())
        self.top.destroy()

        if response == Gtk.ResponseType.OK:
            self.run_tool(cli=False)
            # Save options
            self.options.handler.save_options()

    def on_dummy_data_clicked(self, obj):
        self.label.set_sensitive(obj.get_active())
        self.entry_count.set_sensitive(obj.get_active())

    def run_tool(self, cli=False):
        self.cli = cli
        if not cli:
            while Gtk.events_pending():
                Gtk.main_iteration()
        else:
            self.window = None

        self.transaction_count = 0

        if self.options_dict['lowlevel']:
            with self.progress(_('Generating testcases'),
                               _('Generating low level database errors'),
                               1) as step:
                self.test_low_level()
                step()

        if self.options_dict['bugs'] or self.options_dict['persons']:
            self.generate_tags()

        if self.options_dict['bugs']:
            with self.progress(_('Generating testcases'),
                               _('Generating database errors'),
                               20) as step:
                self.generate_data_errors(step)

        if self.options_dict['persons']:
            with self.progress(_('Generating testcases'),
                               _('Generating families'),
                               self.max_person_count) \
                               as self.progress_step:
                self.person_count = 0

                while True:
                    if not self.persons_todo:
                        pers_h = self.generate_person(0)
                        self.persons_todo.append(pers_h)
                        self.parents_todo.append(pers_h)
                    person_h = self.persons_todo.pop(0)
                    self.generate_family(person_h)
                    if _randint(0, 3) == 0:
                        self.generate_family(person_h)
                    if _randint(0, 7) == 0:
                        self.generate_family(person_h)
                    if self.person_count > self.max_person_count:
                        break
                    for child_h in self.parents_todo:
                        self.generate_parents(child_h)
                        if self.person_count > self.max_person_count:
                            break

        if not cli:
            self.top.destroy()

    def generate_data_errors(self, step):
        """This generates errors in the database to test src/plugins/tool/Check
        The module names correspond to the checking methods in
        src/plugins/tool/Check.CheckIntegrity """
        # The progress meter is normally stepped every time a person is
        # generated by generate_person. However in this case, generate_person
        # is called by some of the constituent functions, but we only want the
        # meter to be stepped every time a test function has been completed.
        self.progress_step = lambda: None

        self.test_fix_encoding()
        step()
        self.test_fix_ctrlchars_in_notes()
        step()
        self.test_fix_alt_place_names()
        step()
        self.test_fix_duplicated_grampsid()
        step()
        self.test_clean_deleted_name_format()
        step()
        self.test_cleanup_empty_objects()
        step()
        self.test_chk_for_broke_family_link()
        step()
        self.test_check_parent_relationships()
        step()
        self.test_cleanup_empty_families()
        step()
        self.test_cleanup_duplicate_spouses()
        step()
        self.test_check_events()
        step()
        self.test_check_person_references()
        step()
        self.test_check_family_references()
        step()
        self.test_check_place_references()
        step()
        self.test_check_source_references()
        step()
        self.test_check_citation_references()
        step()
        self.test_check_media_references()
        step()
        self.test_check_repo_references()
        step()
        self.test_check_note_references()
        step()

    def test_low_level(self):
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1

            obj = Note()
            obj.set("dup 1" + self.rand_text(self.NOTE))
            obj.set_format(_choice((Note.FLOWED, Note.FORMATTED)))
            obj.set_type(self.rand_type(NoteType()))
            self.db.add_note(obj, self.trans)
            print("object %s, handle %s, Gramps_Id %s" % (obj, obj.handle,
                                                          obj.gramps_id))

            handle = obj.get_handle()

            src = Source()
            src.set_title("dup 2" + self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                src.set_author(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                src.set_publication_info(self.rand_text(self.LONG))
            if _randint(0, 1) == 1:
                src.set_abbreviation(self.rand_text(self.SHORT))
            while _randint(0, 1) == 1:
                sattr = SrcAttribute()
                sattr.set_type(self.rand_text(self.SHORT))
                sattr.set_value(self.rand_text(self.SHORT))
                src.add_attribute(sattr)
            src.set_handle(handle)
            self.db.add_source(src, self.trans)
            print("object %s, handle %s, Gramps_Id %s" % (src, src.handle,
                                                          src.gramps_id))

    def test_fix_encoding(self):
        """ Creates a media object with character encoding errors. This tests
        Check.fix_encoding() and also cleanup_missing_photos
        """
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1

            med = Media()
            self.fill_object(med)
            med.set_description("leave this media object invalid description"
                                "\x9f")
            med.set_path("/tmp/click_on_keep_reference.png\x9f")
            med.set_mime_type("image/png\x9f")
            self.db.add_media(med, self.trans)

            med = Media()
            self.fill_object(med)
            med.set_description("reselect this media object invalid "
                                "description\x9f")
            med.set_path("/tmp/click_on_select_file.png\x9f")
            med.set_mime_type("image/png\x9f")
            self.db.add_media(med, self.trans)

            # setup media attached to Source and Citation to be removed

            med = Media()
            self.fill_object(med)
            med.set_description('remove this media object')
            med.set_path("/tmp/click_on_remove_object.png")
            med.set_mime_type("image/png")
            self.db.add_media(med, self.trans)

            src = Source()
            src.set_title('media should be removed from this source')
            ref = MediaRef()
            ref.set_reference_handle(med.handle)
            src.add_media_reference(ref)
            self.db.add_source(src, self.trans)

            cit = Citation()
            self.fill_object(cit)
            cit.set_reference_handle(src.handle)
            cit.set_page('media should be removed from this citation')
            ref = MediaRef()
            ref.set_reference_handle(med.handle)
            cit.add_media_reference(ref)
            self.db.add_citation(cit, self.trans)

    def test_fix_ctrlchars_in_notes(self):
        """ Creates a note with control characters. This tests
        Check.fix_ctrlchars_in_notes()
        """
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1

            obj = Note()
            obj.set("This is a text note with a \x03 control character")
            obj.set_format(_choice((Note.FLOWED, Note.FORMATTED)))
            obj.set_type(self.rand_type(NoteType()))
            self.db.add_note(obj, self.trans)

    def test_fix_alt_place_names(self):
        """
        Creates a place with a duplicate of primary in alt_names,
        a blank alt_name, and a duplicate of one of the alt_names. Also
        include two alt names that are almost duplicates, but not quite.
        This tests Check.fix_alt_place_names()
        """
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1

            plac = Place()
            pri_name = PlaceName()
            pri_name.set_value("Primary name")
            alt_name1 = PlaceName()
            alt_name1.set_value("Alt name 1")
            alt_name2 = PlaceName()
            alt_name2.set_value("Alt name 1")
            alt_name2.set_language("testish")
            alt_name3 = PlaceName()
            alt_name3.set_value("Alt name 1")
            alt_name3.set_date_object(Today())
            alt_names = [pri_name, alt_name1, alt_name1, PlaceName(),
                         alt_name2, alt_name3]
            plac.set_name(pri_name)
            plac.set_alternative_names(alt_names)
            self.db.add_place(plac, self.trans)

    def test_fix_duplicated_grampsid(self):
        """
        Create some duplicate Gramps IDs in various object types
        This tests Check.fix_duplicated_grampsid()
        """
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            for dummy in range(0, 2):
                cit = Citation()
                self.fill_object(cit)
                cit.set_gramps_id("C1001")
                self.db.add_citation(cit, self.trans)

                evt = Event()
                self.fill_object(evt)
                evt.set_gramps_id("E1001")
                self.db.add_event(evt, self.trans)

                person1_h = self.generate_person(
                    Person.MALE, "Smith",
                    "Dup Gramps ID test F1001")
                person2_h = self.generate_person(Person.FEMALE, "Jones", None)
                fam = Family()
                fam.set_father_handle(person1_h)
                fam.set_mother_handle(person2_h)
                fam.set_relationship((FamilyRelType.MARRIED, ''))
                fam.set_gramps_id("F1001")
                fam_h = self.db.add_family(fam, self.trans)
                person1 = self.db.get_person_from_handle(person1_h)
                person1.add_family_handle(fam_h)
                self.db.commit_person(person1, self.trans)
                person2 = self.db.get_person_from_handle(person2_h)
                person2.add_family_handle(fam_h)
                self.db.commit_person(person2, self.trans)

                med = Media()
                self.fill_object(med)
                med.set_gramps_id("O1001")
                self.db.add_media(med, self.trans)

                note = Note()
                self.fill_object(note)
                note.set_gramps_id("N1001")
                self.db.add_note(note, self.trans)

                person1_h = self.generate_person(Person.MALE, "Smith",
                                                 "Dup GID test GID I1001")
                person1 = self.db.get_person_from_handle(person1_h)
                person1.set_gramps_id("I1001")
                self.db.commit_person(person1, self.trans)

                place = Place()
                self.fill_object(place)
                place.set_gramps_id("P1001")
                self.db.add_place(place, self.trans)

                rep = Repository()
                self.fill_object(rep)
                rep.set_gramps_id("R1001")
                self.db.add_repository(rep, self.trans)

                src = Source()
                self.fill_object(src)
                src.set_gramps_id("S1001")
                self.db.add_source(src, self.trans)

    def test_cleanup_missing_photos(self):
        pass

    def test_clean_deleted_name_format(self):
        pass

    def test_cleanup_empty_objects(self):
        """ Generate empty objects to test their deletion """
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1

            pers = Person()
            self.db.add_person(pers, self.trans)

            fam = Family()
            self.db.add_family(fam, self.trans)

            evt = Event()
            self.db.add_event(evt, self.trans)

            place = Place()
            self.db.add_place(place, self.trans)

            src = Source()
            self.db.add_source(src, self.trans)

            cit = Citation()
            self.db.add_citation(cit, self.trans)

            med = Media()
            self.db.add_media(med, self.trans)

            ref = Repository()
            self.db.add_repository(ref, self.trans)

            note = Note()
            self.db.add_note(note, self.trans)

    def test_chk_for_broke_family_link(self):
        """ Create various family related errors """
        # Create a family, that links to father and mother, but father does not
        # link back
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(
                Person.MALE, "Broken1",
                "Family links to this person, but person does not link back")
            person2_h = self.generate_person(Person.FEMALE, "Broken1", None)
            fam = Family()
            fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            fam.set_relationship((FamilyRelType.MARRIED, ''))
            fam_h = self.db.add_family(fam, self.trans)
            # person1 = self.db.get_person_from_handle(person1_h)
            # person1.add_family_handle(fam_h)
            # self.db.commit_person(person1, self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle(fam_h)
            self.db.commit_person(person2, self.trans)

        # Create a family, that misses the link to the father
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(Person.MALE, "Broken2", None)
            person2_h = self.generate_person(Person.FEMALE, "Broken2", None)
            fam = Family()
            # fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            fam.set_relationship((FamilyRelType.MARRIED, ''))
            fam_h = self.db.add_family(fam, self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle(fam_h)
            self.db.commit_person(person1, self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle(fam_h)
            self.db.commit_person(person2, self.trans)

        # Create a family, that misses the link to the mother
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(Person.MALE, "Broken3", None)
            person2_h = self.generate_person(Person.FEMALE, "Broken3", None)
            fam = Family()
            fam.set_father_handle(person1_h)
            # fam.set_mother_handle(person2_h)
            fam.set_relationship((FamilyRelType.MARRIED, ''))
            fam_h = self.db.add_family(fam, self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle(fam_h)
            self.db.commit_person(person1, self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle(fam_h)
            self.db.commit_person(person2, self.trans)

        # Create a family, that links to father and mother, but mother does not
        # link back
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(Person.MALE, "Broken4", None)
            person2_h = self.generate_person(
                Person.FEMALE, "Broken4",
                "Family links to this person, but person does not link back")
            fam = Family()
            fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            fam.set_relationship((FamilyRelType.MARRIED, ''))
            fam_h = self.db.add_family(fam, self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle(fam_h)
            self.db.commit_person(person1, self.trans)
            # person2 = self.db.get_person_from_handle(person2_h)
            # person2.add_family_handle(fam_h)
            # self.db.commit_person(person2, self.trans)

        # Create two married people of same sex.
        # This is NOT detected as an error by plugins/tool/Check.py
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(Person.MALE, "Broken5", None)
            person2_h = self.generate_person(Person.MALE, "Broken5", None)
            fam = Family()
            fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            fam.set_relationship((FamilyRelType.MARRIED, ''))
            fam_h = self.db.add_family(fam, self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle(fam_h)
            self.db.commit_person(person1, self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle(fam_h)
            self.db.commit_person(person2, self.trans)

        # Create a family, that contains an invalid handle to for the father
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            # person1_h = self.generate_person(Person.MALE, "Broken6", None)
            person2_h = self.generate_person(Person.FEMALE, "Broken6", None)
            fam = Family()
            fam.set_father_handle("InvalidHandle1")
            fam.set_mother_handle(person2_h)
            fam.set_relationship((FamilyRelType.MARRIED, ''))
            fam_h = self.db.add_family(fam, self.trans)
            # person1 = self.db.get_person_from_handle(person1_h)
            # person1.add_family_handle(fam_h)
            # self.db.commit_person(person1, self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle(fam_h)
            self.db.commit_person(person2, self.trans)

        # Create a family, that contains an invalid handle to for the mother
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(Person.MALE, "Broken7", None)
            # person2_h = self.generate_person(Person.FEMALE, "Broken7", None)
            fam = Family()
            fam.set_father_handle(person1_h)
            fam.set_mother_handle("InvalidHandle2")
            fam.set_relationship((FamilyRelType.MARRIED, ''))
            fam_h = self.db.add_family(fam, self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle(fam_h)
            self.db.commit_person(person1, self.trans)
            # person2 = self.db.get_person_from_handle(person2_h)
            # person2.add_family_handle(fam_h)
            # self.db.commit_person(person2, self.trans)

        # Creates a family where the child does not link back to the family
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(Person.MALE, "Broken8", None)
            person2_h = self.generate_person(Person.FEMALE, "Broken8", None)
            child_h = self.generate_person(None, "Broken8", None)
            fam = Family()
            fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            fam.set_relationship((FamilyRelType.MARRIED, ''))
            child_ref = ChildRef()
            child_ref.set_reference_handle(child_h)
            self.fill_object(child_ref)
            fam.add_child_ref(child_ref)
            fam_h = self.db.add_family(fam, self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle(fam_h)
            self.db.commit_person(person1, self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle(fam_h)
            self.db.commit_person(person2, self.trans)
            # child = self.db.get_person_from_handle(child_h)
            # person2.add_parent_family_handle(fam_h)
            # self.db.commit_person(child, self.trans)

        # Creates a family where the child is not linked, but the child links
        # to the family
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(Person.MALE, "Broken9", None)
            person2_h = self.generate_person(Person.FEMALE, "Broken9", None)
            child_h = self.generate_person(None, "Broken9", None)
            fam = Family()
            fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            fam.set_relationship((FamilyRelType.MARRIED, ''))
            # child_ref = ChildRef()
            # child_ref.set_reference_handle(child_h)
            # self.fill_object(child_ref)
            # fam.add_child_ref(child_ref)
            fam_h = self.db.add_family(fam, self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle(fam_h)
            self.db.commit_person(person1, self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle(fam_h)
            self.db.commit_person(person2, self.trans)
            child = self.db.get_person_from_handle(child_h)
            child.add_parent_family_handle(fam_h)
            self.db.commit_person(child, self.trans)

        # Creates a family where the child is one of the parents
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(Person.MALE, "Broken19", None)
            person2_h = self.generate_person(Person.FEMALE, "Broken19", None)
            child_h = person2_h
            fam = Family()
            fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            fam.set_relationship((FamilyRelType.MARRIED, ''))
            child_ref = ChildRef()
            child_ref.set_reference_handle(child_h)
            self.fill_object(child_ref)
            fam.add_child_ref(child_ref)
            fam_h = self.db.add_family(fam, self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle(fam_h)
            self.db.commit_person(person1, self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle(fam_h)
            self.db.commit_person(person2, self.trans)
            child = self.db.get_person_from_handle(child_h)
            child.add_parent_family_handle(fam_h)
            self.db.commit_person(child, self.trans)

        # Creates a couple that refer to a family that does not exist in the
        # database.
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person1_h = self.generate_person(Person.MALE, "Broken20", None)
            person2_h = self.generate_person(Person.FEMALE, "Broken20", None)
#            fam = Family()
#            fam.set_father_handle(person1_h)
#            fam.set_mother_handle(person2_h)
#            fam.set_relationship((FamilyRelType.MARRIED, ''))
#            child_ref = ChildRef()
#            # child_ref.set_reference_handle(child_h)
#            # self.fill_object(child_ref)
#            # fam.add_child_ref(child_ref)
#            fam_h = self.db.add_family(fam, self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle("InvalidHandle3")
            self.db.commit_person(person1, self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle("InvalidHandle3")
            self.db.commit_person(person2, self.trans)
#            child = self.db.get_person_from_handle(child_h)
#            child.add_parent_family_handle(fam_h)
#            self.db.commit_person(child, self.trans)

    def test_check_parent_relationships(self):
        pass

    def test_cleanup_empty_families(self):
        pass

    def test_cleanup_duplicate_spouses(self):
        pass

    def test_check_events(self):
        """ Various event related tests """
        # Creates a person having a non existing birth event handle set
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None, "Broken11", None)
            person = self.db.get_person_from_handle(person_h)
            event_ref = EventRef()
            event_ref.set_reference_handle("InvalidHandle4")
            person.set_birth_ref(event_ref)
            self.db.commit_person(person, self.trans)

        # Creates a person having a non existing death event handle set
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None, "Broken12", None)
            person = self.db.get_person_from_handle(person_h)
            event_ref = EventRef()
            event_ref.set_reference_handle("InvalidHandle5")
            person.set_death_ref(event_ref)
            self.db.commit_person(person, self.trans)

        # Creates a person having a non existing event handle set
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None, "Broken13", None)
            person = self.db.get_person_from_handle(person_h)
            event_ref = EventRef()
            event_ref.set_reference_handle("InvalidHandle6")
            person.add_event_ref(event_ref)
            self.db.commit_person(person, self.trans)

        # Creates a person with a birth event having an empty type
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None, "Broken14", None)
            event = Event()
            # The default type _DEFAULT = BIRTH is set in eventtype
            event.set_type('')
            event.set_description("Test for Broken14")
            event_h = self.db.add_event(event, self.trans)
            event_ref = EventRef()
            event_ref.set_reference_handle(event_h)
            person = self.db.get_person_from_handle(person_h)
            person.set_birth_ref(event_ref)
            self.db.commit_person(person, self.trans)

        # Creates a person with a death event having an empty type
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None, "Broken15", None)
            event = Event()
            # The default type _DEFAULT = BIRTH is set in eventtype
            event.set_type('')
            event.set_description("Test for Broken15")
            event_h = self.db.add_event(event, self.trans)
            event_ref = EventRef()
            event_ref.set_reference_handle(event_h)
            person = self.db.get_person_from_handle(person_h)
            person.set_death_ref(event_ref)
            self.db.commit_person(person, self.trans)

        # Creates a person with an event having an empty type
        # This is NOT detected as an error by plugins/tool/Check.py
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None, "Broken16", None)
            event = Event()
            # The default type _DEFAULT = BIRTH is set in eventtype
            event.set_type('')
            event.set_description("Test for Broken16")
            event_h = self.db.add_event(event, self.trans)
            event_ref = EventRef()
            event_ref.set_reference_handle(event_h)
            person = self.db.get_person_from_handle(person_h)
            person.add_event_ref(event_ref)
            self.db.commit_person(person, self.trans)

    def test_check_person_references(self):
        pass

    def test_check_family_references(self):
        pass

    def test_check_place_references(self):
        """ Tests various place reference errors """
        # Creates a person with a birth event pointing to nonexisting place
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None, "Broken17", None)
            event = Event()
            event.set_type(EventType.BIRTH)
            event.set_place_handle("InvalidHandle7")
            event.set_description("Test for Broken17")
            event_h = self.db.add_event(event, self.trans)
            event_ref = EventRef()
            event_ref.set_reference_handle(event_h)
            person = self.db.get_person_from_handle(person_h)
            person.set_birth_ref(event_ref)
            self.db.commit_person(person, self.trans)

        # Creates a person with an event pointing to nonexisting place
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            person_h = self.generate_person(None, "Broken18", None)
            event = Event()
            event.set_type(EventType.BIRTH)
            event.set_place_handle("InvalidHandle8")
            event.set_description("Test for Broken18")
            event_h = self.db.add_event(event, self.trans)
            event_ref = EventRef()
            event_ref.set_reference_handle(event_h)
            person = self.db.get_person_from_handle(person_h)
            person.add_event_ref(event_ref)
            self.db.commit_person(person, self.trans)

    def test_check_source_references(self):
        """ Tests various source reference errors """
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1

            cit = Citation()
            self.fill_object(cit)
            cit.set_reference_handle("unknownsourcehandle")
            cit.set_page('unreferenced citation with invalid source ref')
            self.db.add_citation(cit, self.trans)

            cit = Citation()
            self.fill_object(cit)
            cit.set_reference_handle(None)
            cit.set_page('unreferenced citation with invalid source ref')
            self.db.add_citation(cit, self.trans)

            cit = Citation()
            self.fill_object(cit)
            cit.set_reference_handle("unknownsourcehandle")
            cit.set_page('citation and references to it should be removed')
            c_h1 = self.db.add_citation(cit, self.trans)

            cit = Citation()
            self.fill_object(cit)
            cit.set_reference_handle(None)
            cit.set_page('citation and references to it should be removed')
            c_h2 = self.db.add_citation(cit, self.trans)

            self.create_all_possible_citations([c_h1, c_h2], "Broken21",
                                               'non-existent source')

    def test_check_citation_references(self):
        """ Generate objects that refer to non-existant citations """
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1

            c_h = "unknowncitationhandle"
            self.create_all_possible_citations([c_h, ''], "Broken22",
                                               'non-existent citation')

    def create_all_possible_citations(self, c_h_list, name, message):
        """ Create citations attached to each of the following objects:
            Person
             Name
             Address
             Attribute
             PersonRef
             MediaRef
              Attribute
             LdsOrd

            Family
             Attribute
             ChildRef
             MediaRef
              Attribute
             LdsOrd

            Event
             Attribute
             MediaRef
              Attribute

            Media
             Attribute

            Place
             MediaRef
              Attribute

            Repository (Repositories themselves do not have SourceRefs)
             Address
        """
        med = Media()
        med.set_description(message)
        med.set_path(os.path.abspath(str(ICON)))
        med.set_mime_type(get_type(med.get_path()))
        med.add_citation(_choice(c_h_list))
        # Media : Attribute
        att = Attribute()
        att.set_type(self.rand_type(AttributeType()))
        att.set_value(message)
        att.add_citation(_choice(c_h_list))
        med.add_attribute(att)
        self.db.add_media(med, self.trans)

        person1_h = self.generate_person(Person.MALE, name, None)
        person2_h = self.generate_person(Person.FEMALE, name, None)
        child_h = self.generate_person(None, name, None)
        fam = Family()
        fam.set_father_handle(person1_h)
        fam.set_mother_handle(person2_h)
        fam.set_relationship((FamilyRelType.MARRIED, ''))
        # Family
        fam.add_citation(_choice(c_h_list))
        # Family : Attribute
        att = Attribute()
        att.set_type(self.rand_type(AttributeType()))
        att.set_value(message)
        att.add_citation(_choice(c_h_list))
        fam.add_attribute(att)
        # Family : ChildRef
        child_ref = ChildRef()
        child_ref.set_reference_handle(child_h)
        self.fill_object(child_ref)
        child_ref.add_citation(_choice(c_h_list))
        fam.add_child_ref(child_ref)
        # Family : MediaRef
        mref = MediaRef()
        mref.set_reference_handle(med.handle)
        mref.add_citation(_choice(c_h_list))
        # Family : MediaRef : Attribute
        att = Attribute()
        att.set_type(self.rand_type(AttributeType()))
        att.set_value(message)
        att.add_citation(_choice(c_h_list))
        mref.add_attribute(att)
        fam.add_media_reference(mref)
        # Family : LDSORD
        ldsord = LdsOrd()
        self.fill_object(ldsord)
        # TODO: adapt type and status to family/person
        # if isinstance(obj, Person):
        # if isinstance(obj, Family):
        # pylint: disable=protected-access
        ldsord.set_type(_choice([item[0] for item in LdsOrd._TYPE_MAP]))
        ldsord.set_status(_randint(0, len(LdsOrd._STATUS_MAP) - 1))
        ldsord.add_citation(_choice(c_h_list))
        fam.add_lds_ord(ldsord)
        # Family : EventRef
        evt = Event()
        evt.set_type(EventType.MARRIAGE)
        (dummy, date) = self.rand_date()
        evt.set_date_object(date)
        evt.set_description(message)
        event_h = self.db.add_event(evt, self.trans)
        eref = EventRef()
        eref.set_reference_handle(event_h)
        eref.set_role(self.rand_type(EventRoleType()))
        # Family : EventRef : Attribute
        att = Attribute()
        att.set_type(self.rand_type(AttributeType()))
        att.set_value(message)
        att.add_citation(_choice(c_h_list))
        eref.add_attribute(att)
        fam.add_event_ref(eref)
        fam_h = self.db.add_family(fam, self.trans)
        person1 = self.db.get_person_from_handle(person1_h)
        person1.add_family_handle(fam_h)
        # Person
        person1.add_citation(_choice(c_h_list))
        # Person : Name
        alt_name = Name(person1.get_primary_name())
        alt_name.set_first_name(message)
        alt_name.add_citation(_choice(c_h_list))
        person1.add_alternate_name(alt_name)
        # Person : Address
        add = Address()
        add.set_street(message)
        add.add_citation(_choice(c_h_list))
        person1.add_address(add)
        # Person : Attribute
        att = Attribute()
        att.set_type(self.rand_type(AttributeType()))
        att.set_value(message)
        att.add_citation(_choice(c_h_list))
        person1.add_attribute(att)
        # Person : PersonRef
        asso_h = self.generate_person()
        asso = PersonRef()
        asso.set_reference_handle(asso_h)
        asso.set_relation(self.rand_text(self.SHORT))
        self.fill_object(asso)
        asso.add_citation(_choice(c_h_list))
        person1.add_person_ref(asso)
        # Person : MediaRef
        mref = MediaRef()
        mref.set_reference_handle(med.handle)
        mref.add_citation(_choice(c_h_list))
        # Person : MediaRef : Attribute
        att = Attribute()
        att.set_type(self.rand_type(AttributeType()))
        att.set_value(self.rand_text(self.SHORT))
        att.add_citation(_choice(c_h_list))
        mref.add_attribute(att)
        person1.add_media_reference(mref)
        # Person : LDSORD
        ldsord = LdsOrd()
        self.fill_object(ldsord)
        # TODO: adapt type and status to family/person
        # if isinstance(obj, Person):
        # if isinstance(obj, Family):
        ldsord.set_type(_choice(
            [item[0] for item in LdsOrd._TYPE_MAP]))
        ldsord.set_status(_randint(0, len(LdsOrd._STATUS_MAP) - 1))
        ldsord.add_citation(_choice(c_h_list))
        person1.add_lds_ord(ldsord)
        # Person : EventRef
        evt = Event()
        evt.set_type(EventType.ELECTED)
        (dummy, dat) = self.rand_date()
        evt.set_date_object(dat)
        evt.set_description(message)
        event_h = self.db.add_event(evt, self.trans)
        eref = EventRef()
        eref.set_reference_handle(event_h)
        eref.set_role(self.rand_type(EventRoleType()))
        # Person : EventRef : Attribute
        att = Attribute()
        att.set_type(self.rand_type(AttributeType()))
        att.set_value(message)
        att.add_citation(_choice(c_h_list))
        eref.add_attribute(att)
        person1.add_event_ref(eref)
        self.db.commit_person(person1, self.trans)
        person2 = self.db.get_person_from_handle(person2_h)
        person2.add_family_handle(fam_h)
        self.db.commit_person(person2, self.trans)

        evt = Event()
        evt.set_description(message)
        evt.set_type(EventType.MARRIAGE)
        # Event
        evt.add_citation(_choice(c_h_list))
        # Event : Attribute
        att = Attribute()
        att.set_type(self.rand_type(AttributeType()))
        att.set_value(message)
        att.add_citation(_choice(c_h_list))
        evt.add_attribute(att)
        # Event : MediaRef
        mref = MediaRef()
        mref.set_reference_handle(med.handle)
        mref.add_citation(_choice(c_h_list))
        # Event : MediaRef : Attribute
        att = Attribute()
        att.set_type(self.rand_type(AttributeType()))
        att.set_value(self.rand_text(self.SHORT))
        att.add_citation(_choice(c_h_list))
        mref.add_attribute(att)
        evt.add_media_reference(mref)
        self.db.add_event(evt, self.trans)

        place = Place()
        place.set_title(message)
        place.add_citation(_choice(c_h_list))
        # Place : MediaRef
        mref = MediaRef()
        mref.set_reference_handle(med.handle)
        mref.add_citation(_choice(c_h_list))
        # Place : MediaRef : Attribute
        att = Attribute()
        att.set_type(self.rand_type(AttributeType()))
        att.set_value(self.rand_text(self.SHORT))
        att.add_citation(_choice(c_h_list))
        mref.add_attribute(att)
        place.add_media_reference(mref)
        self.db.add_place(place, self.trans)

        ref = Repository()
        ref.set_name(message)
        ref.set_type(RepositoryType.LIBRARY)
        # Repository : Address
        add = Address()
        add.set_street(message)
        add.add_citation(_choice(c_h_list))
        ref.add_address(add)
        self.db.add_repository(ref, self.trans)

    def test_check_media_references(self):
        pass

    def test_check_repo_references(self):
        pass

    def test_check_note_references(self):
        pass

    def generate_person(self, gender=None, lastname=None, note=None,
                        alive_in_year=None):
        """ This generates a person with lots of attachments """
        if not self.cli:
            if self.person_count % 10 == 0:
                while Gtk.events_pending():
                    Gtk.main_iteration()

        pers = Person()
        self.fill_object(pers)

        # Gender
        if gender is None:
            gender = _randint(0, 1)
        if _randint(0, 10) == 1:  # Set some persons to unknown gender
            pers.set_gender(Person.UNKNOWN)
        else:
            pers.set_gender(gender)

        # Name
        name = Name()
        (firstname, lastname) = self.rand_name(lastname, gender)
        name.set_first_name(firstname)
        surname = Surname()
        surname.set_surname(lastname)
        name.add_surname(surname)
        self.fill_object(name)
        pers.set_primary_name(name)

        # generate some slightly different alternate name
        firstname2 = \
            firstname.replace("m", "n").replace("l", "i").replace("b", "d")
        if firstname2 != firstname:
            alt_name = Name(name)
            self.fill_object(alt_name)
            if _randint(0, 2) == 1:
                surname = Surname()
                surname.set_surname(self.rand_text(self.LASTNAME))
                alt_name.add_surname(surname)
            elif _randint(0, 2) == 1:
                surname = Surname()
                surname.set_surname(lastname)
                alt_name.add_surname(surname)
            if _randint(0, 1) == 1:
                alt_name.set_first_name(firstname2)
            if _randint(0, 1) == 1:
                alt_name.set_title(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                patronymic = Surname()
                patronymic.set_surname(self.rand_text(self.FIRSTNAME_MALE))
                patronymic.set_origintype(NameOriginType.PATRONYMIC)
                alt_name.add_surname(patronymic)
            if _randint(0, 1) == 1:
                alt_name.get_primary_surname().set_prefix(
                    self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                alt_name.set_suffix(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                alt_name.set_call_name(self.rand_text(self.FIRSTNAME))
            pers.add_alternate_name(alt_name)
        firstname2 = \
            firstname.replace("a", "e").replace("o", "u").replace("r", "p")
        if firstname2 != firstname:
            alt_name = Name(name)
            self.fill_object(alt_name)
            if _randint(0, 2) == 1:
                surname = Surname()
                surname.set_surname(self.rand_text(self.LASTNAME))
                alt_name.add_surname(surname)
            elif _randint(0, 2) == 1:
                surname = Surname()
                surname.set_surname(lastname)
                alt_name.add_surname(surname)
            if _randint(0, 1) == 1:
                alt_name.set_first_name(firstname2)
            if _randint(0, 1) == 1:
                alt_name.set_title(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                patronymic = Surname()
                patronymic.set_surname(self.rand_text(self.FIRSTNAME_MALE))
                patronymic.set_origintype(NameOriginType.PATRONYMIC)
                alt_name.add_surname(patronymic)
            if _randint(0, 1) == 1:
                alt_name.get_primary_surname().set_prefix(
                    self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                alt_name.set_suffix(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                alt_name.set_call_name(self.rand_text(self.FIRSTNAME))
            pers.add_alternate_name(alt_name)

        if not alive_in_year:
            alive_in_year = _randint(1700, 2000)

        b_y = alive_in_year - _randint(0, 60)
        d_y = alive_in_year + _randint(0, 60)

        # birth
        if _randint(0, 1) == 1:
            (dummy, eref) = self.rand_personal_event(EventType.BIRTH, b_y, b_y)
            pers.set_birth_ref(eref)

        # baptism
        if _randint(0, 1) == 1:
            (dummy, eref) = self.rand_personal_event(
                _choice((EventType.BAPTISM, EventType.CHRISTEN)), b_y, b_y + 2)
            pers.add_event_ref(eref)

        # death
        if _randint(0, 1) == 1:
            (dummy, eref) = self.rand_personal_event(EventType.DEATH, d_y, d_y)
            pers.set_death_ref(eref)

        # burial
        if _randint(0, 1) == 1:
            (dummy, eref) = self.rand_personal_event(
                _choice((EventType.BURIAL, EventType.CREMATION)), d_y, d_y + 2)
            pers.add_event_ref(eref)

        # some other events
        while _randint(0, 5) == 1:
            (dummy, eref) = self.rand_personal_event(None, b_y, d_y)
            pers.add_event_ref(eref)

        # some shared events
        if self.generated_events:
            while _randint(0, 5) == 1:
                e_h = _choice(self.generated_events)
                eref = EventRef()
                self.fill_object(eref)
                eref.set_reference_handle(e_h)
                pers.add_event_ref(eref)

        # PersonRef
        if _randint(0, 3) == 1:
            for dummy in range(0, _randint(1, 2)):
                if self.person_count > self.max_person_count:
                    break
                if alive_in_year:
                    asso_h = self.generate_person(None, None,
                                                  alive_in_year=alive_in_year)
                else:
                    asso_h = self.generate_person()
                asso = PersonRef()
                asso.set_reference_handle(asso_h)
                asso.set_relation(self.rand_text(self.SHORT))
                self.fill_object(asso)
                pers.add_person_ref(asso)
                if _randint(0, 2) == 0:
                    self.persons_todo.append(asso_h)

        # Note
        if note:
            pass  # Add later?

        person_handle = self.db.add_person(pers, self.trans)

        self.person_count = self.person_count + 1
        self.progress_step()
        if self.person_count % 10 == 1:
            print("person count", self.person_count)
        self.person_dates[person_handle] = (b_y, d_y)

        return person_handle

    def generate_family(self, person1_h):
        """ Make up a family """
        person1 = self.db.get_person_from_handle(person1_h)
        if not person1:
            return
        alive_in_year = None
        if person1_h in self.person_dates:
            (born, died) = self.person_dates[person1_h]
            alive_in_year = min(born + _randint(10, 50),
                                died + _randint(-10, 10))

        if person1.get_gender() == 1:
            if _randint(0, 7) == 1:
                person2_h = None
            else:
                if alive_in_year:
                    person2_h = \
                        self.generate_person(0, alive_in_year=alive_in_year)
                else:
                    person2_h = self.generate_person(0)
        else:
            person2_h = person1_h
            if _randint(0, 7) == 1:
                person1_h = None
            else:
                if alive_in_year:
                    person1_h = \
                        self.generate_person(1, alive_in_year=alive_in_year)
                else:
                    person1_h = self.generate_person(1)

        if person1_h and _randint(0, 2) > 0:
            self.parents_todo.append(person1_h)
        if person2_h and _randint(0, 2) > 0:
            self.parents_todo.append(person2_h)

        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            fam = Family()
            self.add_defaults(fam)
            if person1_h:
                fam.set_father_handle(person1_h)
            if person2_h:
                fam.set_mother_handle(person2_h)

            # Avoid adding the same event more than once to the same family
            event_set = set()

            # Generate at least one family event with a probability of 75%
            if _randint(0, 3) > 0:
                (dummy, eref) = self.rand_family_event(None)
                fam.add_event_ref(eref)
                event_set.add(eref.get_reference_handle())

            # generate some more events with a lower probability
            while _randint(0, 3) == 1:
                (dummy, eref) = self.rand_family_event(None)
                if eref.get_reference_handle() in event_set:
                    continue
                fam.add_event_ref(eref)
                event_set.add(eref.get_reference_handle())

            # some shared events
            if self.generated_events:
                while _randint(0, 5) == 1:
                    typeval = EventType.UNKNOWN
                    while int(typeval) not in self.FAMILY_EVENTS:
                        e_h = _choice(self.generated_events)
                        typeval = self.db.get_event_from_handle(e_h).get_type()
                    if e_h in event_set:
                        break
                    eref = EventRef()
                    self.fill_object(eref)
                    eref.set_reference_handle(e_h)
                    fam.add_event_ref(eref)
                    event_set.add(e_h)

            fam_h = self.db.add_family(fam, self.trans)
            self.generated_families.append(fam_h)
            fam = self.db.commit_family(fam, self.trans)
            if person1_h:
                person1 = self.db.get_person_from_handle(person1_h)
                person1.add_family_handle(fam_h)
                self.db.commit_person(person1, self.trans)
            if person2_h:
                person2 = self.db.get_person_from_handle(person2_h)
                person2.add_family_handle(fam_h)
                self.db.commit_person(person2, self.trans)

            lastname = person1.get_primary_name().get_surname()

            for i in range(0, _randint(1, 10)):
                if self.person_count > self.max_person_count:
                    break
                if alive_in_year:
                    child_h = self.generate_person(
                        None, lastname,
                        alive_in_year=alive_in_year +
                        _randint(16 + 2 * i, 30 + 2 * i))
                else:
                    child_h = self.generate_person(None, lastname)
                    (born, died) = self.person_dates[child_h]
                    alive_in_year = born
                fam = self.db.get_family_from_handle(fam_h)
                child_ref = ChildRef()
                child_ref.set_reference_handle(child_h)
                self.fill_object(child_ref)
                fam.add_child_ref(child_ref)
                self.db.commit_family(fam, self.trans)
                child = self.db.get_person_from_handle(child_h)
                child.add_parent_family_handle(fam_h)
                self.db.commit_person(child, self.trans)
                if _randint(0, 3) > 0:
                    self.persons_todo.append(child_h)

    def generate_parents(self, child_h):
        """ Add parents to a person, if not present already"""
        if not child_h:
            return
        child = self.db.get_person_from_handle(child_h)
        if not child:
            print("ERROR: Person handle %s does not exist in database" %
                  child_h)
            return
        if child.get_parent_family_handle_list():
            return

        lastname = child.get_primary_name().get_surname()
        if child_h in self.person_dates:
            (born, dummy) = self.person_dates[child_h]
            person1_h = self.generate_person(1, lastname, alive_in_year=born)
            person2_h = self.generate_person(0, alive_in_year=born)
        else:
            person1_h = self.generate_person(1, lastname)
            person2_h = self.generate_person(0)

        if _randint(0, 2) > 1:
            self.parents_todo.append(person1_h)
        if _randint(0, 2) > 1:
            self.parents_todo.append(person2_h)

        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            fam = Family()
            self.add_defaults(fam)
            fam.set_father_handle(person1_h)
            fam.set_mother_handle(person2_h)
            child_ref = ChildRef()
            child_ref.set_reference_handle(child_h)
            self.fill_object(child_ref)
            fam.add_child_ref(child_ref)
            fam_h = self.db.add_family(fam, self.trans)
            self.generated_families.append(fam_h)
            fam = self.db.commit_family(fam, self.trans)
            person1 = self.db.get_person_from_handle(person1_h)
            person1.add_family_handle(fam_h)
            self.db.commit_person(person1, self.trans)
            person2 = self.db.get_person_from_handle(person2_h)
            person2.add_family_handle(fam_h)
            self.db.commit_person(person2, self.trans)
            child.add_parent_family_handle(fam_h)
            self.db.commit_person(child, self.trans)

    def generate_tags(self):
        """ Make up some odd tags """
        with DbTxn(_("Testcase generator step %d") % self.transaction_count,
                   self.db) as self.trans:
            self.transaction_count += 1
            for dummy in range(10):
                tag = Tag()
                tag.set_name(self.rand_text(self.TAG))
                tag.set_color(self.rand_color())
                tag.set_priority(self.db.get_number_of_tags())
                tag_handle = self.db.add_tag(tag, self.trans)
                self.generated_tags.append(tag_handle)

    def add_defaults(self, obj):
        self.fill_object(obj)

    def rand_name(self, lastname=None, gender=None):
        """ Create a name pair (first, last)"""
        if gender == Person.MALE:
            firstname = self.rand_text(self.FIRSTNAME_MALE)
        elif gender == Person.FEMALE:
            firstname = self.rand_text(self.FIRSTNAME_FEMALE)
        else:
            firstname = self.rand_text(self.FIRSTNAME)
        if not lastname:
            lastname = self.rand_text(self.LASTNAME)
        return (firstname, lastname)

    def rand_date(self, start=None, end=None):
        """
        Generates a random date object between the given years start and end
        """
        if not start and not end:
            start = _randint(1700, 2000)
        if start and not end:
            end = start + _randint(0, 100)
        if end and not start:
            start = end - _randint(0, 100)
        year = _randint(start, end)

        ndate = Date()
        if _randint(0, 10) == 1:
            # Some get a textual date
            ndate.set_as_text(_choice((self.rand_text(self.SHORT), "Unknown",
                                       "??", "Don't know", "TODO!")))
        else:
            if _randint(0, 10) == 1:
                # some get an empty date
                pass
            else:
                # regular dates
                calendar = Date.CAL_GREGORIAN
                quality = _choice((Date.QUAL_NONE,
                                   Date.QUAL_ESTIMATED,
                                   Date.QUAL_CALCULATED))
                modifier = _choice((Date.MOD_NONE,
                                    Date.MOD_BEFORE,
                                    Date.MOD_AFTER,
                                    Date.MOD_ABOUT,
                                    Date.MOD_RANGE,
                                    Date.MOD_SPAN))
                day = _randint(0, 28)
                if day > 0:  # avoid days without month
                    month = _randint(1, 12)
                else:
                    month = _randint(0, 12)

                if modifier in (Date.MOD_RANGE, Date.MOD_SPAN):
                    day2 = _randint(0, 28)
                    if day2 > 0:
                        month2 = _randint(1, 12)
                    else:
                        month2 = _randint(0, 12)
                    year2 = year + _randint(1, 5)
                    ndate.set(quality, modifier, calendar,
                              (day, month, year, False, day2, month2, year2,
                               False), "")
                else:
                    ndate.set(quality, modifier, calendar,
                              (day, month, year, False), "")

        return (year, ndate)

    def fill_object(self, obj):
        ''' Generic object fill routine '''

        if issubclass(obj.__class__, AddressBase):
            while _randint(0, 1) == 1:
                addr = Address()
                self.fill_object(addr)
                obj.add_address(addr)

        if isinstance(obj, Attribute):
            obj.set_type(self.rand_type(AttributeType()))
            obj.set_value(self.rand_text(self.SHORT))

        if issubclass(obj.__class__, AttributeBase):
            while _randint(0, 1) == 1:
                att = Attribute()
                self.fill_object(att)
                obj.add_attribute(att)

        if isinstance(obj, ChildRef):
            if _randint(0, 3) == 1:
                obj.set_mother_relation(self.rand_type(ChildRefType()))
            if _randint(0, 3) == 1:
                obj.set_father_relation(self.rand_type(ChildRefType()))

        if issubclass(obj.__class__, DateBase):
            if _randint(0, 1) == 1:
                (dummy, dat) = self.rand_date()
                obj.set_date_object(dat)

        if isinstance(obj, Event):
            if _randint(0, 1) == 1:
                obj.set_description(self.rand_text(self.LONG))

        if issubclass(obj.__class__, EventRef):
            obj.set_role(self.rand_type(EventRoleType()))

        if isinstance(obj, Family):
            if _randint(0, 2) == 1:
                obj.set_relationship(self.rand_type(FamilyRelType()))
            else:
                obj.set_relationship(FamilyRelType(FamilyRelType.MARRIED))

        if isinstance(obj, LdsOrd):
            if _randint(0, 1) == 1:
                obj.set_temple(_choice(TEMPLES.name_code_data())[1])

        if issubclass(obj.__class__, LdsOrdBase):
            while _randint(0, 1) == 1:
                ldsord = LdsOrd()
                self.fill_object(ldsord)
                if isinstance(obj, Person):
                    lds_type = _choice([item for item in LDS_INDIVIDUAL_ORD])
                if isinstance(obj, Family):
                    lds_type = LDS_SPOUSE_SEALING[0]
                    if self.generated_families:
                        ldsord.set_family_handle(
                            _choice(self.generated_families))
                ldsord.set_type(lds_type[0])
                status = _choice(lds_type[1])
                if status != LdsOrd.STATUS_NONE:
                    ldsord.set_status(status)
                obj.add_lds_ord(ldsord)

        if isinstance(obj, Location):
            if _randint(0, 1) == 1:
                obj.set_parish(self.rand_text(self.SHORT))

        if issubclass(obj.__class__, LocationBase):
            if _randint(0, 1) == 1:
                obj.set_street(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                obj.set_city(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                obj.set_postal_code(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                obj.set_phone(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                obj.set_state(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                obj.set_country(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                obj.set_county(self.rand_text(self.SHORT))

        if issubclass(obj.__class__, MediaBase):
            # FIXME: frequency changed to prevent recursion
            while _randint(0, 10) == 1:
                obj.add_media_reference(self.fill_object(MediaRef()))

        if isinstance(obj, Media):
            if _randint(0, 3) == 1:
                obj.set_description(str(self.rand_text(self.LONG)))
                path = os.path.abspath(_choice((ICON, LOGO, SPLASH)))
                obj.set_path(str(path))
                mime = get_type(path)
                obj.set_mime_type(mime)
            else:
                obj.set_description(str(self.rand_text(self.SHORT)))
                obj.set_path(os.path.abspath(str(ICON)))
                obj.set_mime_type("image/png")

        if isinstance(obj, MediaRef):
            if not self.generated_media or _randint(0, 10) == 1:
                med = Media()
                self.fill_object(med)
                self.db.add_media(med, self.trans)
                self.generated_media.append(med.get_handle())
            obj.set_reference_handle(_choice(self.generated_media))
            if _randint(0, 1) == 1:
                obj.set_rectangle((_randint(0, 200), _randint(0, 200),
                                   _randint(0, 200), _randint(0, 200)))

        if isinstance(obj, Name):
            obj.set_type(self.rand_type(NameType()))
            if _randint(0, 1) == 1:
                obj.set_title(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                patronymic = Surname()
                patronymic.set_surname(self.rand_text(self.FIRSTNAME_MALE))
                patronymic.set_origintype(NameOriginType.PATRONYMIC)
                obj.add_surname(patronymic)
            if _randint(0, 1) == 1:
                obj.get_primary_surname().set_prefix(
                    self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                obj.set_suffix(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                obj.set_call_name(self.rand_text(self.FIRSTNAME))
            if _randint(0, 1) == 1:
                obj.set_group_as(obj.get_surname()[:1])
            # obj.set_display_as()
            # obj.set_sort_as()

        if isinstance(obj, Note):
            n_type = self.rand_type(NoteType())
            if n_type == NoteType.HTML_CODE:
                obj.set(self.rand_text(self.NOTE))
            else:
                obj.set_styledtext(self.rand_text(self.STYLED_TEXT))
            obj.set_format(_choice((Note.FLOWED, Note.FORMATTED)))
            obj.set_type(n_type)

        if issubclass(obj.__class__, NoteBase):
            while _randint(0, 1) == 1:
                if not self.generated_notes or _randint(0, 10) == 1:
                    note = Note()
                    self.fill_object(note)
                    self.db.add_note(note, self.trans)
                    self.generated_notes.append(note.get_handle())
                n_h = _choice(self.generated_notes)
                obj.add_note(n_h)

        if isinstance(obj, Place):
            obj.set_title(self.rand_text(self.LONG))
            obj.set_name(PlaceName(value=self.rand_text(self.SHORT)))
            obj.set_code(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                if _randint(0, 4) == 1:
                    obj.set_longitude(self.rand_text(self.SHORT))
                else:
                    obj.set_longitude(str(_random() * 360.0 - 180.0))
            if _randint(0, 1) == 1:
                if _randint(0, 4) == 1:
                    obj.set_latitude(self.rand_text(self.SHORT))
                else:
                    obj.set_latitude(str(_random() * 180.0 - 90.0))
            while _randint(0, 1) == 1:
                obj.add_alternate_locations(self.fill_object(Location()))

        if issubclass(obj.__class__, PlaceBase):
            if _randint(0, 1) == 1:
                obj.set_place_handle(self.rand_place())

        if issubclass(obj.__class__, BasicPrimaryObject):
            if _randint(0, 1) == 1:
                obj.set_gramps_id(self.rand_text(self.SHORT))

        if issubclass(obj.__class__, PrivacyBase):
            obj.set_privacy(_randint(0, 5) == 1)

        if isinstance(obj, RepoRef):
            if not self.generated_repos or _randint(0, 10) == 1:
                rep = Repository()
                self.fill_object(rep)
                self.db.add_repository(rep, self.trans)
                self.generated_repos.append(rep.get_handle())
            obj.set_reference_handle(_choice(self.generated_repos))
            if _randint(0, 1) == 1:
                obj.set_call_number(self.rand_text(self.SHORT))
            obj.set_media_type(self.rand_type(SourceMediaType()))

        if isinstance(obj, Repository):
            obj.set_type(self.rand_type(RepositoryType()))
            obj.set_name(self.rand_text(self.SHORT))

        if isinstance(obj, Source):
            obj.set_title(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                obj.set_author(self.rand_text(self.SHORT))
            if _randint(0, 1) == 1:
                obj.set_publication_info(self.rand_text(self.LONG))
            if _randint(0, 1) == 1:
                obj.set_abbreviation(self.rand_text(self.SHORT))
            while _randint(0, 1) == 1:
                sattr = SrcAttribute()
                sattr.set_type(self.rand_text(self.SHORT))
                sattr.set_value(self.rand_text(self.SHORT))
                obj.add_attribute(sattr)
            while _randint(0, 1) == 1:
                rep_ref = RepoRef()
                self.fill_object(rep_ref)
                obj.add_repo_reference(rep_ref)

        if issubclass(obj.__class__, CitationBase):
            while _randint(0, 1) == 1:
                if not self.generated_citations or _randint(1, 10) == 1:
                    cit = Citation()
                    self.fill_object(cit)
                    self.db.add_citation(cit, self.trans)
                    self.generated_citations.append(cit.get_handle())
                s_h = _choice(self.generated_citations)
                obj.add_citation(s_h)

        if isinstance(obj, Citation):
            if not self.generated_sources or _randint(0, 10) == 1:
                src = Source()
                self.fill_object(src)
                self.db.add_source(src, self.trans)
                self.generated_sources.append(src.get_handle())
            obj.set_reference_handle(_choice(self.generated_sources))
            if _randint(0, 1) == 1:
                obj.set_page(self.rand_text(self.NUMERIC))
            # if _randint(0, 1) == 1:
            #    obj.set_text( self.rand_text(self.SHORT))
            # if _randint(0, 1) == 1:
            #    (year, dat) = self.rand_date( )
            #    obj.set_date_object( dat)
            # sort to provide deterministic output in unit tests
            obj.set_confidence_level(_choice(sorted(conf_strings.keys())))

        if issubclass(obj.__class__, TagBase):
            if _randint(0, 1) == 1:
                obj.set_tag_list(self.rand_tags())

        if issubclass(obj.__class__, UrlBase):
            while _randint(0, 1) == 1:
                url = Url()
                self.fill_object(url)
                obj.add_url(url)

        if isinstance(obj, Url):
            obj.set_path("http://www.gramps-project.org/?test=%s" %
                         self.rand_text(self.SHORT))
            obj.set_description(self.rand_text(self.SHORT))
            obj.set_type(self.rand_type(UrlType()))

        return obj

    def rand_personal_event(self, e_type=None, start=None, end=None):
        """ Random personal event """
        if e_type:
            typeval = EventType(e_type)
        else:
            typeval = self.rand_type(EventType())
        return self._rand_event(typeval, start, end)

    def rand_family_event(self, e_type=None, start=None, end=None):
        """ Random family event """
        if e_type:
            EventType(e_type)
        else:
            typeval = EventType.UNKNOWN
            while int(typeval) not in self.FAMILY_EVENTS:
                typeval = self.rand_type(EventType())
        return self._rand_event(typeval, start, end)

    def _rand_event(self, e_type, start, end):
        """ Random general event """
        evt = Event()
        self.fill_object(evt)
        evt.set_type(e_type)
        (year, dat) = self.rand_date(start, end)
        evt.set_date_object(dat)
        event_h = self.db.add_event(evt, self.trans)
        self.generated_events.append(event_h)
        event_ref = EventRef()
        self.fill_object(event_ref)
        event_ref.set_reference_handle(event_h)
        return (year, event_ref)

    def rand_type(self, gtype):
        if issubclass(gtype.__class__, GrampsType):
            gmap = gtype.get_map()
            # sort to provide deterministic output in unit tests
            key = _choice(sorted(gmap.keys()))
            if key == gtype.get_custom():
                value = self.rand_text(self.SHORT)
            else:
                value = ''
            gtype.set((key, value))
            return gtype

    def rand_place(self):
        if not self.generated_places or _randint(0, 10) == 1:
            self.generate_place()
        return _choice(self.generated_places)

    def generate_place(self):
        parent_handle = None
        for type_num in range(1, 8):
            if type_num > 1 and _randint(1, 3) == 1:
                # skip some levels in the place hierarchy
                continue
            place = Place()
            place.set_type(PlaceType(type_num))
            if parent_handle is not None:
                self.add_parent_place(place, parent_handle)
            if type_num > 1 and _randint(1, 3) == 1:
                # add additional parent place
                parent_handle = self.find_parent_place(type_num - 1)
                if parent_handle is not None:
                    self.add_parent_place(place, parent_handle)
            self.fill_object(place)
            self.db.add_place(place, self.trans)
            parent_handle = place.get_handle()
            self.generated_places.append(place.get_handle())
            self.parent_places[type_num].append(place.get_handle())

    def find_parent_place(self, type_num):
        if len(self.parent_places[type_num]) > 0:
            return _choice(self.parent_places[type_num])
        else:
            return None

    def add_parent_place(self, place, handle):
        place_ref = PlaceRef()
        place_ref.ref = handle
        dummy, random_date = self.rand_date()
        place_ref.set_date_object(random_date)
        place.add_placeref(place_ref)

    def rand_text(self, t_type=None):
        """ make random text strings according to desired type """
        # for lastnamesnames
        syllables1 = ["sa", "li", "na", "ma", "no", "re", "mi",
                      "cha", "ki", "du", "ba", "ku", "el"]
        # for firstnames
        syllables2 = ["as", "il", "an", "am", "on", "er", "im",
                      "ach", "ik", "ud", "ab", "ul", "le"]
        # others
        syllables3 = ["ka", "po", "lo", "chi", "she", "di", "fa",
                      "go", "ja", "ne", "pe"]

        syllables = syllables1 + syllables2 + syllables3
        minwords = 5
        maxwords = 8
        minsyllables = 2
        maxsyllables = 5

        # result = "" if t_type != self.STYLED_TEXT else StyledText("")
        if t_type == self.STYLED_TEXT:
            result = StyledText("")
        else:
            result = ""

        if self.options_dict['specialchars']:
            result = result + "ä<ö&ü%ß'\""

        if self.options_dict['add_serial'] and t_type != self.TAG:
            result = result + "#+#%06d#-#" % self.text_serial_number
            self.text_serial_number = self.text_serial_number + 1

        if not t_type:
            t_type = self.SHORT

        if t_type == self.SHORT or t_type == self.TAG:
            minwords = 1
            maxwords = 3
            minsyllables = 2
            maxsyllables = 4

        if t_type == self.LONG:
            minwords = 5
            maxwords = 8
            minsyllables = 2
            maxsyllables = 5

        if t_type == self.FIRSTNAME:
            t_type = _choice((self.FIRSTNAME_MALE, self.FIRSTNAME_FEMALE))

        if t_type == self.FIRSTNAME_MALE or t_type == self.FIRSTNAME_FEMALE:
            syllables = syllables2
            minwords = 1
            maxwords = 5
            minsyllables = 2
            maxsyllables = 5
            if not self.options_dict['long_names']:
                maxwords = 2
                maxsyllables = 3

        if t_type == self.LASTNAME:
            syllables = syllables1
            minwords = 1
            maxwords = 1
            minsyllables = 2
            maxsyllables = 5
            if not self.options_dict['long_names']:
                maxsyllables = 3

        if t_type == self.NOTE or t_type == self.STYLED_TEXT:
            result = result + "Generated by TestcaseGenerator."
            minwords = 20
            maxwords = 100

        if t_type == self.NUMERIC:
            if _randint(0, 1) == 1:
                return "%d %s" % (_randint(1, 100), result)
            if _randint(0, 1) == 1:
                return "%d, %d %s" % (_randint(1, 100), _randint(100, 1000),
                                      result)
            med = _randint(100, 1000)
            return "%d - %d %s" % (med, med + _randint(1, 5), result)

        for dummy in range(0, _randint(minwords, maxwords)):
            if result:
                result = result + " "
            word = ""
            for j in range(0, _randint(minsyllables, maxsyllables)):
                word = word + _choice(syllables)
            if t_type == self.FIRSTNAME_MALE:
                word = word + _choice(("a", "e", "i", "o", "u"))
            if _randint(0, 3) == 1:
                word = word.title()
            if t_type == self.NOTE:
                if _randint(0, 10) == 1:
                    word = "<b>%s</b>" % word
                elif _randint(0, 10) == 1:
                    word = "<i>%s</i>" % word
                elif _randint(0, 10) == 1:
                    word = "<i>%s</i>" % word
                if _randint(0, 20) == 1:
                    word = word + "."
                elif _randint(0, 30) == 1:
                    word = word + ".\n"
            if t_type == self.STYLED_TEXT:
                tags = []
                if _randint(0, 10) == 1:
                    tags += [StyledTextTag(StyledTextTagType.BOLD, True,
                                           [(0, len(word))])]
                elif _randint(0, 10) == 1:
                    tags += [StyledTextTag(StyledTextTagType.ITALIC, True,
                                           [(0, len(word))])]
                elif _randint(0, 10) == 1:
                    tags += [StyledTextTag(StyledTextTagType.UNDERLINE, True,
                                           [(0, len(word))])]
                sword = StyledText(word, tags)
                if _randint(0, 20) == 1:
                    sword = sword + "."
                elif _randint(0, 30) == 1:
                    sword = sword + ".\n"
                result = StyledText("").join((result, sword))
            else:
                result += word

        if t_type == self.LASTNAME:
            case = _randint(0, 2)
            if case == 0:
                result = result.title()
            elif case == 1:
                result = result.upper()

        if self.options_dict['add_linebreak'] and \
                t_type != self.TAG:
            result = result + "\nNEWLINE"

        return result

    def rand_color(self):
        return '#%012X' % _randint(0, 281474976710655)

    def rand_tags(self):
        maxtags = 5
        taglist = []
        for dummy in range(0, _randint(1, maxtags)):
            tag = _choice(self.generated_tags)
            if tag not in taglist:
                taglist.append(tag)
        return taglist


# -----------------------------------------------------------------------
#
# The options class for the tool
#
# -----------------------------------------------------------------------
class TestcaseGeneratorOptions(tool.ToolOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, person_id=None):
        tool.ToolOptions.__init__(self, name, person_id)

        # Options specific for this report
        self.options_dict = {
            'lowlevel':       0,
            'bugs':           0,
            'persons':        1,
            'person_count':   2000,
            'long_names':     0,
            'specialchars':   0,
            'add_serial':     0,
            'add_linebreak':  0,
        }
        self.options_help = {
            'lowlevel':      ("=0/1",
                              "Whether to create low level database errors.",
                              ["Skip test",
                               "Create low level database errors"],
                              True),
            'bugs':          ("=0/1",
                              "Whether to create invalid database references.",
                              ["Skip test",
                               "Create invalid Database references"],
                              True),
            'persons':       ("=0/1",
                              "Whether to create a bunch of dummy persons",
                              ["Dont create persons", "Create dummy persons"],
                              True),
            'person_count':  ("=int",
                              "Number of dummy persons to generate",
                              "Number of persons"),
            'long_names':    ("=0/1",
                              "Whether to create short or long names",
                              ["Short names", "Long names"],
                              True),
            'specialchars':  ("=0/1",
                              "Whether to ass some special characters to every"
                              " text field",
                              ["No special characters",
                               "Add special characters"],
                              True),
            'add_serial':    ("=0/1",
                              "Whether to add a serial number to every text "
                              "field",
                              ["No serial", "Add serial number"],
                              True),
            'add_linebreak': ("=0/1",
                              "Whether to add a line break to every text "
                              "field",
                              ["No linebreak", "Add line break"],
                              True),
        }
