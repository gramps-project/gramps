#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007  Douglas S. Blank
# Copyright (C) 2000-2007 Donald N. Allingham
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
from gettext import gettext as _
import csv
import string
import codecs
import cStringIO

#------------------------------------------------------------------------
#
# Set up logging
#
#------------------------------------------------------------------------
import logging
log = logging.getLogger(".ImportCSV")

#-------------------------------------------------------------------------
#
# GTK/GNOME Modules
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import Errors
import RelLib
import const
from QuestionDialog import ErrorDialog
from DateHandler import parser as _dp
from PluginUtils import register_import
from Utils import gender as gender_map
from htmlentitydefs import name2codepoint

#-------------------------------------------------------------------------
#
# Encoding support for CSV, from http://docs.python.org/lib/csv-examples.html
#
#-------------------------------------------------------------------------
class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, **kwds)
        self.stream = f
        self.encoder = codecs.getencoder(encoding)

    def writerow(self, row):
        self.writer.writerow([s.encode('utf-8') for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode('utf-8')
        # ... and reencode it into the target encoding
        data, length = self.encoder(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

    def close(self):
        self.stream.close()

#-------------------------------------------------------------------------
#
# Support and main functions
#
#-------------------------------------------------------------------------
def rd(line_number, row, col, key, default = None):
    """ Return Row data by column name """
    if key in col:
        if col[key] >= len(row):
            print "Error: invalid column reference on line", line_number
            return default
        retval = row[col[key]].strip()
        if retval == "":
            return default
        else:
            return retval
    else:
        return default

def cleanup_column_name(column):
    """ Handle column aliases """
    retval = string.lower(column)
    if retval == "lastname":
        retval = "surname"
    elif retval == "mother":
        retval = "wife"
    elif retval == "father":
        retval = "husband"
    elif retval == "parent1":
        retval = "husband"
    elif retval == "parent2":
        retval = "wife"
    return retval

def importData(db, filename, callback=None):
    g = CSVParser(db, filename, callback)
    g.process()

#-------------------------------------------------------------------------
#
# CSV Parser 
#
#-------------------------------------------------------------------------
class CSVParser:
    def __init__(self, db, filename, callback):
        self.db = db
        self.filename = filename
        self.callback = callback
        self.debug = 0

    def readCSV(self):
        fp = None
        reader = []
        try:
            fp = open(self.filename, "rb")
            reader = UnicodeReader(fp) 
        except IOError, msg:
            errmsg = _("%s could not be opened\n") % self.filename
            ErrorDialog(errmsg,str(msg))
            try:
                fp.close()
            except:
                pass
            return None
        data = []
        try:
            for row in reader:
                row = map(string.strip, row)
                data.append( row )
        except csv.Error, e:
            ErrorDialog(_('format error: file %s, line %d: %s') %
                        (self.filename, reader.line_num, e))
            try:
                fp.close()
            except:
                pass
            return None
        return data

    def lookup(self, type, id):
        if id == None: return None
        if type == "family":
            if id.startswith("[") and id.endswith("]"):
                id = id[1:-1]
                db_lookup = self.db.get_family_from_gramps_id(id)
                if db_lookup == None:
                    return self.lookup(type, id)
                else:
                    return db_lookup
            elif id.lower() in self.fref.keys():
                return self.fref[id.lower()]
            else:
                return None
        elif type == "person":
            if id.startswith("[") and id.endswith("]"):
                id = id[1:-1]
                db_lookup = self.db.get_person_from_gramps_id(id)
                if db_lookup == None:
                    return self.lookup(type, id)
                else:
                    return db_lookup
            elif id.lower() in self.pref.keys():
                return self.pref[id.lower()]
            else:
                return None
        else:
            print "error: invalid lookup type in CSV import: '%s'" % type
            return None

    def storeup(self, type, id, object):
        if id.startswith("[") and id.endswith("]"):
            id = id[1:-1]
            #return # do not store gramps people; go look them up
        if type == "person":
            self.pref[id.lower()] = object
        elif type == "family":
            self.fref[id.lower()] = object
        else:
            print "error: invalid storeup type in CSV import: '%s'" % type

    def process(self):
        data = self.readCSV() 
        self.trans = self.db.transaction_begin("",batch=True)
        self.db.disable_signals()
        t = time.time()
        self.lineno = 0
        self.index = 0
        self.fam_count = 0
        self.indi_count = 0
        self.pref  = {} # person ref, internal to this sheet
        self.fref  = {} # family ref, internal to this sheet
        
        header = None
        line_number = 0
        for row in data:
            line_number += 1
            if "".join(row) == "": # no blanks are allowed inside a table
                header = None # clear headers, ready for next "table"
                continue
            ######################################
            if header == None:
                header = map(cleanup_column_name, row)
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
                # marriage, husband, wife
                marriage_ref   = rd(line_number, row, col, "marriage")
                husband  = rd(line_number, row, col, "husband")
                wife     = rd(line_number, row, col, "wife")
                marriagedate = rd(line_number, row, col, "date")
                marriageplace = rd(line_number, row, col, "place")
                marriagesource = rd(line_number, row, col, "source")
                note = rd(line_number, row, col, "note")
                wife = self.lookup("person", wife)
                husband = self.lookup("person", husband)
                if husband == None and wife == None:
                    # might have children, so go ahead and add
                    print "Warning: no parents on line %d; adding family anyway" % line_number
                family = self.get_or_create_family(marriage_ref, husband, wife)
                # adjust gender, if not already provided
                if husband:
                    # this is just a guess, if unknown
                    if husband.get_gender() == RelLib.Person.UNKNOWN:
                        husband.set_gender(RelLib.Person.MALE)
                        self.db.commit_person(husband, self.trans)
                if wife:
                    # this is just a guess, if unknown
                    if wife.get_gender() == RelLib.Person.UNKNOWN:
                        wife.set_gender(RelLib.Person.FEMALE)
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
                if marriagedate or marriageplace or marriagesource:
                    # add, if new; replace, if different
                    new, marriage = self.get_or_create_event(family, RelLib.EventType.MARRIAGE, marriagedate, marriageplace, marriagesource)
                    if new:
                        mar_ref = RelLib.EventRef()
                        mar_ref.set_reference_handle(marriage.get_handle())
                        family.add_event_ref(mar_ref)
                        self.db.commit_family(family, self.trans)
                    # only add note to event:
                    if note:
                        # append notes, if previous notes
                        previous_notes = marriage.get_note()
                        if previous_notes != "":
                            if note not in previous_notes:
                                note = previous_notes + "\n" + note
                        marriage.set_note(note)
                        self.db.commit_event(marriage, self.trans)
            elif "family" in header:
                # family, child
                family_ref   = rd(line_number, row, col, "family")
                if family_ref == None:
                    print "Error: no family reference found for family on line %d" % line_number
                    continue # required
                child   = rd(line_number, row, col, "child")
                source  = rd(line_number, row, col, "source")
                note  = rd(line_number, row, col, "note")
                gender  = rd(line_number, row, col, "gender")
                child = self.lookup("person", child)
                family = self.lookup("family", family_ref)
                if family == None:
                    print "Error: no matching family reference found for family on line %d" % line_number
                    continue
                if child == None:
                    print "Error: no matching child reference found for family on line %d" % line_number
                    continue
                # is this child already in this family? If so, don't add
                if self.debug: print "children:", [ref.ref for ref in family.get_child_ref_list()]
                if self.debug: print "looking for:", child.get_handle()
                if child.get_handle() not in [ref.ref for ref in family.get_child_ref_list()]:
                    # add child to family
                    if self.debug: print "   adding child to family", child.get_gramps_id(), family.get_gramps_id()
                    childref = RelLib.ChildRef()
                    childref.set_reference_handle(child.get_handle())
                    family.add_child_ref( childref)
                    self.db.commit_family(family, self.trans)
                    child.add_parent_family_handle(family.get_handle())
                if gender:
                    # replace
                    gender = gender.lower()
                    if gender == gender_map[RelLib.Person.MALE]:
                        gender = RelLib.Person.MALE
                    elif gender == gender_map[RelLib.Person.FEMALE]:
                        gender = RelLib.Person.FEMALE
                    else:
                        gender = RelLib.Person.UNKNOWN
                    child.set_gender(gender)
                if source:
                    # add, if new
                    new, source = self.get_or_create_source(source)
                    source_refs = child.get_source_references()
                    found = 0
                    for ref in source_refs:
                        if self.debug: print "child: looking for ref:", ref.ref, source.get_handle()
                        if ref.ref == source.get_handle():
                            found = 1
                    if not found:
                        sref = RelLib.SourceRef()
                        sref.set_reference_handle(source.get_handle())
                        child.add_source_reference(sref)
                # put note on child
                if note:
                    # append notes, if previous notes
                    previous_notes = child.get_note()
                    if self.debug: print " previous note:", previous_notes
                    if previous_notes != "":
                        if note not in previous_notes:
                            note = previous_notes + "\n" + note
                    child.set_note(note)
                self.db.commit_person(child, self.trans)
            elif "surname" in header:              # person data
                # surname, and any of the following
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
                deathplace  = rd(line_number, row, col, "deathplace")
                deathdate   = rd(line_number, row, col, "deathdate")
                deathsource = rd(line_number, row, col, "deathsource")
                deathcause  = rd(line_number, row, col, "deathcause")
                grampsid    = rd(line_number, row, col, "grampsid")
                person_ref  = rd(line_number, row, col, "person")
                #########################################################
                # if this person already exists, don't create them
                person = self.lookup("person", person_ref)
                if person == None:
                    if surname == None and firstname == "":
                        print "Error: need both firstname and surname for new person on line %d" % line_number
                        continue # need a name if it is a new person
                    # new person
                    person = self.create_person(firstname, surname)
                    name = RelLib.Name()
                    name.set_type( RelLib.NameType(RelLib.NameType.BIRTH))
                    name.set_first_name(firstname)
                    name.set_surname(surname)
                    person.set_primary_name(name)
                else:
                    name = person.get_primary_name()
                #########################################################
                if person_ref != None:
                    self.storeup("person", person_ref, person)
                # replace
                if callname != None:
                    name.set_call_name(callname)
                if title != None:
                    name.set_title(title)
                if prefix != None:
                    name.prefix   = prefix
                    name.group_as = '' # HELP? what should I do here?
                if suffix != None:
                    name.set_suffix(suffix)
                if note != None:
                    # append notes, if previous notes
                    previous_notes = person.get_note()
                    if previous_notes != "":
                        if note not in previous_notes:
                            note = previous_notes + "\n" + note
                    person.set_note(note)
                if grampsid != None:
                    person.gramps_id = grampsid
                elif person_ref != None:
                    if person_ref.startswith("[") and person_ref.endswith("]"):
                        person.gramps_id = person_ref[1:-1]
                if person.get_gender() == RelLib.Person.UNKNOWN and gender != None:
                    gender = gender.lower()
                    if gender == gender_map[RelLib.Person.MALE]:
                        gender = RelLib.Person.MALE
                    elif gender == gender_map[RelLib.Person.FEMALE]:
                        gender = RelLib.Person.FEMALE
                    else:
                        gender = RelLib.Person.UNKNOWN
                    person.set_gender(gender)
                #########################################################
                # add if new, replace if different
                if birthdate != None:
                    birthdate = _dp.parse(birthdate)
                if birthplace != None:
                    new, birthplace = self.get_or_create_place(birthplace)
                if birthsource != None:
                    new, birthsource = self.get_or_create_source(birthsource)
                if birthdate or birthplace or birthsource:
                    new, birth = self.get_or_create_event(person, RelLib.EventType.BIRTH, birthdate, birthplace, birthsource)
                    birth_ref = person.get_birth_ref()
                    if birth_ref == None:
                        # new
                        birth_ref = RelLib.EventRef()
                    birth_ref.set_reference_handle( birth.get_handle())
                    person.set_birth_ref( birth_ref)
                if deathdate != None:
                    deathdate = _dp.parse(deathdate)
                if deathplace != None:
                    new, deathplace = self.get_or_create_place(deathplace)
                if deathsource != None:
                    new, deathsource = self.get_or_create_source(deathsource)
                if deathdate or deathplace or deathsource or deathcause:
                    new, death = self.get_or_create_event(person, RelLib.EventType.DEATH, deathdate, deathplace, deathsource)
                    if deathcause:
                        death.set_description(deathcause)
                        self.db.commit_event(death, self.trans)
                    death_ref = person.get_death_ref()
                    if death_ref == None:
                        # new
                        death_ref = RelLib.EventRef()
                    death_ref.set_reference_handle(death.get_handle())
                    person.set_death_ref(death_ref)
                if source:
                    # add, if new
                    new, source = self.get_or_create_source(source)
                    source_refs = person.get_source_references()
                    found = 0
                    for ref in source_refs:
                        if self.debug: print "person: looking for ref:", ref.ref, source.get_handle()
                        if ref.ref == source.get_handle():
                            found = 1
                    if not found:
                        sref = RelLib.SourceRef()
                        sref.set_reference_handle(source.get_handle())
                        person.add_source_reference(sref)
                self.db.commit_person(person, self.trans)
            else:
                print "Warning: ignoring line %d" % line_number
        t = time.time() - t
        msg = _('Import Complete: %d seconds') % t
        self.db.transaction_commit(self.trans,_("CSV import"))
        self.db.enable_signals()
        self.db.request_rebuild()
        print msg
        print "New Families: %d" % self.fam_count
        print "New Individuals: %d" % self.indi_count
        return None

    def get_or_create_family(self, family_ref, husband, wife):
        # if a gramps_id and exists:
        if self.debug: print "get_or_create_family"
        if family_ref.startswith("[") and family_ref.endswith("]"):
            family = self.db.get_family_from_gramps_id(family_ref[1:-1])
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
                        family.set_wife_handle(wife.get_handle())
                if self.debug: print "   returning existing family"
                return family
        # if not, create one:
        family = RelLib.Family()
        # was marked with a gramps_id, but didn't exist, so we'll use it:
        if family_ref.startswith("[") and family_ref.endswith("]"):
            family.set_gramps_id(family_ref[1:-1])
        # add it:
        self.db.add_family(family, self.trans)
        if husband:
            family.set_father_handle(husband.get_handle())
            husband.add_family_handle(family.get_handle())
        if wife:
            family.set_mother_handle(wife.get_handle())
            wife.add_family_handle(family.get_handle())
        self.db.commit_family(family,self.trans)
        if husband:
            self.db.commit_person(husband, self.trans)
        if wife:
            self.db.commit_person(wife, self.trans)
        self.fam_count += 1
        return family
        
    def get_or_create_event(self, object, type, date=None, place=None, source=None):
        """ Add or find a type event on object """
        # first, see if it exists
        if self.debug: print "get_or_create_event"
        ref_list = object.get_event_ref_list()
        if self.debug: print "refs:", ref_list
        # look for a match, and possible correction
        for ref in ref_list:
            event = self.db.get_event_from_handle(ref.ref)
            if self.debug: print "   compare event type", int(event.get_type()), type
            if int(event.get_type()) == type:
                # Match! Let's update
                if date:
                    event.set_date_object(date)
                if place:
                    event.set_place_handle(place.get_handle())
                if source:
                    source_refs = event.get_source_references()
                    found = 0
                    for ref in source_refs:
                        if self.debug: print "get_or_create_event: looking for ref:", ref.ref, source.get_handle()
                        if ref.ref == source.get_handle():
                            found = 1
                    if not found:
                        sref = RelLib.SourceRef()
                        sref.set_reference_handle(source.get_handle())
                        event.add_source_reference(sref)
                self.db.commit_event(event,self.trans)
                if self.debug: print "   returning existing event"
                return (0, event)
        # else create it:
        if self.debug: print "   creating event"
        event = RelLib.Event()
        if type:
            event.set_type(RelLib.EventType(type))
        if date:
            event.set_date_object(date)
        if place:
            event.set_place_handle(place.get_handle())
        if source:
            source_refs = event.get_source_references()
            found = 0
            for ref in source_refs:
                if self.debug: print "looking for ref:", ref.ref, source.get_handle()
                if ref.ref == source.get_handle():
                    found = 1
            if not found:
                sref = RelLib.SourceRef()
                sref.set_reference_handle(source.get_handle())
                event.add_source_reference(sref)
        self.db.add_event(event,self.trans)
        self.db.commit_event(event,self.trans)
        return (1, event)
    
    def create_person(self,firstname,lastname):
        """ Used to create a new person we know doesn't exist """
        person = RelLib.Person()
        mykey = firstname+lastname
        self.db.add_person(person,self.trans)
        self.db.commit_person(person,self.trans)
        self.indi_count += 1
        return person

    def get_or_create_place(self,place_name):
        place_list = self.db.get_place_handles()
        if self.debug: print "get_or_create_place: list:", place_list
        if self.debug: print "get_or_create_place: looking for:", place_name
        for place_handle in place_list:
            place = self.db.get_place_from_handle(place_handle)
            if place.get_title() == place_name:
                return (0, place)
        place = RelLib.Place()
        place.set_title(place_name)
        self.db.add_place(place,self.trans)
        self.db.commit_place(place,self.trans)
        return (1, place)

    def get_or_create_source(self, source_text):
        source_list = self.db.get_source_handles()
        if self.debug: print "get_or_create_source: list:", source_list
        if self.debug: print "get_or_create_source: looking for:", source_text
        for source_handle in source_list:
            source = self.db.get_source_from_handle(source_handle)
            if source.get_title() == source_text:
                return (0, source)
        source = RelLib.Source()
        source.set_title(source_text)
        self.db.add_source(source, self.trans)
        self.db.commit_source(source, self.trans)
        return (1, source)

#-------------------------------------------------------------------------
#
# Register the plugin
#
#-------------------------------------------------------------------------
_mime_type = "text/x-comma-separated-values" # CSV Document
_filter = gtk.FileFilter()
_filter.set_name(_('CSV spreadsheet files'))
_filter.add_mime_type(_mime_type)
_format_name = _('CSV Spreadheet')
register_import(importData,_filter,_mime_type,0,_format_name)
