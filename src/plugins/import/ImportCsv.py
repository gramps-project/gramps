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
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id$

"Import from CSV Spreadsheet"

#-------------------------------------------------------------------------
#
# Standard Python Modules
#
#-------------------------------------------------------------------------
import time
import csv
import codecs

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
LOG = logging.getLogger(".ImportCSV")

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.ggettext import sgettext as _
from gen.ggettext import ngettext
import gen.lib
from gen.db import DbTxn
from gen.plug.utils import OpenFileOrStdin
from DateHandler import parser as _dp
from Utils import gender as gender_map
from Utils import create_id
from gui.utils import ProgressMeter
from gen.lib.eventroletype import EventRoleType

#-------------------------------------------------------------------------
#
# Support Functions
#
#-------------------------------------------------------------------------
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

#-------------------------------------------------------------------------
#
# Encoding support for CSV, from http://docs.python.org/lib/csv-examples.html
#
#-------------------------------------------------------------------------
class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, stream, encoding):
        self.reader = codecs.getreader(encoding)(stream)

    def __iter__(self):
        return self

    def next(self):
        "Encode the next line of the file."
        return self.reader.next().encode("utf-8")

class UnicodeReader(object):
    """
    A CSV reader which will iterate over lines in the CSV file,
    which is encoded in the given encoding.
    """

    def __init__(self, csvfile, encoding="utf-8", **kwds):
        self.first_row = True
        csvfile = UTF8Recoder(csvfile, encoding)
        self.reader = csv.reader(csvfile, **kwds)

    def next(self):
        "Read the next line of the file."
        row = self.reader.next()
        rowlist = [unicode(s, "utf-8") for s in row]
        # Add check for Byte Order Mark (Windows, Notepad probably):
        if self.first_row:
            if len(rowlist) > 0 and rowlist[0].startswith(u"\ufeff"):
                rowlist[0] = rowlist[0][1:]
            self.first_row = False
        return rowlist

    def __iter__(self):
        return self

#-------------------------------------------------------------------------
#
# Support and main functions
#
#-------------------------------------------------------------------------
def rd(line_number, row, col, key, default = None):
    """ Return Row data by column name """
    if key in col:
        if col[key] >= len(row):
            LOG.warn("missing '%s, on line %d" % (key, line_number))
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
    parser = CSVParser(dbase, user)
    try:
        with OpenFileOrStdin(filename, 'b') as filehandle:
            parser.parse(filehandle)
    except EnvironmentError, err:
        user.notify_error(_("%s could not be opened\n") % filename, str(err))
        return
    return None # This module doesn't provide info about what got imported.

#-------------------------------------------------------------------------
#
# CSV Parser 
#
#-------------------------------------------------------------------------
class CSVParser(object):
    """Class to read data in CSV format from a file object."""
    def __init__(self, dbase, user):
        self.db = dbase
        self.user = user
        self.trans = None
        self.lineno = 0
        self.index = 0
        self.fam_count = 0
        self.indi_count = 0
        self.pref  = {} # person ref, internal to this sheet
        self.fref  = {} # family ref, internal to this sheet        
        column2label = {
            "surname": ("Lastname", "Surname", _("Surname"), "lastname",
                "last_name", "surname", _("surname")),
            "firstname": ("Firstname", "Given name", _("Given name"), "Given",
                _("Given"), "firstname", "first_name", "given_name",
                "given name", _("given name"), "given", _("given")),
            "callname": ("Callname", "Call name", _("Call name"), "Call",
                _("Call"), "callname", "call_name", "call name", "call",
                _("call")),
            "title": ("Title", _("Person|Title"), "title", _("Person|title")),
            "prefix": ("Prefix", _("Prefix"), "prefix", _("prefix")),
            "suffix": ("Suffix", _("Suffix"), "suffix", _("suffix")),
            "gender": ("Gender", _("Gender"), "gender", _("gender")),
            "source": ("Source", _("Source"), "source", _("source")),
            "note": ("Note", _("Note"), "note", _("note")),
            "birthplace": ("Birthplace", "Birth place", _("Birth place"),
                "birthplace", "birth_place", "birth place", _("birth place")),
            "birthdate": ("Birthdate", "Birth date", _("Birth date"),
                "birthdate", "birth_date", "birth date", _("birth date")),
            "birthsource": ("Birthsource", "Birth source", _("Birth source"),
                "birthsource", "birth_source", "birth source",
                _("birth source")),
            "baptismplace": ("Baptismplace", "Baptism place",
                _("Baptism place"), "baptismplace", "baptism place",
                _("baptism place")),
            "baptismdate": ("Baptismdate", "Baptism date", _("Baptism date"),
                "baptismdate", "baptism date", _("baptism date")),
            "baptismsource": ("Baptismsource", "Baptism source",
                _("Baptism source"), "baptismsource", "baptism source",
                _("baptism source")),
            "burialplace": ("Burialplace", "Burial place", _("Burial place"),
                "burialplace", "burial place", _("burial place")),
            "burialdate": ("Burialdate", "Burial date", _("Burial date"),
                "burialdate", "burial date", _("burial date")),
            "burialsource": ("Burialsource", "Burial source",
                _("Burial source"), "burialsource", "burial source",
                _("burial source")),
            "deathplace": ("Deathplace", "Death place", _("Death place"),
                "deathplace", "death_place", "death place", _("death place")),
            "deathdate": ("Deathdate", "Death date", _("Death date"),
                "deathdate", "death_date", "death date", _("death date")),
            "deathsource": ("Deathsource", "Death source", _("Death source"),
                "deathsource", "death_source", "death source",
                _("death source")),
            "deathcause": ("Deathcause", "Death cause", _("Death cause"),
                "deathcause", "death_cause", "death cause", _("death cause")),
            "grampsid": ("Grampsid", "ID", "Gramps id", _("Gramps ID"),
                "grampsid", "id", "gramps_id", "gramps id", _("Gramps id")),
            "person": ("Person", _("Person"), "person", _("person")),
            # ----------------------------------
            "child": ("Child", _("Child"), "child", _("child")),
            "family": ("Family", _("Family"), "family", _("family")),
            # ----------------------------------
            "wife": ("Mother", _("Mother"), "Wife", _("Wife"), "Parent2",
                _("Parent2"), "mother", _("mother"), "wife", _("wife"),
                "parent2", _("parent2")),
            "husband": ("Father", _("Father"), "Husband", _("Husband"),
                "Parent1", _("Parent1"), "father", _("father"), "husband",
                _("husband"), "parent1", _("parent1")),
            "marriage": ("Marriage", _("Marriage"), "marriage", _("marriage")),
            "date": ("Date", _("Date"), "date", _("date")),
            "place": ("Place", _("Place"), "place", _("place")),
            }
        lab2col_dict = []
        for key in column2label.keys():
            for val in column2label[key]:
                lab2col_dict.append((val, key))
        self.label2column = dict(lab2col_dict)

    def cleanup_column_name(self, column):
        """Handle column aliases for CSV spreadsheet import and SQL."""
        return self.label2column.get(column, column)

    def read_csv(self, filehandle):
        "Read the data from the file and return it as a list."
        reader = UnicodeReader(filehandle)
        try:
            data = [[r.strip() for r in row] for row in reader]
        except csv.Error, err:
            ErrorDialog(_('format error: line %(line)d: %(zero)s') % {
                        'line' : reader.reader.line_num, 'zero' : err } )
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
            elif id_.lower() in self.fref:
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
            elif id_.lower() in self.pref:
                return self.pref[id_.lower()]
            else:
                return None
        else:
            LOG.warn("invalid lookup type in CSV import: '%s'" % type_)
            return None

    def storeup(self, type_, id_, object_):
        "Store object object_ of type type_ in a dictionary under key id_."
        if id_.startswith("[") and id_.endswith("]"):
            id_ = id_[1:-1]
            #return # do not store gramps people; go look them up
        if type_ == "person":
            id_ = self.db.id2user_format(id_)
            self.pref[id_.lower()] = object_
        elif type_ == "family":
            id_ = self.db.fid2user_format(id_)
            self.fref[id_.lower()] = object_
        else:
            LOG.warn("invalid storeup type in CSV import: '%s'" % type_)

    def parse(self, filehandle):
        """
        Prepare the database and parse the input file.

        :param filehandle: open file handle positioned at start of the file
        """
        data = self.read_csv(filehandle)
        progress = ProgressMeter(_('CSV Import'))
        progress.set_pass(_('Reading data...'), 1)
        progress.set_pass(_('Importing data...'), len(data))
        tym = time.time()
        self.db.disable_signals()
        with DbTxn(_("CSV import"), self.db, batch=True) as self.trans:
            self._parse_csv_data(data, progress)
        self.db.enable_signals()
        self.db.request_rebuild()
        tym = time.time() - tym
        msg = ngettext('Import Complete: %d second',
                'Import Complete: %d seconds', tym ) % tym
        LOG.debug(msg)
        LOG.debug("New Families: %d" % self.fam_count)
        LOG.debug("New Individuals: %d" % self.indi_count)
        progress.close()

    def _parse_csv_data(self, data, progress=None):
        """Parse each line of the input data and act accordingly."""
        self.lineno = 0
        self.index = 0
        self.fam_count = 0
        self.indi_count = 0
        self.pref  = {} # person ref, internal to this sheet
        self.fref  = {} # family ref, internal to this sheet        
        header = None
        line_number = 0
        for row in data:
            if progress is not None:
                progress.step()
            line_number += 1
            if "".join(row) == "": # no blanks are allowed inside a table
                header = None # clear headers, ready for next "table"
                continue
            ######################################
            if header is None:
                header = [self.cleanup_column_name(r) for r in row]
                col = {}
                count = 0
                for key in header:
                    col[key] = count
                    count += 1
                continue
            # three different kinds of data: person, family, and marriage
            if (("marriage" in header) or
                ("husband" in header) or
                ("wife" in header)):
                self._parse_marriage(line_number, row, col)
            elif "family" in header:
                self._parse_family(line_number, row, col)
            elif "surname" in header:
                self._parse_person(line_number, row, col)
            else:
                LOG.warn("ignoring line %d" % line_number)
        return None

    def _parse_marriage(self, line_number, row, col):
        "Parse the content of a Marriage,Husband,Wife line."
        marriage_ref   = rd(line_number, row, col, "marriage")
        husband  = rd(line_number, row, col, "husband")
        wife     = rd(line_number, row, col, "wife")
        marriagedate = rd(line_number, row, col, "date")
        marriageplace = rd(line_number, row, col, "place")
        marriagesource = rd(line_number, row, col, "source")
        note = rd(line_number, row, col, "note")
        wife = self.lookup("person", wife)
        husband = self.lookup("person", husband)
        if husband is None and wife is None:
            # might have children, so go ahead and add
            LOG.warn("no parents on line %d; adding family anyway" %
                     line_number)
        family = self.get_or_create_family(marriage_ref, husband, wife)
        # adjust gender, if not already provided
        if husband:
            # this is just a guess, if unknown
            if husband.get_gender() == gen.lib.Person.UNKNOWN:
                husband.set_gender(gen.lib.Person.MALE)
                self.db.commit_person(husband, self.trans)
        if wife:
            # this is just a guess, if unknown
            if wife.get_gender() == gen.lib.Person.UNKNOWN:
                wife.set_gender(gen.lib.Person.FEMALE)
                self.db.commit_person(wife, self.trans)
        if marriage_ref:
            self.storeup("family", marriage_ref.lower(), family)
        if marriagesource:
            # add, if new
            new, marriagesource = self.get_or_create_source(marriagesource)
        if marriageplace:
            # add, if new
            new, marriageplace = self.get_or_create_place(marriageplace)
        if marriagedate:
            marriagedate = _dp.parse(marriagedate)
        if marriagedate or marriageplace or marriagesource or note:
            # add, if new; replace, if different
            new, marriage = self.get_or_create_event(family,
                    gen.lib.EventType.MARRIAGE, marriagedate,
                    marriageplace, marriagesource)
            if new:
                mar_ref = gen.lib.EventRef()
                mar_ref.set_reference_handle(marriage.get_handle())
                family.add_event_ref(mar_ref)
                self.db.commit_family(family, self.trans)
            # only add note to event:
            # append notes, if previous notes
            if note:
                previous_notes_list = marriage.get_note_list()
                updated_note = False
                for note_handle in previous_notes_list:
                    previous_note = self.db.get_note_from_handle(
                            note_handle)
                    if previous_note.type == gen.lib.NoteType.EVENT:
                        previous_text = previous_note.get()
                        if note not in previous_text:
                            note = previous_text + "\n" + note
                        previous_note.set(note)
                        self.db.commit_note(previous_note, self.trans)
                        updated_note = True
                        break
                if not updated_note:
                    # add new note here
                    new_note = gen.lib.Note()
                    new_note.handle = create_id()
                    new_note.type.set(gen.lib.NoteType.EVENT)
                    new_note.set(note)
                    self.db.add_note(new_note, self.trans)
                    marriage.add_note(new_note.handle)
                self.db.commit_event(marriage, self.trans)

    def _parse_family(self, line_number, row, col):
        "Parse the content of a family line"
        family_ref   = rd(line_number, row, col, "family")
        if family_ref is None:
            LOG.warn("no family reference found for family on line %d" %
                     line_number)
            return # required
        child   = rd(line_number, row, col, "child")
        source  = rd(line_number, row, col, "source")
        note  = rd(line_number, row, col, "note")
        gender  = rd(line_number, row, col, "gender")
        child = self.lookup("person", child)
        family = self.lookup("family", family_ref)
        if family is None:
            LOG.warn("no matching family reference found for family "
                     "on line %d" % line_number)
            return
        if child is None:
            LOG.warn("no matching child reference found for family "
                     "on line %d" % line_number)
            return
        # is this child already in this family? If so, don't add
        LOG.debug("children: %s", [ref.ref for ref in
                                   family.get_child_ref_list()])
        LOG.debug("looking for: %s", child.get_handle())
        if child.get_handle() not in [ref.ref for ref in
                                      family.get_child_ref_list()]:
            # add child to family
            LOG.debug("   adding child [%s] to family [%s]",
                      child.get_gramps_id(), family.get_gramps_id())
            childref = gen.lib.ChildRef()
            childref.set_reference_handle(child.get_handle())
            family.add_child_ref( childref)
            self.db.commit_family(family, self.trans)
            child.add_parent_family_handle(family.get_handle())
        if gender:
            # replace
            gender = gender.lower()
            if gender == gender_map[gen.lib.Person.MALE].lower():
                gender = gen.lib.Person.MALE
            elif gender == gender_map[gen.lib.Person.FEMALE].lower():
                gender = gen.lib.Person.FEMALE
            else:
                gender = gen.lib.Person.UNKNOWN
            child.set_gender(gender)
        if source:
            # add, if new
            dummy_new, source = self.get_or_create_source(source)
            self.find_and_set_citation(child, source)
        # put note on child
        if note:
            # append notes, if previous notes
            previous_notes_list = child.get_note_list()
            updated_note = False
            for note_handle in previous_notes_list:
                previous_note = self.db.get_note_from_handle(note_handle)
                if previous_note.type == gen.lib.NoteType.PERSON:
                    previous_text = previous_note.get()
                    if note not in previous_text:
                        note = previous_text + "\n" + note
                    previous_note.set(note)
                    self.db.commit_note(previous_note, self.trans)
                    updated_note = True
                    break
            if not updated_note:
                # add new note here
                new_note = gen.lib.Note()
                new_note.handle = create_id()
                new_note.type.set(gen.lib.NoteType.PERSON)
                new_note.set(note)
                self.db.add_note(new_note, self.trans)
                child.add_note(new_note.handle)
        self.db.commit_person(child, self.trans)

    def _parse_person(self, line_number, row, col):
        "Parse the content of a Person line."
        surname   = rd(line_number, row, col, "surname")
        firstname = rd(line_number, row, col, "firstname", "")
        callname  = rd(line_number, row, col, "callname")
        title     = rd(line_number, row, col, "title")
        prefix    = rd(line_number, row, col, "prefix")
        suffix    = rd(line_number, row, col, "suffix")
        gender    = rd(line_number, row, col, "gender")
        source    = rd(line_number, row, col, "source")
        note      = rd(line_number, row, col, "note")
        birthplace  = rd(line_number, row, col, "birthplace")
        birthdate   = rd(line_number, row, col, "birthdate")
        birthsource = rd(line_number, row, col, "birthsource")
        baptismplace  = rd(line_number, row, col, "baptismplace")
        baptismdate   = rd(line_number, row, col, "baptismdate")
        baptismsource = rd(line_number, row, col, "baptismsource")
        burialplace  = rd(line_number, row, col, "burialplace")
        burialdate   = rd(line_number, row, col, "burialdate")
        burialsource = rd(line_number, row, col, "burialsource")
        deathplace  = rd(line_number, row, col, "deathplace")
        deathdate   = rd(line_number, row, col, "deathdate")
        deathsource = rd(line_number, row, col, "deathsource")
        deathcause  = rd(line_number, row, col, "deathcause")
        grampsid    = rd(line_number, row, col, "grampsid")
        person_ref  = rd(line_number, row, col, "person")
        #########################################################
        # if this person already exists, don't create them
        person = self.lookup("person", person_ref)
        if person is None:
            if surname is None:
                LOG.warn("empty surname for new person on line %d" %
                         line_number)
                surname = ""
            # new person
            person = self.create_person()
            name = gen.lib.Name()
            name.set_type(gen.lib.NameType(gen.lib.NameType.BIRTH))
            name.set_first_name(firstname)
            surname_obj = gen.lib.Surname()
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
        if title is not None:
            name.set_title(title)
        if prefix is not None:
            name.get_primary_surname().set_prefix(prefix)
            name.group_as = '' # HELP? what should I do here?
        if suffix is not None:
            name.set_suffix(suffix)
        if note is not None:
            # append notes, if previous notes
            previous_notes_list = person.get_note_list()
            updated_note = False
            for note_handle in previous_notes_list:
                previous_note = self.db.get_note_from_handle(note_handle)
                if previous_note.type == gen.lib.NoteType.PERSON:
                    previous_text = previous_note.get()
                    if note not in previous_text:
                        note = previous_text + "\n" + note
                    previous_note.set(note)
                    self.db.commit_note(previous_note, self.trans)
                    updated_note = True
                    break
            if not updated_note:
                # add new note here
                new_note = gen.lib.Note()
                new_note.handle = create_id()
                new_note.type.set(gen.lib.NoteType.PERSON)
                new_note.set(note)
                self.db.add_note(new_note, self.trans)
                person.add_note(new_note.handle)
        if grampsid is not None:
            person.gramps_id = grampsid
        elif person_ref is not None:
            if person_ref.startswith("[") and person_ref.endswith("]"):
                person.gramps_id = self.db.id2user_format(person_ref[1:-1])
        if (person.get_gender() == gen.lib.Person.UNKNOWN and
                gender is not None):
            gender = gender.lower()
            if gender == gender_map[gen.lib.Person.MALE].lower():
                gender = gen.lib.Person.MALE
            elif gender == gender_map[gen.lib.Person.FEMALE].lower():
                gender = gen.lib.Person.FEMALE
            else:
                gender = gen.lib.Person.UNKNOWN
            person.set_gender(gender)
        #########################################################
        # add if new, replace if different
        # Birth:
        if birthdate is not None:
            birthdate = _dp.parse(birthdate)
        if birthplace is not None:
            new, birthplace = self.get_or_create_place(birthplace)
        if birthsource is not None:
            new, birthsource = self.get_or_create_source(birthsource)
        if birthdate or birthplace or birthsource:
            new, birth = self.get_or_create_event(person, 
                 gen.lib.EventType.BIRTH, birthdate, 
                 birthplace, birthsource)
            birth_ref = person.get_birth_ref()
            if birth_ref is None:
                # new
                birth_ref = gen.lib.EventRef()
            birth_ref.set_reference_handle( birth.get_handle())
            person.set_birth_ref( birth_ref)
        # Baptism:
        if baptismdate is not None:
            baptismdate = _dp.parse(baptismdate)
        if baptismplace is not None:
            new, baptismplace = self.get_or_create_place(baptismplace)
        if baptismsource is not None:
            new, baptismsource = self.get_or_create_source(baptismsource)
        if baptismdate or baptismplace or baptismsource:
            new, baptism = self.get_or_create_event(person, 
                 gen.lib.EventType.BAPTISM, baptismdate, 
                 baptismplace, baptismsource)
            baptism_ref = get_primary_event_ref_from_type(self.db, person,
                                                          "Baptism")
            if baptism_ref is None:
                # new
                baptism_ref = gen.lib.EventRef()
            baptism_ref.set_reference_handle( baptism.get_handle())
            person.add_event_ref( baptism_ref)
        # Death:
        if deathdate is not None:
            deathdate = _dp.parse(deathdate)
        if deathplace is not None:
            new, deathplace = self.get_or_create_place(deathplace)
        if deathsource is not None:
            new, deathsource = self.get_or_create_source(deathsource)
        if deathdate or deathplace or deathsource or deathcause:
            new, death = self.get_or_create_event(person,
                    gen.lib.EventType.DEATH, deathdate, deathplace,
                    deathsource)
            if deathcause:
                death.set_description(deathcause)
                self.db.commit_event(death, self.trans)
            death_ref = person.get_death_ref()
            if death_ref is None:
                # new
                death_ref = gen.lib.EventRef()
            death_ref.set_reference_handle(death.get_handle())
            person.set_death_ref(death_ref)
        # Burial:
        if burialdate is not None:
            burialdate = _dp.parse(burialdate)
        if burialplace is not None:
            new, burialplace = self.get_or_create_place(burialplace)
        if burialsource is not None:
            new, burialsource = self.get_or_create_source(burialsource)
        if burialdate or burialplace or burialsource:
            new, burial = self.get_or_create_event(person, 
                 gen.lib.EventType.BURIAL, burialdate, 
                 burialplace, burialsource)
            burial_ref = get_primary_event_ref_from_type(self.db, person,
                                                         "Burial")
            if burial_ref is None:
                # new
                burial_ref = gen.lib.EventRef()
            burial_ref.set_reference_handle( burial.get_handle())
            person.add_event_ref( burial_ref)
        if source:
            # add, if new
            new, source = self.get_or_create_source(source)
            self.find_and_set_citation(person, source)
        self.db.commit_person(person, self.trans)

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
        family = gen.lib.Family()
        # was marked with a gramps_id, but didn't exist, so we'll use it:
        if family_ref.startswith("[") and family_ref.endswith("]"):
            id_ = self.db.fid2user_format(family_ref[1:-1])
            family.set_gramps_id(id_)
        # add it:
        family.set_handle(self.db.create_id())
        if husband:
            family.set_father_handle(husband.get_handle())
            husband.add_family_handle(family.get_handle())
        if wife:
            family.set_mother_handle(wife.get_handle())
            wife.add_family_handle(family.get_handle())
        if husband and wife:
            family.set_relationship(gen.lib.FamilyRelType.MARRIED)
        self.db.add_family(family, self.trans)
        if husband:
            self.db.commit_person(husband, self.trans)
        if wife:
            self.db.commit_person(wife, self.trans)
        self.fam_count += 1
        return family
        
    def get_or_create_event(self, object_, type_, date=None, place=None,
                            source=None):
        """ Add or find a type event on object """
        # first, see if it exists
        LOG.debug("get_or_create_event")
        ref_list = object_.get_event_ref_list()
        LOG.debug("refs: %s", ref_list)
        # look for a match, and possible correction
        for ref in ref_list:
            event = self.db.get_event_from_handle(ref.ref)
            LOG.debug("   compare event type %s == %s", int(event.get_type()),
                      type_)
            if int(event.get_type()) == type_:
                # Match! Let's update
                if date:
                    event.set_date_object(date)
                if place:
                    event.set_place_handle(place.get_handle())
                if source:
                    self.find_and_set_citation(event, source)
                self.db.commit_event(event, self.trans)
                LOG.debug("   returning existing event")
                return (0, event)
        # else create it:
        LOG.debug("   creating event")
        event = gen.lib.Event()
        if type_:
            event.set_type(gen.lib.EventType(type_))
        if date:
            event.set_date_object(date)
        if place:
            event.set_place_handle(place.get_handle())
        if source:
            self.find_and_set_citation(event, source)
        self.db.add_event(event, self.trans)
        return (1, event)
    
    def create_person(self):
        """ Used to create a new person we know doesn't exist """
        person = gen.lib.Person()
        self.db.add_person(person, self.trans)
        self.indi_count += 1
        return person

    def get_or_create_place(self, place_name):
        "Return the requested place object tuple-packed with a new indicator."
        LOG.debug("get_or_create_place: looking for: %s", place_name)
        for place_handle in self.db.iter_place_handles():
            place = self.db.get_place_from_handle(place_handle)
            if place.get_title() == place_name:
                return (0, place)
        place = gen.lib.Place()
        place.set_title(place_name)
        self.db.add_place(place, self.trans)
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
        source = gen.lib.Source()
        source.set_title(source_text)
        self.db.add_source(source, self.trans)
        return (1, source)

    def find_and_set_citation(self, obj, source):
        # look for the source in the existing citations for the object
        LOG.debug("find_and_set_citation: looking for source: %s",
                  source.get_gramps_id())
        for citation_handle in obj.get_citation_list():
            citation = self.db.get_citation_from_handle(citation_handle)
            LOG.debug("find_and_set_citation: existing citation: %s",
                      citation.get_gramps_id())
            poss_source = self.db.get_source_from_handle(
                                    citation.get_reference_handle())
            LOG.debug("   compare source %s == %s", source.get_gramps_id(),
                      poss_source.get_gramps_id())
            if poss_source.get_handle() == source.get_handle():
                # The source is already cited
                LOG.debug("   source already cited")
                return
        # we couldn't find an appropriate citation, so we have to create one.
        citation = gen.lib.Citation()
        LOG.debug("   creating citation")
        citation.set_reference_handle(source.get_handle())
        self.db.add_citation(citation, self.trans)
        LOG.debug("   created citation, citation %s %s" % 
                  (citation, citation.get_gramps_id()))
        obj.add_citation(citation.get_handle())
