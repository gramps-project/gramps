#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004  Martin Hawlisch
# Copyright (C) 2004-2006, 2008 Donald N. Allingham
# Copyright (C) 2008  Brian G. Matherly
# Copyright (C) 2009  Gary Burton
# Copyright (C) 2010       Jakim Friant
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

"Export to GeneWeb."

# -------------------------------------------------------------------------
#
# Standard Python Modules
#
# -------------------------------------------------------------------------
import os

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
import logging
from collections import abc

log = logging.getLogger(".WriteGeneWeb")

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext
from gramps.gen.lib import Date, Event, EventType, FamilyRelType, Person
from gramps.gui.plug.export import WriterOptionBox
from gramps.gen.utils.alive import probably_alive
from gramps.gui.glade import Glade
from gramps.gen.config import config
from gramps.gen.display.place import displayer as _pd


class GeneWebWriter:
    def __init__(self, database, filename, user, option_box=None):
        self.db = database
        self.filename = filename
        self.user = user
        self.option_box = option_box
        if isinstance(self.user.callback, abc.Callable):  # is really callable
            self.update = self.update_real
        else:
            self.update = self.update_empty

        self.persons_details_done = []
        self.persons_notes_done = []
        self.person_ids = {}

        if option_box:
            self.option_box.parse_options()
            self.db = option_box.get_filtered_database(self.db)

    def update_empty(self):
        pass

    def update_real(self):
        self.count += 1
        newval = int(100 * self.count / self.total)
        if newval != self.oldval:
            self.user.callback(newval)
            self.oldval = newval

    def writeln(self, text):
        self.g.write(self.iso8859("%s\n" % (text)))

    def export_data(self):
        self.dirname = os.path.dirname(self.filename)
        try:
            with open(self.filename, "wb") as self.g:
                self.flist = self.db.get_family_handles()
                self.flist.sort()
                if len(self.flist) < 1:
                    self.user.notify_error(_("No families matched by selected filter"))
                    return False

                self.count = 0
                self.oldval = 0
                self.total = len(self.flist)
                for key in self.flist:
                    self.write_family(key)
                    self.writeln("")

                return True
        except IOError as msg:
            msg2 = _("Could not create %s") % self.filename
            self.user.notify_error(msg2, str(msg))
            return False
        except:
            self.user.notify_error(_("Could not create %s") % self.filename)
            return False

    def write_family(self, family_handle):
        family = self.db.get_family_from_handle(family_handle)
        if family:
            self.update()
            father_handle = family.get_father_handle()
            if father_handle:
                father = self.db.get_person_from_handle(father_handle)
                mother_handle = family.get_mother_handle()
                if mother_handle:
                    mother = self.db.get_person_from_handle(mother_handle)
                    self.writeln(
                        "fam %s %s+%s %s %s"
                        % (
                            self.get_ref_name(father),
                            self.get_full_person_info_fam(father),
                            self.get_wedding_data(family),
                            self.get_ref_name(mother),
                            self.get_full_person_info_fam(mother),
                        )
                    )
                    self.write_witness(family)
                    self.write_sources(family.get_citation_list())
                    self.write_children(family, father)
                    self.write_notes(family, father, mother)
                    if True:  # FIXME: not (self.restrict and self.exclnotes):
                        notelist = family.get_note_list()
                        note = ""
                        for notehandle in notelist:
                            noteobj = self.db.get_note_from_handle(notehandle)
                            note += noteobj.get() + " "
                        if note and note != "":
                            note = note.replace("\n\r", " ")
                            note = note.replace("\r\n", " ")
                            note = note.replace("\n", " ")
                            note = note.replace("\r", " ")
                            self.writeln("comm %s" % note)

    def write_witness(self, family):
        # FIXME: witnesses are not in events anymore
        return

        if self.restrict:
            return
        event_ref_list = family.get_event_ref_list()
        for event_ref in event_ref:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event.type == EventType.MARRIAGE:
                w_list = event.get_witness_list()
                if w_list:
                    for witness in w_list:
                        if witness and witness.type == Event.ID:
                            person = self.db.get_person_from_handle(witness.get_value())
                            if person:
                                gender = ""
                                if person.get_gender() == Person.MALE:
                                    gender = "h"
                                elif person.get_gender() == Person.FEMALE:
                                    gender = "f"
                                self.writeln(
                                    "wit %s %s %s"
                                    % (
                                        gender,
                                        self.get_ref_name(person),
                                        self.get_full_person_info_fam(person),
                                    )
                                )

    def write_sources(self, reflist):
        # FIXME
        # if self.restrict and self.exclnotes:
        #    return

        if reflist:
            for handle in reflist:
                citation = self.db.get_citation_from_handle(handle)
                src_handle = citation.get_reference_handle()
                source = self.db.get_source_from_handle(src_handle)
                if source:
                    self.writeln("src %s" % (self.rem_spaces(source.get_title())))

    def write_children(self, family, father):
        father_lastname = father.get_primary_name().get_surname()
        child_ref_list = family.get_child_ref_list()
        if child_ref_list:
            self.writeln("beg")
            for child_ref in child_ref_list:
                child = self.db.get_person_from_handle(child_ref.ref)
                if child:
                    gender = ""
                    if child.get_gender() == Person.MALE:
                        gender = "h"
                    elif child.get_gender() == Person.FEMALE:
                        gender = "f"
                    self.writeln(
                        "- %s %s %s"
                        % (
                            gender,
                            self.get_child_ref_name(child, father_lastname),
                            self.get_full_person_info_child(child),
                        )
                    )
            self.writeln("end")

    def write_notes(self, family, father, mother):
        # FIXME:
        # if self.restrict and self.exclnotes:
        #    return

        self.write_note_of_person(father)
        self.write_note_of_person(mother)
        child_ref_list = family.get_child_ref_list()
        if child_ref_list:
            for child_ref in child_ref_list:
                child = self.db.get_person_from_handle(child_ref.ref)
                if child:
                    self.write_note_of_person(child)
        # FIXME: witnesses do not exist in events anymore

    ##         event_ref_list = family.get_event_ref_list()
    ##         for event_ref in event_ref_list:
    ##             event = self.db.get_event_from_handle(event_ref.ref)
    ##             if int(event.get_type()) == EventType.MARRIAGE:
    ##                 w_list = event.get_witness_list()
    ##                 if w_list:
    ##                     for witness in w_list:
    ##                         if witness and witness.type == Event.ID:
    ##                             person = self.db.get_person_from_handle(witness.get_value())
    ##                             if person:
    ##                                 self.write_note_of_person(person)

    def write_note_of_person(self, person):
        if self.persons_notes_done.count(person.get_handle()) == 0:
            self.persons_notes_done.append(person.get_handle())

            notelist = person.get_note_list()
            note = ""
            for notehandle in notelist:
                noteobj = self.db.get_note_from_handle(notehandle)
                note += noteobj.get()
                note += " "

            if note and note != "":
                self.writeln("")
                self.writeln("notes %s" % self.get_ref_name(person))
                self.writeln("beg")
                self.writeln(note)
                self.writeln("end notes")

    def get_full_person_info(self, person):
        # FIXME:
        # if self.restrict:
        #    return "0 "

        retval = ""

        b_date = "0"
        b_place = ""
        birth_ref = person.get_birth_ref()
        if birth_ref:
            birth = self.db.get_event_from_handle(birth_ref.ref)
            if birth:
                b_date = self.format_date(birth.get_date_object())
                place_handle = birth.get_place_handle()
                if place_handle:
                    b_place = _pd.display_event(self.db, birth)

        if probably_alive(person, self.db):
            d_date = ""
        else:
            d_date = "0"
        d_place = ""
        death_ref = person.get_death_ref()
        if death_ref:
            death = self.db.get_event_from_handle(death_ref.ref)
            if death:
                d_date = self.format_date(death.get_date_object())
                place_handle = death.get_place_handle()
                if place_handle:
                    d_place = _pd.display_event(self.db, death)

        retval = retval + "%s " % b_date
        if b_place != "":
            retval = retval + "#bp %s " % self.rem_spaces(b_place)
        retval = retval + "%s " % d_date
        if d_place != "":
            retval = retval + "#dp %s " % self.rem_spaces(d_place)
        return retval

    def get_full_person_info_fam(self, person):
        """Output full person data of a family member.

        This is only done if the person is not listed as a child.

        """
        retval = ""
        if self.persons_details_done.count(person.get_handle()) == 0:
            is_child = 0
            pf_list = person.get_parent_family_handle_list()
            if pf_list:
                for family_handle in pf_list:
                    if family_handle in self.flist:
                        is_child = 1
            if is_child == 0:
                self.persons_details_done.append(person.get_handle())
                retval = self.get_full_person_info(person)
        return retval

    def get_full_person_info_child(self, person):
        """Output full person data for a child, if not printed somewhere else."""
        retval = ""
        if self.persons_details_done.count(person.get_handle()) == 0:
            self.persons_details_done.append(person.get_handle())
            retval = self.get_full_person_info(person)
        return retval

    def rem_spaces(self, str):
        return str.replace(" ", "_")

    def get_ref_name(self, person):
        # missing_surname = config.get("preferences.no-surname-text")
        surname = self.rem_spaces(person.get_primary_name().get_surname())
        # firstname = config.get('preferences.private-given-text')
        # if not (probably_alive(person,self.db) and \
        #  self.restrict and self.living):
        firstname = self.rem_spaces(person.get_primary_name().get_first_name())
        if person.get_handle() not in self.person_ids:
            self.person_ids[person.get_handle()] = len(self.person_ids)
        return "%s %s.%d" % (surname, firstname, self.person_ids[person.get_handle()])

    def get_child_ref_name(self, person, father_lastname):
        # missing_first_name = config.get("preferences.no-given-text")
        surname = self.rem_spaces(person.get_primary_name().get_surname())
        # firstname = config.get('preferences.private-given-text')
        # if not (probably_alive(person,self.db) and \
        #  self.restrict and self.living):
        firstname = self.rem_spaces(person.get_primary_name().get_first_name())
        if person.get_handle() not in self.person_ids:
            self.person_ids[person.get_handle()] = len(self.person_ids)
        ret = "%s.%d" % (firstname, self.person_ids[person.get_handle()])
        if surname != father_lastname:
            ret += " " + surname
        return ret

    def get_wedding_data(self, family):
        ret = ""
        event_ref_list = family.get_event_ref_list()
        m_date = ""
        m_place = ""
        m_source = ""
        married = 0
        eng_date = ""
        eng_place = ""
        eng_source = ""
        engaged = 0
        div_date = ""
        divorced = 0
        for event_ref in event_ref_list:
            event = self.db.get_event_from_handle(event_ref.ref)
            if event.get_type() == EventType.MARRIAGE:
                married = 1
                m_date = self.format_date(event.get_date_object())
                place_handle = event.get_place_handle()
                if place_handle:
                    m_place = _pd.display_event(self.db, event)
                m_source = self.get_primary_source(event.get_citation_list())
            if event.get_type() == EventType.ENGAGEMENT:
                engaged = 1
                eng_date = self.format_date(event.get_date_object())
                place_handle = event.get_place_handle()
                if place_handle:
                    eng_place = _pd.display_event(self.db, event)
                eng_source = self.get_primary_source(event.get_citation_list())
            if event.get_type() == EventType.DIVORCE:
                divorced = 1
                div_date = self.format_date(event.get_date_object())
        if married == 1:
            if m_date != "":
                ret = ret + m_date
            if m_place != "" and m_source != "":
                ret = ret + " #mp %s #ms %s" % (
                    self.rem_spaces(m_place),
                    self.rem_spaces(m_source),
                )
            if m_place != "" and m_source == "":
                ret = ret + " #mp %s" % self.rem_spaces(m_place)
            if m_source != "" and m_place == "":
                ret = ret + " #ms %s" % self.rem_spaces(m_source)
        elif engaged == 1:
            """Geneweb only supports either Marriage or engagement"""
            if eng_date != "":
                ret = ret + eng_date
            if m_place != "" and m_source != "":
                ret = ret + " #mp %s #ms %s" % (
                    self.rem_spaces(m_place),
                    self.rem_spaces(m_source),
                )
            if eng_place != "" and m_source == "":
                ret = ret + " #mp %s" % self.rem_spaces(m_place)
            if eng_source != "" and m_place == "":
                ret = ret + " #ms %s" % self.rem_spaces(m_source)
        else:
            if family.get_relationship() != FamilyRelType.MARRIED:
                """Not married or engaged"""
                ret = ret + " #nm"

        if divorced == 1:
            if div_date != "":
                ret = ret + " -%s" % div_date
            else:
                ret = ret + " -0"

        return ret

    def get_primary_source(self, reflist):
        ret = ""
        if reflist:
            for handle in reflist:
                citation = self.db.get_citation_from_handle(handle)
                src_handle = citation.get_reference_handle()
                source = self.db.get_source_from_handle(src_handle)
                if source:
                    if ret != "":
                        ret = ret + ", "
                        ret = ret + source.get_title()
        return ret

    def format_single_date(self, subdate, cal, mode):
        retval = ""
        (day, month, year, sl) = subdate

        cal_type = ""
        if cal == Date.CAL_HEBREW:
            cal_type = "H"
        elif cal == Date.CAL_FRENCH:
            cal_type = "F"
        elif cal == Date.CAL_JULIAN:
            cal_type = "J"

        mode_prefix = ""
        if mode == Date.MOD_ABOUT:
            mode_prefix = "~"
        elif mode == Date.MOD_BEFORE:
            mode_prefix = "<"
        elif mode == Date.MOD_AFTER:
            mode_prefix = ">"

        if year > 0:
            if month > 0:
                if day > 0:
                    retval = "%s%s/%s/%s%s" % (mode_prefix, day, month, year, cal_type)
                else:
                    retval = "%s%s/%s%s" % (mode_prefix, month, year, cal_type)
            else:
                retval = "%s%s%s" % (mode_prefix, year, cal_type)
        return retval

    def format_date(self, date):
        retval = ""
        if date.get_modifier() == Date.MOD_TEXTONLY:
            retval = "0(%s)" % self.rem_spaces(date.get_text())
        elif not date.is_empty():
            mod = date.get_modifier()
            cal = cal = date.get_calendar()
            if mod == Date.MOD_SPAN or mod == Date.MOD_RANGE:
                retval = "%s..%s" % (
                    self.format_single_date(date.get_start_date(), cal, mod),
                    self.format_single_date(date.get_stop_date(), cal, mod),
                )
            elif mod == Date.MOD_FROM:
                retval = "%s..0" % (
                    self.format_single_date(date.get_start_date(), cal, mod)
                )
            elif mod == Date.MOD_TO:
                retval = "0..%s" % (
                    self.format_single_date(date.get_start_date(), cal, mod)
                )
            else:
                retval = self.format_single_date(date.get_start_date(), cal, mod)
        return retval

    def iso8859(self, s):
        return s.encode("iso-8859-1", "xmlcharrefreplace")


# -------------------------------------------------------------------------
#
#
#
# -------------------------------------------------------------------------
def exportData(database, filename, user, option_box=None):
    gw = GeneWebWriter(database, filename, user, option_box)
    return gw.export_data()
