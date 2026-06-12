# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007       Douglas S. Blank
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2008       Raphael Ackerman
# Copyright (C) 2008       Brian G. Matherly
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"Import from CSV Spreadsheet"

import codecs
import csv

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
import logging

# -------------------------------------------------------------------------
#
# Standard Python Modules
#
# -------------------------------------------------------------------------
import mimetypes
import os
import time
from io import TextIOWrapper

from gramps.gen.config import config

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.datehandler import parser as _dp
from gramps.gen.db import DbTxn
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.errors import GrampsImportError as Error
from gramps.gen.lib import (
    Attribute,
    ChildRef,
    Citation,
    Event,
    EventRef,
    EventType,
    Family,
    FamilyRelType,
    Media,
    MediaRef,
    Name,
    NameType,
    Note,
    NoteType,
    Person,
    Place,
    PlaceName,
    PlaceRef,
    PlaceType,
    Source,
    Surname,
    Tag,
)
from gramps.gen.lib.eventroletype import EventRoleType
from gramps.gen.utils.id import create_id
from gramps.gen.utils.libformatting import ImportInfo
from gramps.gen.utils.string import gender as gender_map
from gramps.gen.utils.unknown import create_explanation_note

LOG = logging.getLogger(".ImportCSV")

_ = glocale.translation.sgettext
ngettext = glocale.translation.ngettext  # else "nearby" comments are ignored

# -------------------------------------------------------------------------
#
# Support Functions
#
# -------------------------------------------------------------------------


def get_primary_event_ref_from_type(dbase, person, event_name):
    """
    >>> get_primary_event_ref_from_type(dbase, Person(), "Baptism"):
    """
    for ref in person.event_ref_list:
        if ref.get_role() == EventRoleType.PRIMARY:
            event = dbase.get_event_from_handle(ref.ref)
            if event and event.type.is_type(event_name):
                return ref
    return None


# -------------------------------------------------------------------------
#
# Support and main functions
#
# -------------------------------------------------------------------------
def rd(line_number, row, col, key, default=None):
    """Return Row data by column name"""
    if key in col:
        if col[key] >= len(row):
            LOG.warning("missing '%s, on line %d" % (key, line_number))
            return default
        retval = row[col[key]].strip()
        if retval == "":
            return default
        else:
            return retval
    else:
        return default


def importData(dbase, filename, user):
    """Function called by Gramps to import data on persons in CSV format."""
    if dbase.get_feature("skip-import-additions"):  # don't add source or tags
        parser = CSVParser(dbase, user, None)
    else:
        parser = CSVParser(
            dbase,
            user,
            (
                config.get("preferences.tag-on-import-format")
                if config.get("preferences.tag-on-import")
                else None
            ),
        )
    try:
        with open(filename, "rb") as filehandle:
            line = filehandle.read(3)
            if line == codecs.BOM_UTF8:
                filehandle.seek(0)
                filehandle = TextIOWrapper(
                    filehandle, encoding="utf_8_sig", errors="replace", newline=""
                )
            else:  # just open with OS encoding
                filehandle.seek(0)
                filehandle = TextIOWrapper(filehandle, errors="replace", newline="")
            msg = parser.parse(filehandle)
            if msg:
                user.notify_error(_("Bad references"), msg)
    except EnvironmentError as err:
        user.notify_error(_("%s could not be opened\n") % filename, str(err))
        return
    return ImportInfo({_("Results"): _("done")})


# -------------------------------------------------------------------------
#
# CSV Parser
#
# -------------------------------------------------------------------------
class CSVParser:
    """Class to read data in CSV format from a file object."""

    def __init__(self, dbase, user, default_tag_format=None):
        self.db = dbase
        self.user = user
        self.trans = None
        self.lineno = 0
        self.index = 0
        self.fam_count = 0
        self.indi_count = 0
        self.place_count = 0
        self.pref = {}  # person ref, internal to this sheet
        self.fref = {}  # family ref, internal to this sheet
        self.placeref = {}
        self.eventref = {}
        self.citationref = {}
        self.event_count = 0
        self.citation_count = 0
        self.place_types = {}
        # Build reverse dictionary, name to type number
        for code, trans, untrans in PlaceType._DATAMAP:
            self.place_types[trans] = code
            self.place_types[trans.lower()] = code
            self.place_types[untrans] = code
            self.place_types[untrans.lower()] = code
        # Add custom types:
        for custom_type in self.db.get_place_types():
            self.place_types[custom_type] = 0
            self.place_types[custom_type.lower()] = 0
        self.event_types = {}
        for code, trans, untrans in EventType._DATAMAP:
            self.event_types[trans.lower()] = code
            self.event_types[untrans.lower()] = code
        self.note_types = {}
        for code, trans, untrans in NoteType._DATAMAP:
            self.note_types[trans.lower()] = code
            self.note_types[untrans.lower()] = code
        self.role_types = {}
        for code, trans, untrans in EventRoleType._DATAMAP:
            self.role_types[trans.lower()] = code
            self.role_types[untrans.lower()] = code
        column2label = {
            "surname": ("lastname", "last_name", "surname", _("surname"), _("Surname")),
            "firstname": (
                "firstname",
                "first_name",
                "given_name",
                "given",
                "given name",
                _("given name"),
                _("given"),
                _("Given"),
                _("Given name"),
            ),
            "callname": (
                "call name",
                _("Call name"),
                "callname",
                "call_name",
                "call",
                _("Call"),
                _("call"),
            ),
            "nickname": (
                "nickname",
                _("nickname"),
                "Nickname",
                _("Nickname"),
                "nick",
                _("nick"),
                "Nick",
                _("Nick"),
                "nick_name",
                _("nick_name"),
            ),
            "tag": ("tag", _("tag"), _("Tag")),
            "title": ("title", _("title"), _("title", "Person or Place")),
            "prefix": ("prefix", _("prefix"), _("Prefix")),
            "suffix": ("suffix", _("suffix"), _("Suffix")),
            "gender": ("gender", _("gender"), _("Gender")),
            "source": ("source", _("source"), _("Source")),
            "note": ("note", _("note"), _("Note")),
            "birthplace": (
                "birthplace",
                "birth_place",
                "birth place",
                _("birth place"),
                _("Birth place"),
            ),
            "birthplace_id": (
                "birthplaceid",
                "birth_place_id",
                "birth place id",
                _("birth place id"),
                "birthplace_id",
            ),
            "birthdate": ("birthdate", "birth_date", "birth date", _("birth date")),
            "birthsource": (
                "birthsource",
                "birth_source",
                "birth source",
                _("birth source"),
            ),
            "baptismplace": ("baptismplace", "baptism place", _("baptism place")),
            "baptismplace_id": (
                "baptismplaceid",
                "baptism place id",
                _("baptism place id"),
                "baptism_place_id",
                "baptismplace_id",
            ),
            "baptismdate": ("baptismdate", "baptism date", _("baptism date")),
            "baptismsource": ("baptismsource", "baptism source", _("baptism source")),
            "burialplace": ("burialplace", "burial place", _("burial place")),
            "burialplace_id": (
                "burialplaceid",
                "burial place id",
                _("burial place id"),
                "burial_place_id",
                "burialplace_id",
            ),
            "burialdate": ("burialdate", "burial date", _("burial date")),
            "burialsource": ("burialsource", "burial source", _("burial source")),
            "deathplace": (
                "deathplace",
                "death_place",
                "death place",
                _("death place"),
            ),
            "deathplace_id": (
                "deathplaceid",
                "death place id",
                _("death place id"),
                "death_place_id",
                "deathplace_id",
            ),
            "deathdate": ("deathdate", "death_date", "death date", _("death date")),
            "deathsource": (
                "deathsource",
                "death_source",
                "death source",
                _("death source"),
            ),
            "deathcause": (
                "deathcause",
                "death_cause",
                "death cause",
                _("death cause"),
            ),
            "grampsid": (_("Gramps ID"), "grampsid", "id", "gramps_id", "gramps id"),
            "person": ("person", _("person"), _("Person")),
            "occupationdescr": (
                "occupationdescr",
                _("occupationdescr"),
                _("Occupation description"),
            ),
            "occupationdate": (
                "occupationdate",
                _("occupationdate"),
                _("Occupation date"),
            ),
            "occupationplace": (
                "occupationplace",
                _("occupationplace"),
                _("Occupation place"),
            ),
            "occupationplace_id": (
                "occupationplace_id",
                _("occupationplace_id"),
                _("Occupation place id"),
            ),
            "occupationsource": (
                "occupationsource",
                _("occupationsource"),
                _("Occupation source"),
            ),
            "residencedate": ("residencedate", _("residencedate"), _("residence date")),
            "residenceplace": (
                "residenceplace",
                _("residenceplace"),
                _("residence place"),
            ),
            "residenceplace_id": (
                "residenceplace_id",
                _("residenceplace_id"),
                _("residence place id"),
            ),
            "residencesource": (
                "residencesource",
                _("residencesource"),
                _("residence source"),
            ),
            "attributetype": ("attributetype", _("attributetype"), _("attribute type")),
            "attributevalue": (
                "attributevalue",
                _("attributevalue"),
                _("attribute value"),
            ),
            "attributesource": (
                "attributesource",
                _("attributesource"),
                _("attribute source"),
            ),
            # ----------------------------------
            "child": ("child", _("child"), _("Child")),
            "family": ("family", _("family"), _("Family")),
            # ----------------------------------
            "wife": (
                "mother",
                _("mother"),
                _("Mother"),
                "wife",
                _("wife"),
                _("Wife"),
                "parent2",
                _("parent2"),
            ),
            "husband": (
                "father",
                _("father"),
                _("Father"),
                "husband",
                _("husband"),
                _("Husband"),
                "parent1",
                _("parent1"),
            ),
            "marriage": ("marriage", _("marriage"), _("Marriage")),
            "date": ("date", _("date"), _("Date")),
            "place": ("place", _("place"), _("Place")),
            "place_id": ("place id", "place_id", "placeid", _("place id")),
            "name": ("name", _("name"), _("Name")),
            "type": ("type", _("type"), _("Type")),
            "latitude": ("latitude", _("latitude")),
            "longitude": ("longitude", _("longitude")),
            "code": ("code", _("code"), _("Code")),
            "enclosed_by": (
                "enclosed by",
                _("enclosed by"),
                "enclosed_by",
                _("enclosed_by"),
                "enclosedby",
            ),
            "eventtype": (
                "eventtype",
                "event type",
                _("event type"),
                _("Event type"),
            ),
            "description": (
                "description",
                "descr",
                _("description"),
                _("Description"),
            ),
            "role": ("role", _("role"), _("Role")),
            "citation": ("citation", _("citation"), _("Citation")),
            "page": ("page", _("page"), _("Page")),
            "confidence": ("confidence", _("confidence"), _("Confidence")),
            "note_type": (
                "note_type",
                "note type",
                _("note type"),
                _("Note type"),
            ),
            "media": ("media", _("media"), _("Media")),
            "media_description": (
                "media_description",
                "media description",
                _("media description"),
                _("Media description"),
            ),
            "media_date": (
                "media_date",
                "media date",
                _("media date"),
                _("Media date"),
            ),
        }
        lab2col_dict = []
        for key in list(column2label.keys()):
            for val in column2label[key]:
                lab2col_dict.append((val.lower(), key))
        self.label2column = dict(lab2col_dict)
        if default_tag_format:
            name = time.strftime(default_tag_format)
            tag = self.db.get_tag_from_name(name)
            if tag:
                self.default_tag = tag
            else:
                self.default_tag = Tag()
                self.default_tag.set_name(name)
        else:
            self.default_tag = None

    def cleanup_column_name(self, column):
        """Handle column aliases for CSV spreadsheet import and SQL."""
        return self.label2column.get(column, column)

    def read_csv(self, filehandle):
        "Read the data from the file and return it as a list."
        my_dialect = config.get("csv.dialect")
        my_delimiter = config.get("csv.delimiter")
        try:
            if my_dialect == _("Custom"):
                data = [
                    [r.strip() for r in row]
                    for row in csv.reader(filehandle, delimiter=my_delimiter)
                ]
            else:
                data = [
                    [r.strip() for r in row]
                    for row in csv.reader(filehandle, dialect=my_dialect)
                ]
        except csv.Error as err:
            self.user.notify_error(
                _("format error: line %(line)d: %(zero)s")
                % {"line": csv.reader.line_num, "zero": err}
            )
            return None
        return data

    def lookup(self, type_, id_):
        """
        Return the object of type type_ with id id_ from db or previously
        stored value.
        """
        if id_ is None:
            return None
        if type_ == "family":
            if id_.startswith("[") and id_.endswith("]"):
                id_ = self.db.fid2user_format(id_[1:-1])
                db_lookup = self.db.get_family_from_gramps_id(id_)
                if db_lookup is None:
                    return self.lookup(type_, id_)
                else:
                    return db_lookup
            else:
                id_ = self.db.fid2user_format(id_)
                if id_.lower() in self.fref:
                    return self.fref[id_.lower()]
                else:
                    return None
        elif type_ == "person":
            if id_.startswith("[") and id_.endswith("]"):
                id_ = self.db.id2user_format(id_[1:-1])
                db_lookup = self.db.get_person_from_gramps_id(id_)
                if db_lookup is None:
                    return self.lookup(type_, id_)
                else:
                    return db_lookup
            else:
                id_ = self.db.id2user_format(id_)
                if id_.lower() in self.pref:
                    return self.pref[id_.lower()]
                else:
                    return None
        elif type_ == "place":
            if id_.startswith("[") and id_.endswith("]"):
                id_ = self.db.pid2user_format(id_[1:-1])
                db_lookup = self.db.get_place_from_gramps_id(id_)
                if db_lookup is None:
                    return self.lookup(type_, id_)
                else:
                    return db_lookup
            else:
                id_ = self.db.pid2user_format(id_)
                if id_.lower() in self.placeref:
                    return self.placeref[id_.lower()]
                else:
                    return None
        elif type_ == "event":
            if id_.startswith("[") and id_.endswith("]"):
                id_ = self.db.eid2user_format(id_[1:-1])
                db_lookup = self.db.get_event_from_gramps_id(id_)
                if db_lookup is None:
                    return self.lookup(type_, id_)
                else:
                    return db_lookup
            else:
                id_ = self.db.eid2user_format(id_)
                if id_.lower() in self.eventref:
                    return self.eventref[id_.lower()]
                else:
                    return None
        elif type_ == "citation":
            if id_.startswith("[") and id_.endswith("]"):
                id_ = self.db.cid2user_format(id_[1:-1])
                db_lookup = self.db.get_citation_from_gramps_id(id_)
                if db_lookup is None:
                    return self.lookup(type_, id_)
                else:
                    return db_lookup
            else:
                id_ = self.db.cid2user_format(id_)
                if id_.lower() in self.citationref:
                    return self.citationref[id_.lower()]
                else:
                    return None
        else:
            LOG.warning("invalid lookup type in CSV import: '%s'" % type_)
            return None

    def storeup(self, type_, id_, object_):
        "Store object object_ of type type_ in a dictionary under key id_."
        if id_.startswith("[") and id_.endswith("]"):
            id_ = id_[1:-1]
            # return # do not store gramps people; go look them up
        if type_ == "person":
            id_ = self.db.id2user_format(id_)
            self.pref[id_.lower()] = object_
        elif type_ == "family":
            id_ = self.db.fid2user_format(id_)
            self.fref[id_.lower()] = object_
        elif type_ == "place":
            id_ = self.db.pid2user_format(id_)
            self.placeref[id_.lower()] = object_
        elif type_ == "event":
            id_ = self.db.eid2user_format(id_)
            self.eventref[id_.lower()] = object_
        elif type_ == "citation":
            id_ = self.db.cid2user_format(id_)
            self.citationref[id_.lower()] = object_
        else:
            LOG.warning("invalid storeup type in CSV import: '%s'" % type_)

    def parse(self, filehandle):
        """
        Prepare the database and parse the input file.

        :param filehandle: open file handle positioned at start of the file
        """
        progress_title = _("CSV Import")
        with self.user.progress(progress_title, _("Reading data..."), 1) as step:
            data = self.read_csv(filehandle)

        with self.user.progress(
            progress_title, _("Importing data..."), len(data)
        ) as step:
            tym = time.time()
            self.db.disable_signals()
            with DbTxn(_("CSV import"), self.db, batch=True) as self.trans:
                if self.default_tag and self.default_tag.handle is None:
                    self.db.add_tag(self.default_tag, self.trans)
                self._parse_csv_data(data, step)
                err_msg = self._check_refs()
            self.db.enable_signals()
            self.db.request_rebuild()
            tym = time.time() - tym
            # Translators: leave all/any {...} untranslated
            msg = ngettext(
                "Import Complete: {number_of} second",
                "Import Complete: {number_of} seconds",
                tym,
            ).format(number_of=tym)
            LOG.debug(msg)
            LOG.debug("New Families: %d" % self.fam_count)
            LOG.debug("New Individuals: %d" % self.indi_count)
            LOG.debug("New Places: %d" % self.place_count)
            LOG.debug("New Events: %d" % self.event_count)
            LOG.debug("New Citations: %d" % self.citation_count)
        return err_msg

    def _check_refs(self):
        """Check that forward cross references were satisfied"""
        txt = ""
        expl_note = create_explanation_note(self.db)
        for key in self.placeref:
            place = self.placeref[key]
            if place.name.value == _("Unknown"):
                txt = (", " + key) if txt else key
                place.add_note(expl_note.handle)
                self.db.commit_place(place, self.trans)
        if txt:
            self.db.commit_note(expl_note, self.trans, time.time())
            return _("The following IDs were referenced but not found:\n" + txt)
        else:
            return None

    def _parse_csv_data(self, data, step):
        """Parse each line of the input data and act accordingly."""
        self.lineno = 0
        self.index = 0
        self.fam_count = 0
        self.indi_count = 0
        self.place_count = 0
        self.event_count = 0
        self.citation_count = 0
        self.pref = {}  # person ref, internal to this sheet
        self.fref = {}  # family ref, internal to this sheet
        self.placeref = {}
        self.eventref = {}
        self.citationref = {}
        header = None
        line_number = 0
        for row in data:
            step()
            line_number += 1
            if "".join(row) == "":  # no blanks are allowed inside a table
                header = None  # clear headers, ready for next "table"
                continue
            ######################################
            if header is None:
                header = [self.cleanup_column_name(r.lower()) for r in row]
                col = {}
                count = 0
                for key in header:
                    col[key] = count
                    count += 1
                continue
            # different kinds of data: person, family, marriage, place, event, citation
            if ("marriage" in header) or ("husband" in header) or ("wife" in header):
                self._parse_marriage(line_number, row, col)
            elif "eventtype" in header:
                self._parse_event(line_number, row, col)
            elif "citation" in header:
                self._parse_citation(line_number, row, col)
            elif "family" in header:
                self._parse_family(line_number, row, col)
            elif any(("surname" in header, "person" in header)):
                self._parse_person(line_number, row, col)
            elif "place" in header:
                self._parse_place(line_number, row, col)
            else:
                LOG.warning("ignoring line %d" % line_number)
        return None

    def _parse_marriage(self, line_number, row, col):
        "Parse the content of a Marriage,Husband,Wife line."
        marriage_ref = rd(line_number, row, col, "marriage")
        husband = rd(line_number, row, col, "husband")
        wife = rd(line_number, row, col, "wife")
        marriagedate = rd(line_number, row, col, "date")
        marriageplace = rd(line_number, row, col, "place")
        marriageplace_id = rd(line_number, row, col, "place_id")
        marriagesource = rd(line_number, row, col, "source")
        note = rd(line_number, row, col, "note")
        tag = rd(line_number, row, col, "tag")
        wife = self.lookup("person", wife)
        husband = self.lookup("person", husband)

        if (
            husband is None
            and wife is None
            and (tag is not None or note is not None)
            and marriage_ref is not None
        ):
            # Just adding a note or tag to a marriage event
            marriage = self.lookup("event", marriage_ref)
            if marriage is None:
                LOG.warning("no marriage found for ref %s" % marriage_ref)
                return
            if tag:
                self.add_tag(marriage, tag)
            if note:
                self.add_note(NoteType.EVENT, marriage, note)
            self.db.commit_event(marriage, self.trans)
            return

        # Below, we assume editing/creating a family

        if husband is None and wife is None and marriage_ref is None:
            # might have children, so go ahead and add
            LOG.warning("no parents on line %d; adding family anyway" % line_number)

        family = self.get_or_create_family(marriage_ref, husband, wife)
        # adjust gender, if not already provided
        if husband:
            # this is just a guess, if unknown
            if husband.get_gender() == Person.UNKNOWN:
                husband.set_gender(Person.MALE)
                self.db.commit_person(husband, self.trans)
        if wife:
            # this is just a guess, if unknown
            if wife.get_gender() == Person.UNKNOWN:
                wife.set_gender(Person.FEMALE)
                self.db.commit_person(wife, self.trans)
        if marriage_ref:
            self.storeup("family", marriage_ref, family)
        if marriagesource:
            # add, if new
            new, marriagesource = self.get_or_create_source(marriagesource)
        if marriageplace and marriageplace_id:
            raise Error("Error in marriage: can't have a place and place_id")
        if marriageplace:
            # add, if new
            new, marriageplace = self.get_or_create_place(marriageplace)
        elif marriageplace_id:
            # better exist already, locally or in database:
            marriageplace = self.lookup("place", marriageplace_id)
        if marriagedate:
            marriagedate = _dp.parse(marriagedate)
        if marriagedate or marriageplace or marriagesource:
            # add, if new; replace, if different
            new, marriage = self.get_or_create_event(
                family, EventType.MARRIAGE, marriagedate, marriageplace, marriagesource
            )
            if new:
                mar_ref = EventRef()
                mar_ref.set_reference_handle(marriage.get_handle())
                mar_ref.set_role(EventRoleType(EventRoleType.FAMILY))
                family.add_event_ref(mar_ref)
            if tag:
                self.add_tag(marriage, tag)
            if note:
                self.add_note(NoteType.EVENT, marriage, note)
            self.db.commit_event(marriage, self.trans)

        self.db.commit_family(family, self.trans)

    def _parse_family(self, line_number, row, col):
        "Parse the content of a family line"
        family_ref = rd(line_number, row, col, "family")
        if family_ref is None:
            LOG.warning("no family reference found for family on line %d" % line_number)
            return  # required
        source = rd(line_number, row, col, "source")
        note = rd(line_number, row, col, "note")
        gender = rd(line_number, row, col, "gender")
        tag = rd(line_number, row, col, "tag")
        child_ref = rd(line_number, row, col, "child")
        child = self.lookup("person", child_ref)
        family = self.lookup("family", family_ref)
        if family is None:
            LOG.warning(
                "no matching family reference found for family "
                "on line %d" % line_number
            )
            return
        if child:
            # is this child already in this family? If so, don't add
            LOG.debug("children: %s", [ref.ref for ref in family.get_child_ref_list()])
            LOG.debug("looking for: %s", child.get_handle())
            if child.get_handle() not in [
                ref.ref for ref in family.get_child_ref_list()
            ]:
                # add child to family
                LOG.debug(
                    "   adding child [%s] to family [%s]",
                    child.get_gramps_id(),
                    family.get_gramps_id(),
                )
                childref = ChildRef()
                childref.set_reference_handle(child.get_handle())
                family.add_child_ref(childref)
                self.db.commit_family(family, self.trans)
                child.add_parent_family_handle(family.get_handle())
            if gender:
                # replace
                gender = gender.lower()
                if gender == gender_map[Person.MALE].lower():
                    gender = Person.MALE
                elif gender == gender_map[Person.FEMALE].lower():
                    gender = Person.FEMALE
                elif gender == gender_map[Person.OTHER].lower():
                    gender = Person.OTHER
                else:
                    gender = Person.UNKNOWN
                child.set_gender(gender)
            if source:
                dummy_new, source = self.get_or_create_source(source)
                self.find_and_set_citation(child, source)
            if tag is not None:
                self.add_tag(child, tag)
            if note:
                self.add_note(NoteType.PERSON, child, note)

            self.db.commit_person(child, self.trans)

        else:  # not a child; note and tag refers to family
            if tag is not None:
                self.add_tag(family, tag)
            if note:
                self.add_note(NoteType.EVENT, family, note)

        self.db.commit_family(family, self.trans)

    def _parse_person(self, line_number, row, col):
        "Parse the content of a Person line."
        surname = rd(line_number, row, col, "surname")
        firstname = rd(line_number, row, col, "firstname")
        callname = rd(line_number, row, col, "callname")
        nickname = rd(line_number, row, col, "nickname")
        tag = rd(line_number, row, col, "tag")
        title = rd(line_number, row, col, "title")
        prefix = rd(line_number, row, col, "prefix")
        suffix = rd(line_number, row, col, "suffix")
        gender = rd(line_number, row, col, "gender")
        source = rd(line_number, row, col, "source")
        note = rd(line_number, row, col, "note")
        birthplace = rd(line_number, row, col, "birthplace")
        birthplace_id = rd(line_number, row, col, "birthplace_id")
        birthdate = rd(line_number, row, col, "birthdate")
        birthsource = rd(line_number, row, col, "birthsource")
        baptismplace = rd(line_number, row, col, "baptismplace")
        baptismplace_id = rd(line_number, row, col, "baptismplace_id")
        baptismdate = rd(line_number, row, col, "baptismdate")
        baptismsource = rd(line_number, row, col, "baptismsource")
        burialplace = rd(line_number, row, col, "burialplace")
        burialplace_id = rd(line_number, row, col, "burialplace_id")
        burialdate = rd(line_number, row, col, "burialdate")
        burialsource = rd(line_number, row, col, "burialsource")
        deathplace = rd(line_number, row, col, "deathplace")
        deathplace_id = rd(line_number, row, col, "deathplace_id")
        deathdate = rd(line_number, row, col, "deathdate")
        deathsource = rd(line_number, row, col, "deathsource")
        deathcause = rd(line_number, row, col, "deathcause")
        grampsid = rd(line_number, row, col, "grampsid")
        person_ref = rd(line_number, row, col, "person")
        occupationdescr = rd(line_number, row, col, "occupationdescr")
        occupationplace = rd(line_number, row, col, "occupationplace")
        occupationplace_id = rd(line_number, row, col, "occupationplace_id")
        occupationsource = rd(line_number, row, col, "occupationsource")
        occupationdate = rd(line_number, row, col, "occupationdate")
        residencedate = rd(line_number, row, col, "residencedate")
        residenceplace = rd(line_number, row, col, "residenceplace")
        residenceplace_id = rd(line_number, row, col, "residenceplace_id")
        residencesource = rd(line_number, row, col, "residencesource")
        attributetype = rd(line_number, row, col, "attributetype")
        attributevalue = rd(line_number, row, col, "attributevalue")
        attributesource = rd(line_number, row, col, "attributesource")

        #########################################################
        # if this person already exists, don't create them
        person = self.lookup("person", person_ref)
        if person is None:
            if surname is None:
                LOG.warning("empty surname for new person on line %d" % line_number)
                surname = ""
            # new person — resolve gramps_id before db.add_person() so the
            # auto-generated ID does not overwrite the one from the CSV.
            resolved_id = None
            if grampsid is not None:
                resolved_id = grampsid
            elif (
                person_ref is not None
                and person_ref.startswith("[")
                and person_ref.endswith("]")
            ):
                resolved_id = self.db.id2user_format(person_ref[1:-1])
            person = self.create_person(resolved_id)
            name = Name()
            name.set_type(NameType(NameType.BIRTH))
            if firstname is not None:
                name.set_first_name(firstname)
            surname_obj = Surname()
            if surname is not None:
                surname_obj.set_surname(surname)
            name.add_surname(surname_obj)
            person.set_primary_name(name)
        else:
            name = person.get_primary_name()
        #########################################################
        if person_ref is not None:
            self.storeup("person", person_ref, person)
        # replace
        if surname is not None:
            name.get_primary_surname().set_surname(surname)
        if firstname is not None:
            name.set_first_name(firstname)
        if callname is not None:
            name.set_call_name(callname)
        if nickname is not None:
            name.set_nick_name(nickname)
        if title is not None:
            name.set_title(title)
        if prefix is not None:
            name.get_primary_surname().set_prefix(prefix)
            name.group_as = ""  # HELP? what should I do here?
        if suffix is not None:
            name.set_suffix(suffix)
        if note is not None:
            # append notes, if previous notes
            previous_notes_list = person.get_note_list()
            updated_note = False
            for note_handle in previous_notes_list:
                previous_note = self.db.get_note_from_handle(note_handle)
                if previous_note.type == NoteType.PERSON:
                    previous_text = previous_note.get()
                    if note not in previous_text:
                        note = previous_text + "\n" + note
                    previous_note.set(note)
                    self.db.commit_note(previous_note, self.trans)
                    updated_note = True
                    break
            if not updated_note:
                # add new note here
                new_note = Note()
                new_note.handle = create_id()
                new_note.type.set(NoteType.PERSON)
                new_note.set(note)
                if self.default_tag:
                    new_note.add_tag(self.default_tag.handle)
                self.db.add_note(new_note, self.trans)
                person.add_note(new_note.handle)
        if person.get_gender() == Person.UNKNOWN and gender is not None:
            gender = gender.lower()
            if gender == gender_map[Person.MALE].lower():
                gender = Person.MALE
            elif gender == gender_map[Person.FEMALE].lower():
                gender = Person.FEMALE
            elif gender == gender_map[Person.OTHER].lower():
                gender = Person.OTHER
            else:
                gender = Person.UNKNOWN
            person.set_gender(gender)
        if tag is not None:
            self.add_tag(person, tag)
        #########################################################
        # add if new, replace if different
        # Birth:
        if birthdate is not None:
            birthdate = _dp.parse(birthdate)
        if birthplace and birthplace_id:
            raise Error("Error in person: can't have a birthplace and birthplace_id")
        if birthplace is not None:
            new, birthplace = self.get_or_create_place(birthplace)
        elif birthplace_id:
            # better exist already, locally or in database:
            birthplace = self.lookup("place", birthplace_id)
        if birthsource is not None:
            new, birthsource = self.get_or_create_source(birthsource)
        if birthdate or birthplace or birthsource:
            new, birth = self.get_or_create_event(
                person, EventType.BIRTH, birthdate, birthplace, birthsource
            )
            birth_ref = person.get_birth_ref()
            if birth_ref is None:
                # new
                birth_ref = EventRef()
            birth_ref.set_reference_handle(birth.get_handle())
            person.set_birth_ref(birth_ref)
        # Baptism:
        if baptismdate is not None:
            baptismdate = _dp.parse(baptismdate)
        if baptismplace and baptismplace_id:
            raise Error(
                "Error in person: can't have a baptismplace and baptismplace_id"
            )
        if baptismplace is not None:
            new, baptismplace = self.get_or_create_place(baptismplace)
        elif baptismplace_id:
            # better exist already, locally or in database:
            baptismplace = self.lookup("place", baptismplace_id)
        if baptismsource is not None:
            new, baptismsource = self.get_or_create_source(baptismsource)
        if baptismdate or baptismplace or baptismsource:
            new, baptism = self.get_or_create_event(
                person, EventType.BAPTISM, baptismdate, baptismplace, baptismsource
            )
            baptism_ref = get_primary_event_ref_from_type(self.db, person, "Baptism")
            if baptism_ref is None:
                # new
                baptism_ref = EventRef()
            baptism_ref.set_reference_handle(baptism.get_handle())
            person.add_event_ref(baptism_ref)
        # Death:
        if deathdate is not None:
            deathdate = _dp.parse(deathdate)
        if deathplace and deathplace_id:
            raise Error("Error in person: can't have a deathplace and deathplace_id")
        if deathplace is not None:
            new, deathplace = self.get_or_create_place(deathplace)
        elif deathplace_id:
            # better exist already, locally or in database:
            deathplace = self.lookup("place", deathplace_id)
        if deathsource is not None:
            new, deathsource = self.get_or_create_source(deathsource)
        if deathdate or deathplace or deathsource or deathcause:
            new, death = self.get_or_create_event(
                person, EventType.DEATH, deathdate, deathplace, deathsource
            )
            if deathcause:
                death.set_description(deathcause)
                self.db.commit_event(death, self.trans)
            death_ref = person.get_death_ref()
            if death_ref is None:
                # new
                death_ref = EventRef()
            death_ref.set_reference_handle(death.get_handle())
            person.set_death_ref(death_ref)
        # Burial:
        if burialdate is not None:
            burialdate = _dp.parse(burialdate)
        if burialplace and burialplace_id:
            raise Error("Error in person: can't have a burialplace and burialplace_id")
        if burialplace is not None:
            new, burialplace = self.get_or_create_place(burialplace)
        elif burialplace_id:
            # better exist already, locally or in database:
            burialplace = self.lookup("place", burialplace_id)
        if burialsource is not None:
            new, burialsource = self.get_or_create_source(burialsource)
        if burialdate or burialplace or burialsource:
            new, burial = self.get_or_create_event(
                person, EventType.BURIAL, burialdate, burialplace, burialsource
            )
            burial_ref = get_primary_event_ref_from_type(self.db, person, "Burial")
            if burial_ref is None:
                # new
                burial_ref = EventRef()
            burial_ref.set_reference_handle(burial.get_handle())
            person.add_event_ref(burial_ref)
        if source:
            # add, if new
            new, source = self.get_or_create_source(source)
            self.find_and_set_citation(person, source)

        # Attribute
        # update existing custom attribute or create it
        if attributevalue is not None:
            new, attr = self.get_or_create_attribute(
                person, attributetype, attributevalue, attributesource
            )

        # Occupation:
        # Contrary to the fields above,
        # each line in the csv will add a new occupation event
        if occupationdescr is not None:  # if no description we have no info to add
            if occupationdate is not None:
                occupationdate = _dp.parse(occupationdate)
            # occupation place takes precedence over place id if both are set
            if occupationplace is not None:
                new, occupationplace = self.get_or_create_place(occupationplace)
            elif occupationplace_id:
                occupationplace = self.lookup("place", occupationplace_id)
            if occupationsource is not None:
                new, occupationsource = self.get_or_create_source(occupationsource)
            new, occupation = self.get_or_create_event(
                person,
                EventType.OCCUPATION,
                occupationdate,
                occupationplace,
                occupationsource,
                occupationdescr,
                True,
            )
            occupation_ref = EventRef()
            occupation_ref.set_reference_handle(occupation.get_handle())
            person.add_event_ref(occupation_ref)

        # Residence:
        # Contrary to the fields above occupation,
        # each line in the csv will add a new residence event
        if residencedate is not None:
            residencedate = _dp.parse(residencedate)
        # residence  place takes precedence over place id if both are set
        if residenceplace is not None:
            new, residenceplace = self.get_or_create_place(residenceplace)
        elif residenceplace_id:
            residenceplace = self.lookup("place", residenceplace_id)
        if residencesource is not None:
            new, residencesource = self.get_or_create_source(residencesource)
        if residencedate or residenceplace or residencesource:
            new, residence = self.get_or_create_event(
                person,
                EventType.RESIDENCE,
                residencedate,
                residenceplace,
                residencesource,
                None,
                True,
            )
            residence_ref = EventRef()
            residence_ref.set_reference_handle(residence.get_handle())
            person.add_event_ref(residence_ref)

        self.db.commit_person(person, self.trans)

    def _parse_place(self, line_number, row, col):
        "Parse the content of a Place line."
        place_id = rd(line_number, row, col, "place")
        place_title = rd(line_number, row, col, "title")
        place_name = rd(line_number, row, col, "name")
        place_type_str = rd(line_number, row, col, "type")
        place_latitude = rd(line_number, row, col, "latitude")
        place_longitude = rd(line_number, row, col, "longitude")
        place_code = rd(line_number, row, col, "code")
        place_enclosed_by_id = rd(line_number, row, col, "enclosed_by")
        place_date = rd(line_number, row, col, "date")
        tag = rd(line_number, row, col, "tag")
        #########################################################
        # if this place already exists, don't create it
        place = self.lookup("place", place_id)
        if place is None:
            # new place — resolve gramps_id before db.add_place()
            resolved_id = None
            if (
                place_id is not None
                and place_id.startswith("[")
                and place_id.endswith("]")
            ):
                resolved_id = self.db.pid2user_format(place_id[1:-1])
            place = self.create_place(resolved_id)
            if place_id is not None:
                self.storeup("place", place_id, place)
        if place_title is not None:
            place.title = place_title
        if tag is not None:
            self.add_tag(place, tag)
        if place_name is not None:
            place.name = PlaceName(value=place_name)
        if place_type_str is not None:
            place.place_type = self.get_place_type(place_type_str)
        if place_latitude is not None:
            place.lat = place_latitude
        if place_longitude is not None:
            place.long = place_longitude
        if place_code is not None:
            place.code = place_code
        if place_enclosed_by_id is not None:
            place_enclosed_by = self.lookup("place", place_enclosed_by_id)
            if place_enclosed_by is None:
                # Not yet found in import, so store for later
                enclosed_id = None
                if place_enclosed_by_id.startswith(
                    "["
                ) and place_enclosed_by_id.endswith("]"):
                    enclosed_id = self.db.pid2user_format(place_enclosed_by_id[1:-1])
                place_enclosed_by = self.create_place(enclosed_id)
                place_enclosed_by.name.set_value(_("Unknown"))
                self.storeup("place", place_enclosed_by_id, place_enclosed_by)
            for placeref in place.placeref_list:
                if place_enclosed_by.handle == placeref.ref:
                    break
            else:
                placeref = PlaceRef()
                placeref.ref = place_enclosed_by.handle
                place.placeref_list.append(placeref)
            if place_date:
                placeref.date = _dp.parse(place_date)
        #########################################################
        self.db.commit_place(place, self.trans)

    def _resolve_type(self, type_class, type_map, value):
        """Return a type_class instance for value, falling back to custom."""
        key = value.lower()
        if key in type_map:
            return type_class(type_map[key])
        return type_class((0, value))

    def _parse_confidence(self, value, line_number):
        """Return a Citation confidence integer from a string or digit."""
        conf_map = {
            "very low": Citation.CONF_VERY_LOW,
            "low": Citation.CONF_LOW,
            "normal": Citation.CONF_NORMAL,
            "high": Citation.CONF_HIGH,
            "very high": Citation.CONF_VERY_HIGH,
        }
        if value.isdigit():
            int_val = int(value)
            if 0 <= int_val <= 4:
                return int_val
        key = value.lower()
        if key in conf_map:
            return conf_map[key]
        LOG.warning(
            "unrecognised confidence '%s' on line %d, defaulting to Normal"
            % (value, line_number)
        )
        return Citation.CONF_NORMAL

    def _parse_event(self, line_number, row, col):
        """Parse the content of an Event line."""
        event_ref = rd(line_number, row, col, "event")
        eventtype = rd(line_number, row, col, "eventtype")
        date = rd(line_number, row, col, "date")
        place = rd(line_number, row, col, "place")
        description = rd(line_number, row, col, "description")
        source = rd(line_number, row, col, "source")
        note = rd(line_number, row, col, "note")
        note_type = rd(line_number, row, col, "note_type")
        tag = rd(line_number, row, col, "tag")
        person_ref = rd(line_number, row, col, "person")
        family_ref = rd(line_number, row, col, "family")
        role = rd(line_number, row, col, "role")
        media = rd(line_number, row, col, "media")
        media_description = rd(line_number, row, col, "media_description")
        media_date = rd(line_number, row, col, "media_date")

        event = self.lookup("event", event_ref) if event_ref else None
        if event is None:
            if eventtype is None:
                LOG.warning("no eventtype for new event on line %d" % line_number)
                return
            event = Event()
            event.set_type(self._resolve_type(EventType, self.event_types, eventtype))
            if (
                event_ref is not None
                and event_ref.startswith("[")
                and event_ref.endswith("]")
            ):
                event.set_gramps_id(self.db.eid2user_format(event_ref[1:-1]))
            if self.default_tag:
                event.add_tag(self.default_tag.handle)
            self.db.add_event(event, self.trans)
            self.event_count += 1
        else:
            if eventtype is not None:
                event.set_type(
                    self._resolve_type(EventType, self.event_types, eventtype)
                )
        if event_ref is not None:
            self.storeup("event", event_ref, event)
        if date is not None:
            event.set_date_object(_dp.parse(date))
        if place is not None:
            new, place_obj = self.get_or_create_place(place)
            event.set_place_handle(place_obj.get_handle())
        if description is not None:
            event.set_description(description)
        if source is not None:
            new, source_obj = self.get_or_create_source(source)
            self.find_and_set_citation(event, source_obj)
        if note is not None:
            resolved_note_type = (
                self._resolve_type(NoteType, self.note_types, note_type)
                if note_type is not None
                else NoteType(NoteType.EVENT)
            )
            self.add_note(resolved_note_type, event, note)
        if tag is not None:
            self.add_tag(event, tag)
        if media is not None:
            new, media_obj = self.get_or_create_media(
                media, media_description, media_date
            )
            media_ref = MediaRef()
            media_ref.set_reference_handle(media_obj.get_handle())
            event.add_media_reference(media_ref)
        self.db.commit_event(event, self.trans)
        if person_ref is not None:
            person = self.lookup("person", person_ref)
            if person is None:
                LOG.warning(
                    "person ref '%s' not found on line %d" % (person_ref, line_number)
                )
            else:
                role_type = (
                    self._resolve_type(EventRoleType, self.role_types, role)
                    if role is not None
                    else EventRoleType(EventRoleType.PRIMARY)
                )
                eref = EventRef()
                eref.set_reference_handle(event.get_handle())
                eref.set_role(role_type)
                person.add_event_ref(eref)
                self.db.commit_person(person, self.trans)
        if family_ref is not None:
            family = self.lookup("family", family_ref)
            if family is None:
                LOG.warning(
                    "family ref '%s' not found on line %d" % (family_ref, line_number)
                )
            else:
                role_type = (
                    self._resolve_type(EventRoleType, self.role_types, role)
                    if role is not None
                    else EventRoleType(EventRoleType.FAMILY)
                )
                eref = EventRef()
                eref.set_reference_handle(event.get_handle())
                eref.set_role(role_type)
                family.add_event_ref(eref)
                self.db.commit_family(family, self.trans)

    def _parse_citation(self, line_number, row, col):
        """Parse the content of a Citation line."""
        citation_ref = rd(line_number, row, col, "citation")
        source = rd(line_number, row, col, "source")
        page = rd(line_number, row, col, "page")
        date = rd(line_number, row, col, "date")
        confidence = rd(line_number, row, col, "confidence")
        note = rd(line_number, row, col, "note")
        note_type = rd(line_number, row, col, "note_type")
        tag = rd(line_number, row, col, "tag")
        person_ref = rd(line_number, row, col, "person")
        family_ref = rd(line_number, row, col, "family")
        event_ref = rd(line_number, row, col, "event")
        place_ref = rd(line_number, row, col, "place")
        media = rd(line_number, row, col, "media")
        media_description = rd(line_number, row, col, "media_description")
        media_date = rd(line_number, row, col, "media_date")

        citation = self.lookup("citation", citation_ref) if citation_ref else None
        if citation is None:
            if source is None:
                LOG.warning("no source for new citation on line %d" % line_number)
                return
            citation = Citation()
            new, source_obj = self.get_or_create_source(source)
            citation.set_reference_handle(source_obj.get_handle())
            if (
                citation_ref is not None
                and citation_ref.startswith("[")
                and citation_ref.endswith("]")
            ):
                citation.set_gramps_id(self.db.cid2user_format(citation_ref[1:-1]))
            if self.default_tag:
                citation.add_tag(self.default_tag.handle)
            self.db.add_citation(citation, self.trans)
            self.citation_count += 1
        else:
            if source is not None:
                new, source_obj = self.get_or_create_source(source)
                citation.set_reference_handle(source_obj.get_handle())
        if citation_ref is not None:
            self.storeup("citation", citation_ref, citation)
        if page is not None:
            citation.set_page(page)
        if date is not None:
            citation.set_date_object(_dp.parse(date))
        if confidence is not None:
            citation.set_confidence_level(
                self._parse_confidence(confidence, line_number)
            )
        if note is not None:
            resolved_note_type = (
                self._resolve_type(NoteType, self.note_types, note_type)
                if note_type is not None
                else NoteType(NoteType.CITATION)
            )
            self.add_note(resolved_note_type, citation, note)
        if tag is not None:
            self.add_tag(citation, tag)
        if media is not None:
            new, media_obj = self.get_or_create_media(
                media, media_description, media_date
            )
            media_ref = MediaRef()
            media_ref.set_reference_handle(media_obj.get_handle())
            citation.add_media_reference(media_ref)
        self.db.commit_citation(citation, self.trans)
        for ref_val, lookup_type in [
            (person_ref, "person"),
            (family_ref, "family"),
            (event_ref, "event"),
        ]:
            if ref_val is not None:
                obj = self.lookup(lookup_type, ref_val)
                if obj is None:
                    LOG.warning(
                        "%s ref '%s' not found on line %d"
                        % (lookup_type, ref_val, line_number)
                    )
                else:
                    obj.add_citation(citation.get_handle())
                    if lookup_type == "person":
                        self.db.commit_person(obj, self.trans)
                    elif lookup_type == "family":
                        self.db.commit_family(obj, self.trans)
                    elif lookup_type == "event":
                        self.db.commit_event(obj, self.trans)
        if place_ref is not None:
            place = self.lookup("place", place_ref)
            if place is None:
                LOG.warning(
                    "place ref '%s' not found on line %d" % (place_ref, line_number)
                )
            else:
                place.add_citation(citation.get_handle())
                self.db.commit_place(place, self.trans)

    def get_or_create_media(self, path, description=None, media_date=None):
        """Return the requested media object tuple-packed with a new indicator."""
        for handle in self.db.get_media_handles(sort_handles=False):
            media_obj = self.db.get_media_from_handle(handle)
            if media_obj.get_path() == path:
                return (0, media_obj)
        media_obj = Media()
        media_obj.set_path(path)
        media_obj.set_description(
            description if description else os.path.basename(path)
        )
        if media_date is not None:
            media_obj.set_date_object(_dp.parse(media_date))
        mime = mimetypes.guess_type(path)[0]
        if mime:
            media_obj.set_mime_type(mime)
        if self.default_tag:
            media_obj.add_tag(self.default_tag.handle)
        self.db.add_media(media_obj, self.trans)
        return (1, media_obj)

    def get_place_type(self, place_type_str):
        if place_type_str in self.place_types:
            return PlaceType((self.place_types[place_type_str], place_type_str))
        else:
            # New custom type:
            return PlaceType((0, place_type_str))

    def get_or_create_family(self, family_ref, husband, wife):
        "Return the family object for the give family ID."
        # if a gramps_id and exists:
        LOG.debug("get_or_create_family")
        if family_ref.startswith("[") and family_ref.endswith("]"):
            id_ = self.db.fid2user_format(family_ref[1:-1])
            family = self.db.get_family_from_gramps_id(id_)
            if family:
                # don't delete, only add
                fam_husband_handle = family.get_father_handle()
                fam_wife_handle = family.get_mother_handle()
                if husband:
                    if husband.get_handle() != fam_husband_handle:
                        # this husband is not the same old one! Add him!
                        family.set_father_handle(husband.get_handle())
                if wife:
                    if wife.get_handle() != fam_wife_handle:
                        # this wife is not the same old one! Add her!
                        family.set_mother_handle(wife.get_handle())
                LOG.debug("   returning existing family")
                return family
        # if not, create one:
        family = Family()
        # was marked with a gramps_id, but didn't exist, so we'll use it:
        if family_ref.startswith("[") and family_ref.endswith("]"):
            id_ = self.db.fid2user_format(family_ref[1:-1])
            family.set_gramps_id(id_)
        # add it:
        family.set_handle(create_id())
        if self.default_tag:
            family.add_tag(self.default_tag.handle)
        if husband:
            family.set_father_handle(husband.get_handle())
            husband.add_family_handle(family.get_handle())
        if wife:
            family.set_mother_handle(wife.get_handle())
            wife.add_family_handle(family.get_handle())
        if husband and wife:
            family.set_relationship(FamilyRelType.MARRIED)
        self.db.add_family(family, self.trans)
        if husband:
            self.db.commit_person(husband, self.trans)
        if wife:
            self.db.commit_person(wife, self.trans)
        self.fam_count += 1
        return family

    def get_or_create_event(
        self,
        object_,
        type_,
        date=None,
        place=None,
        source=None,
        descr=None,
        create_only=False,
    ):
        # first, see if it exists
        LOG.debug("get_or_create_event")
        ref_list = object_.get_event_ref_list()
        LOG.debug("refs: %s", ref_list)
        # look for a match, and possible correction
        # except if create_only is true (for events that
        # can have several occurrences like occupations, residences)
        if not create_only:
            for ref in ref_list:
                event = self.db.get_event_from_handle(ref.ref)
                LOG.debug(
                    "   compare event type %s == %s", int(event.get_type()), type_
                )
                if int(event.get_type()) == type_:
                    # Match! Let's update
                    if date:
                        event.set_date_object(date)
                    if place:
                        event.set_place_handle(place.get_handle())
                    if source:
                        self.find_and_set_citation(event, source)
                    if descr:
                        event.set_description(descr)
                    self.db.commit_event(event, self.trans)
                    LOG.debug("   returning existing event")
                    return (0, event)
        # else create it:
        LOG.debug("   creating event")
        event = Event()
        if type_:
            event.set_type(EventType(type_))
        if date:
            event.set_date_object(date)
        if place:
            event.set_place_handle(place.get_handle())
        if source:
            self.find_and_set_citation(event, source)
        if descr:
            event.set_description(descr)
        if self.default_tag:
            event.add_tag(self.default_tag.handle)
        self.db.add_event(event, self.trans)
        return (1, event)

    def get_or_create_attribute(self, object_, type_, value_, source=None):
        "Replaces existing attribute or create it"
        LOG.debug("get_or_create_attribute")
        attr_list = object_.get_attribute_list()
        LOG.debug("refs: %s", attr_list)
        # remove attributes if it already exists
        if type_ is None:
            type_ = "UNKNOWN"
        for attr in attr_list:
            if attr.get_type() == type_:
                object_.remove_attribute(attr)
        # then add it
        LOG.debug("adding attribute")
        attr = Attribute()
        attr.set_type(type_)
        attr.set_value(value_)
        if source is not None:
            new, source = self.get_or_create_source(source)
            self.find_and_set_citation(attr, source)
        object_.add_attribute(attr)
        return (1, attr)

    def create_person(self, gramps_id: str | None = None):
        """Used to create a new person we know doesn't exist"""
        person = Person()
        if gramps_id is not None:
            person.set_gramps_id(gramps_id)
        if self.default_tag:
            person.add_tag(self.default_tag.handle)
        self.db.add_person(person, self.trans)
        self.indi_count += 1
        return person

    def create_place(self, gramps_id: str | None = None):
        """Used to create a new place we know doesn't exist"""
        place = Place()
        if gramps_id is not None:
            place.set_gramps_id(gramps_id)
        if self.default_tag:
            place.add_tag(self.default_tag.handle)
        self.db.add_place(place, self.trans)
        self.place_count += 1
        return place

    def get_or_create_place(self, place_name):
        "Return the requested place object tuple-packed with a new indicator."
        if place_name.startswith("[") and place_name.endswith("]"):
            place = self.lookup("place", place_name)
            return (0, place)
        LOG.debug("get_or_create_place: looking for: %s", place_name)
        for place_handle in self.db.iter_place_handles():
            place = self.db.get_place_from_handle(place_handle)
            place_title = place_displayer.display(self.db, place)
            if place_title == place_name:
                return (0, place)
        place = Place()
        place.set_title(place_name)
        place.name = PlaceName(value=place_name)
        self.db.add_place(place, self.trans)
        self.place_count += 1
        return (1, place)

    def get_or_create_source(self, source_text):
        "Return the requested source object tuple-packed with a new indicator."
        source_list = self.db.get_source_handles(sort_handles=False)
        LOG.debug("get_or_create_source: list: %s", source_list)
        LOG.debug("get_or_create_source: looking for: %s", source_text)
        for source_handle in source_list:
            source = self.db.get_source_from_handle(source_handle)
            if source.get_title() == source_text:
                LOG.debug("   returning existing source")
                return (0, source)
        LOG.debug("   creating source")
        source = Source()
        source.set_title(source_text)
        self.db.add_source(source, self.trans)
        return (1, source)

    def find_and_set_citation(self, obj, source):
        # look for the source in the existing citations for the object
        LOG.debug(
            "find_and_set_citation: looking for source: %s", source.get_gramps_id()
        )
        for citation_handle in obj.get_citation_list():
            citation = self.db.get_citation_from_handle(citation_handle)
            LOG.debug(
                "find_and_set_citation: existing citation: %s", citation.get_gramps_id()
            )
            poss_source = self.db.get_source_from_handle(
                citation.get_reference_handle()
            )
            LOG.debug(
                "   compare source %s == %s",
                source.get_gramps_id(),
                poss_source.get_gramps_id(),
            )
            if poss_source.get_handle() == source.get_handle():
                # The source is already cited
                LOG.debug("   source already cited")
                return
        # we couldn't find an appropriate citation, so we have to create one.
        citation = Citation()
        LOG.debug("   creating citation")
        citation.set_reference_handle(source.get_handle())
        self.db.add_citation(citation, self.trans)
        LOG.debug(
            "   created citation, citation %s %s" % (citation, citation.get_gramps_id())
        )
        obj.add_citation(citation.get_handle())

    def add_tag(self, obj, name):
        """
        Add a tag to an obj and database if it doesn't have it already
        """
        tag = self.db.get_tag_from_name(name)
        if tag is None:
            tag = Tag()
            tag.set_name(name)
            self.db.add_tag(tag, self.trans)
        obj.add_tag(tag.handle)

    def add_note(self, note_type, obj, note):
        """
        Add a note to an object
        """
        previous_notes_list = obj.get_note_list()
        updated_note = False
        for note_handle in previous_notes_list:
            previous_note = self.db.get_note_from_handle(note_handle)
            if previous_note.type == note_type:
                previous_text = previous_note.get()
                if note not in previous_text:
                    note = previous_text + "\n" + note
                previous_note.set(note)
                self.db.commit_note(previous_note, self.trans)
                updated_note = True
                break
        if not updated_note:
            new_note = Note()
            new_note.handle = create_id()
            new_note.type.set(note_type)
            new_note.set(note)
            if self.default_tag:
                new_note.add_tag(self.default_tag.handle)
            self.db.add_note(new_note, self.trans)
            obj.add_note(new_note.handle)

        if note_type == NoteType.PERSON:
            self.db.commit_person(obj, self.trans)
        elif note_type == NoteType.EVENT:
            self.db.commit_event(obj, self.trans)
        elif note_type == NoteType.FAMILY:
            self.db.commit_family(obj, self.trans)
