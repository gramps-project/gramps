#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008 Douglas S. Blank
# Copyright (C) 2004-2007 Donald N. Allingham
# Copyright (C) 2008      Brian G. Matherly
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2013       Vassilii Khachaturov
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

"Export to CSV Spreadsheet."

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import os
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.sgettext
import csv
from io import StringIO
import codecs

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
from collections import abc
LOG = logging.getLogger(".ExportCSV")

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gramps.gen.lib import EventType, Person
from gramps.gen.lib.eventroletype import EventRoleType
from gramps.gui.plug.export import WriterOptionBox
from gramps.gen.utils.string import gender as gender_map
from gramps.gen.datehandler import get_date
from gramps.gen.display.place import displayer as _pd
from gramps.gui.glade import Glade
from gramps.gen.constfunc import win

#-------------------------------------------------------------------------
#
# The function that does the exporting
#
#-------------------------------------------------------------------------
def exportData(database, filename, user, option_box=None):
    gw = CSVWriter(database, filename, user, option_box)
    return gw.export_data()

#-------------------------------------------------------------------------
#
# Support Functions
#
#-------------------------------------------------------------------------
def sortable_string_representation(text):
    numeric = ""
    alpha = ""
    for s in text:
        if s.isdigit():
            numeric += s
        else:
            alpha += s
    return alpha + (("0" * 10) + numeric)[-10:]

def get_primary_event_ref_from_type(db, person, event_name):
    """
    >>> get_primary_event_ref_from_type(db, Person(), "Baptism"):
    """
    for ref in person.event_ref_list:
        if ref.get_role() == EventRoleType.PRIMARY:
            event = db.get_event_from_handle(ref.ref)
            if event and event.type.is_type(event_name):
                return ref
    return None

def get_primary_source_title(db, obj):
    for citation_handle in obj.get_citation_list():
        citation = db.get_citation_from_handle(citation_handle)
        source = db.get_source_from_handle(citation.get_reference_handle())
        if source:
            return source.get_title()
    return ""

#-------------------------------------------------------------------------
#
# CSVWriter Options
#
#-------------------------------------------------------------------------
class CSVWriterOptionBox(WriterOptionBox):
    """
    Create a VBox with the option widgets and define methods to retrieve
    the options.

    """
    def __init__(self, person, dbstate, uistate, track=[], window=None):
        WriterOptionBox.__init__(self, person, dbstate, uistate, track=track,
                                 window=window)
        ## TODO: add place filter selection
        self.include_individuals = 1
        self.include_marriages = 1
        self.include_children = 1
        self.include_places = 1
        self.translate_headers = 1
        self.include_individuals_check = None
        self.include_marriages_check = None
        self.include_children_check = None
        self.include_places_check = None
        self.translate_headers_check = None

    def get_option_box(self):
        from gi.repository import Gtk
        option_box = WriterOptionBox.get_option_box(self)

        self.include_individuals_check = Gtk.CheckButton(label=_("Include people"))
        self.include_marriages_check = Gtk.CheckButton(label=_("Include marriages"))
        self.include_children_check = Gtk.CheckButton(label=_("Include children"))
        self.include_places_check = Gtk.CheckButton(label=_("Include places"))
        self.translate_headers_check = Gtk.CheckButton(label=_("Translate headers"))

        self.include_individuals_check.set_active(1)
        self.include_marriages_check.set_active(1)
        self.include_children_check.set_active(1)
        self.include_places_check.set_active(1)
        self.translate_headers_check.set_active(1)

        option_box.pack_start(self.include_individuals_check, False, True, 0)
        option_box.pack_start(self.include_marriages_check, False, True, 0)
        option_box.pack_start(self.include_children_check, False, True, 0)
        option_box.pack_start(self.include_places_check, False, True, 0)
        option_box.pack_start(self.translate_headers_check, False, True, 0)

        return option_box

    def parse_options(self):
        WriterOptionBox.parse_options(self)
        if self.include_individuals_check:
            self.include_individuals = self.include_individuals_check.get_active()
            self.include_marriages = self.include_marriages_check.get_active()
            self.include_children = self.include_children_check.get_active()
            self.include_places = self.include_places_check.get_active()
            self.translate_headers = self.translate_headers_check.get_active()

#-------------------------------------------------------------------------
#
# CSVWriter class
#
#-------------------------------------------------------------------------
class CSVWriter:
    def __init__(self, database, filename, user, option_box=None):
        self.db = database
        self.option_box = option_box
        self.filename = filename
        self.user = user
        if isinstance(self.user.callback, abc.Callable):  # is really callable
            self.update = self.update_real
        else:
            self.update = self.update_empty

        self.plist = {}
        self.flist = {}
        self.place_list = {}

        self.persons_details_done = []
        self.persons_notes_done = []
        self.person_ids = {}

        if not option_box:
            self.include_individuals = 1
            self.include_marriages = 1
            self.include_children = 1
            self.include_places = 1
            self.translate_headers = 1
        else:
            self.option_box.parse_options()
            self.db = option_box.get_filtered_database(self.db)

            self.include_individuals = self.option_box.include_individuals
            self.include_marriages = self.option_box.include_marriages
            self.include_children = self.option_box.include_children
            self.include_places = self.option_box.include_places
            self.translate_headers = self.option_box.translate_headers

        self.plist = [x for x in self.db.iter_person_handles()]

        # make place list so that dependencies are first:
        self.place_list = []
        place_list = sorted([x for x in self.db.iter_place_handles()])
        while place_list:
            handle = place_list[0]
            place = self.db.get_place_from_handle(handle)
            if place:
                if all([(x.ref in self.place_list) for x in place.placeref_list]):
                    self.place_list.append(place_list.pop(0))
                else: # put at the back of the line:
                    place_list.append(place_list.pop(0))
            else:
                place_list.pop(0)
        # get the families for which these people are spouses:
        self.flist = {}
        for key in self.plist:
            p = self.db.get_person_from_handle(key)
            if p:
                for family_handle in p.get_family_handle_list():
                    self.flist[family_handle] = 1
        # now add the families for which these people are a child:
        for family_handle in self.db.iter_family_handles():
            family = self.db.get_family_from_handle(family_handle)
            if family:
                for child_ref in family.get_child_ref_list():
                    if child_ref:
                        child_handle = child_ref.ref
                        if child_handle in self.plist:
                            self.flist[family_handle] = 1

    def update_empty(self):
        pass

    def update_real(self):
        self.count += 1
        newval = int(100*self.count/self.total)
        if newval != self.oldval:
            self.user.callback(newval)
            self.oldval = newval

    def writeln(self):
        self.g.writerow([])

    def write_csv(self, *items):
        self.g.writerow(items)

    def export_data(self):
        self.dirname = os.path.dirname (self.filename)
        try:
            self.fp = open(self.filename, "w",
                           encoding='utf_8_sig' if win() else 'utf_8',
                           newline='')
            self.g = csv.writer(self.fp)
        except IOError as msg:
            msg2 = _("Could not create %s") % self.filename
            self.user.notify_error(msg2,str(msg))
            return False
        except:
            self.user.notify_error(_("Could not create %s") % self.filename)
            return False
        ######################### initialize progress bar
        self.count = 0
        self.total = 0
        self.oldval = 0
        if self.include_individuals:
            self.total += len(self.plist)
        if self.include_marriages:
            self.total += len(self.flist)
        if self.include_children:
            self.total += len(self.flist)
        if self.include_places:
            self.total += len(self.place_list)
        ########################
        LOG.debug("Possible people to export: %s", len(self.plist))
        LOG.debug("Possible families to export: %s", len(self.flist))
        LOG.debug("Possible places to export: %s", len(self.place_list))
        ###########################
        if self.include_places:
            if self.translate_headers:
                self.write_csv(_("Place"), _("Title"), _("Name"),
                               _("Type"), _("Latitude"), _("Longitude"),
                               _("Code"), _("Enclosed_by"), _("Date"))
            else:
                self.write_csv("Place", "Title", "Name",
                               "Type", "Latitude", "Longitude",
                               "Code", "Enclosed_by", "Date")
            for key in self.place_list:
                place = self.db.get_place_from_handle(key)
                if place:
                    place_id = place.gramps_id
                    place_title = place.title
                    place_name = place.name.value
                    place_type = str(place.place_type)
                    place_latitude = place.lat
                    place_longitude = place.long
                    place_code = place.code
                    if place.placeref_list:
                        for placeref in place.placeref_list:
                            placeref_obj = self.db.get_place_from_handle(placeref.ref)
                            placeref_date = ""
                            if not placeref.date.is_empty():
                                placeref_date = placeref.date
                            placeref_id = ""
                            if placeref_obj:
                                placeref_id = "[%s]" % placeref_obj.gramps_id
                            self.write_csv("[%s]" % place_id, place_title, place_name, place_type,
                                           place_latitude, place_longitude, place_code, placeref_id,
                                           placeref_date)
                    else:
                        self.write_csv("[%s]" % place_id, place_title, place_name, place_type,
                                       place_latitude, place_longitude, place_code, "",
                                       "")
                self.update()
            self.writeln()
        ########################### sort:
        sortorder = []
        dropped_surnames = set()
        for key in self.plist:
            person = self.db.get_person_from_handle(key)
            if person:
                primary_name = person.get_primary_name()
                first_name = primary_name.get_first_name()
                surname_obj = primary_name.get_primary_surname()
                surname = surname_obj.get_surname()

                # See bug #6955
                nonprimary_surnames = set(primary_name.get_surname_list())
                nonprimary_surnames.remove(surname_obj)
                dropped_surnames.update(nonprimary_surnames)

                sortorder.append( (surname, first_name, key) )
        if dropped_surnames:
            LOG.warning(
                    _("CSV export doesn't support non-primary surnames, "
                        "{count} dropped").format(
                            count=len(dropped_surnames)) )
            LOG.debug(
                    "Dropped surnames: " +
                    ', '.join([("%s %s %s" % (surname.get_prefix(),
                    surname.get_surname(), surname.get_connector())).strip()
                    for surname in dropped_surnames]))
        sortorder.sort() # will sort on tuples
        plist = [data[2] for data in sortorder]
        ###########################
        if self.include_individuals:
            if self.translate_headers:
                self.write_csv(
                    _("Person"), _("Surname"), _("Given"),
                    _("Call"), _("Suffix"), _("Prefix"),
                    _("Title", "Person"), _("Gender"),
                    _("Birth date"), _("Birth place"), _("Birth source"),
                    _("Baptism date"), _("Baptism place"), _("Baptism source"),
                    _("Death date"), _("Death place"), _("Death source"),
                    _("Burial date"), _("Burial place"), _("Burial source"),
                    _("Note"))
            else:
                self.write_csv(
                    "Person", "Surname", "Given",
                    "Call", "Suffix", "Prefix",
                    "Title", "Gender",
                    "Birth date", "Birth place", "Birth source",
                    "Baptism date", "Baptism place", "Baptism source",
                    "Death date", "Death place", "Death source",
                    "Burial date", "Burial place", "Burial source",
                    "Note")
            for key in plist:
                person = self.db.get_person_from_handle(key)
                if person:
                    primary_name = person.get_primary_name()
                    first_name = primary_name.get_first_name()
                    surname_obj = primary_name.get_primary_surname()
                    surname = surname_obj.get_surname()
                    prefix = surname_obj.get_prefix()
                    suffix = primary_name.get_suffix()
                    title = primary_name.get_title()
                    grampsid = person.get_gramps_id()
                    grampsid_ref = ""
                    if grampsid != "":
                        grampsid_ref = "[" + grampsid + "]"
                    note = '' # don't export notes
                    callname = primary_name.get_call_name()
                    gender = person.get_gender()
                    if gender == Person.MALE:
                        gender = gender_map[Person.MALE]
                    elif gender == Person.FEMALE:
                        gender = gender_map[Person.FEMALE]
                    else:
                        gender = gender_map[Person.UNKNOWN]
                    # Birth:
                    birthdate = ""
                    birthplace = ""
                    birthsource = ""
                    birth_ref = person.get_birth_ref()
                    if birth_ref:
                        birth = self.db.get_event_from_handle(birth_ref.ref)
                        if birth:
                            birthdate = self.format_date( birth)
                            birthplace = self.format_place(birth)
                            birthsource = get_primary_source_title(self.db, birth)
                    # Baptism:
                    baptismdate = ""
                    baptismplace = ""
                    baptismsource = ""
                    baptism_ref = get_primary_event_ref_from_type(
                        self.db, person, "Baptism")
                    if baptism_ref:
                        baptism = self.db.get_event_from_handle(baptism_ref.ref)
                        if baptism:
                            baptismdate = self.format_date( baptism)
                            baptismplace = self.format_place(baptism)
                            baptismsource = get_primary_source_title(self.db, baptism)
                    # Death:
                    deathdate = ""
                    deathplace = ""
                    deathsource = ""
                    death_ref = person.get_death_ref()
                    if death_ref:
                        death = self.db.get_event_from_handle(death_ref.ref)
                        if death:
                            deathdate = self.format_date( death)
                            deathplace = self.format_place(death)
                            deathsource = get_primary_source_title(self.db, death)
                    # Burial:
                    burialdate = ""
                    burialplace = ""
                    burialsource = ""
                    burial_ref = get_primary_event_ref_from_type(
                        self.db, person, "Burial")
                    if burial_ref:
                        burial = self.db.get_event_from_handle(burial_ref.ref)
                        if burial:
                            burialdate = self.format_date( burial)
                            burialplace = self.format_place(burial)
                            burialsource = get_primary_source_title(self.db, burial)
                    # Write it out:
                    self.write_csv(grampsid_ref, surname, first_name, callname,
                                   suffix, prefix, title, gender,
                                   birthdate, birthplace, birthsource,
                                   baptismdate, baptismplace, baptismsource,
                                   deathdate, deathplace, deathsource,
                                   burialdate, burialplace, burialsource,
                                   note)
                self.update()
            self.writeln()
        ########################### sort:
        sortorder = []
        for key in self.flist:
            family = self.db.get_family_from_handle(key)
            if family:
                marriage_id = family.get_gramps_id()
                sortorder.append(
                    (sortable_string_representation(marriage_id), key)
                    )
        sortorder.sort() # will sort on tuples
        flist = [data[1] for data in sortorder]
        ###########################
        if self.include_marriages:
            if self.translate_headers:
                self.write_csv(_("Marriage"), _("Husband"), _("Wife"),
                               _("Date"), _("Place"), _("Source"), _("Note"))
            else:
                self.write_csv("Marriage", "Husband", "Wife",
                               "Date", "Place", "Source", "Note")
            for key in flist:
                family = self.db.get_family_from_handle(key)
                if family:
                    marriage_id = family.get_gramps_id()
                    if marriage_id != "":
                        marriage_id = "[" + marriage_id + "]"
                    mother_id = ''
                    father_id = ''
                    father_handle = family.get_father_handle()
                    if father_handle:
                        father = self.db.get_person_from_handle(father_handle)
                        father_id = father.get_gramps_id()
                        if father_id != "":
                            father_id = "[" + father_id + "]"
                    mother_handle = family.get_mother_handle()
                    if mother_handle:
                        mother = self.db.get_person_from_handle(mother_handle)
                        mother_id = mother.get_gramps_id()
                        if mother_id != "":
                            mother_id = "[" + mother_id + "]"
                    # get mdate, mplace
                    mdate, mplace, source = '', '', ''
                    event_ref_list = family.get_event_ref_list()
                    for event_ref in event_ref_list:
                        event = self.db.get_event_from_handle(event_ref.ref)
                        if event.get_type() == EventType.MARRIAGE:
                            mdate = self.format_date( event)
                            mplace = self.format_place(event)
                            source = get_primary_source_title(self.db, event)
                    note = ''
                    self.write_csv(marriage_id, father_id, mother_id, mdate,
                                   mplace, source, note)
                self.update()
            self.writeln()
        if self.include_children:
            if self.translate_headers:
                self.write_csv(_("Family"), _("Child"))
            else:
                self.write_csv("Family", "Child")
            for key in flist:
                family = self.db.get_family_from_handle(key)
                if family:
                    family_id = family.get_gramps_id()
                    if family_id != "":
                        family_id = "[" + family_id + "]"
                    for child_ref in family.get_child_ref_list():
                        child_handle = child_ref.ref
                        child = self.db.get_person_from_handle(child_handle)
                        grampsid = child.get_gramps_id()
                        grampsid_ref = ""
                        if grampsid != "":
                            grampsid_ref = "[" + grampsid + "]"
                        self.write_csv(family_id, grampsid_ref)
                self.update()
            self.writeln()
        self.fp.close()
        return True

    def format_date(self, date):
        return get_date(date)

    def format_place(self, event):
        """
        If places are included in the export return a link, else return a
        formatted place for the given event.
        """
        if self.include_places:
            place_handle = event.get_place_handle()
            if place_handle:
                place = self.db.get_place_from_handle(place_handle)
                if place:
                    return "[%s]" % place.get_gramps_id()
            return ""
        else:
            return _pd.display_event(self.db, event)
