#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
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
Package providing filtering framework for GRAMPS.
"""

#------------------------------------------------------------------------
#
# Gramps imports
#
#------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from ..lib.person import Person
from ..lib.family import Family
from ..lib.src import Source
from ..lib.citation import Citation
from ..lib.event import Event
from ..lib.place import Place
from ..lib.repo import Repository
from ..lib.mediaobj import MediaObject
from ..lib.note import Note
from ..lib.tag import Tag

#-------------------------------------------------------------------------
#
# GenericFilter
#
#-------------------------------------------------------------------------
class GenericFilter(object):
    """Filter class that consists of several rules."""
    
    logical_functions = ['or', 'and', 'xor', 'one']

    def __init__(self, source=None):
        if source:
            self.need_param = source.need_param
            self.flist = source.flist[:]
            self.name = source.name
            self.comment = source.comment
            self.logical_op = source.logical_op
            self.invert = source.invert
        else:
            self.need_param = 0
            self.flist = []
            self.name = ''
            self.comment = ''
            self.logical_op = 'and'
            self.invert = False

    def match(self, handle, db):
        """
        Return True or False depending on whether the handle matches the filter.
        """
        if self.apply(db, [handle]):
            return True
        else:
            return False

    def is_empty(self):
        return ((len(self.flist) == 0) or 
                (len(self.flist) == 1 and ((self.flist[0].is_empty() and 
                                            not self.invert))))

    def set_logical_op(self, val):
        if val in GenericFilter.logical_functions:
            self.logical_op = val
        else:
            self.logical_op = 'and'

    def get_logical_op(self):
        return self.logical_op

    def set_invert(self, val):
        self.invert = bool(val)

    def get_invert(self):
        return self.invert

    def get_name(self, ulocale=glocale):
        return self.name
    
    def set_name(self, name):
        self.name = name

    def set_comment(self, comment):
        self.comment = comment

    def get_comment(self):
        return self.comment
    
    def add_rule(self, rule):
        self.flist.append(rule)

    def delete_rule(self, rule):
        self.flist.remove(rule)

    def set_rules(self, rules):
        self.flist = rules

    def get_rules(self):
        return self.flist

    def get_cursor(self, db):
        return db.get_person_cursor()

    def make_obj(self):
        return Person()

    def find_from_handle(self, db, handle):
        return db.get_person_from_handle(handle)

    def check_func(self, db, id_list, task, cb_progress=None, tupleind=None):
        final_list = []
        
        if id_list is None:
            with self.get_cursor(db) as cursor:
                for handle, data in cursor:
                    person = self.make_obj()
                    person.unserialize(data)
                    if cb_progress:
                        cb_progress()
                    if task(db, person) != self.invert:
                        final_list.append(handle)
        else:
            for data in id_list:
                if tupleind is None:
                    handle = data
                else:
                    handle = data[tupleind]
                person = self.find_from_handle(db, handle)
                if cb_progress:
                    cb_progress()
                if task(db, person) != self.invert:
                    final_list.append(data)
        return final_list

    def check_and(self, db, id_list, cb_progress=None, tupleind=None):
        final_list = []
        flist = self.flist

        if id_list is None:
            with self.get_cursor(db) as cursor:
                for handle, data in cursor:
                    person = self.make_obj()
                    person.unserialize(data)
                    if cb_progress:
                        cb_progress()
                    val = all(rule.apply(db, person) for rule in flist)
                    if val != self.invert:
                        final_list.append(handle)
        else:
            for data in id_list:
                if tupleind is None:
                    handle = data
                else:
                    handle = data[tupleind]
                person = self.find_from_handle(db, handle)
                if cb_progress:
                    cb_progress()
                val = all(rule.apply(db, person) for rule in flist if person)
                if val != self.invert:
                    final_list.append(data)
        return final_list

    def check_or(self, db, id_list, cb_progress=None, tupleind=None):
        return self.check_func(db, id_list, self.or_test, cb_progress,
                                tupleind)

    def check_one(self, db, id_list, cb_progress=None, tupleind=None):
        return self.check_func(db, id_list, self.one_test, cb_progress,
                                tupleind)

    def check_xor(self, db, id_list, cb_progress=None, tupleind=None):
        return self.check_func(db, id_list, self.xor_test, cb_progress,
                                tupleind)

    def xor_test(self, db, person):
        test = False
        for rule in self.flist:
            test = test ^ rule.apply(db, person)
        return test

    def one_test(self, db, person):
        found_one = False
        for rule in self.flist:
            if rule.apply(db, person):
                if found_one:
                    return False    # There can be only one!
                found_one = True
        return found_one

    def or_test(self, db, person):
        return any(rule.apply(db, person) for rule in self.flist) 

    def get_check_func(self):
        try:
            m = getattr(self, 'check_' + self.logical_op)
        except AttributeError:
            m = self.check_and
        return m

    def check(self, db, handle):
        return self.get_check_func()(db, [handle])

    def apply(self, db, id_list=None, cb_progress=None, tupleind=None):
        """
        Apply the filter using db.
        If id_list given, the handles in id_list are used. If not given
        a database cursor will be used over all entries.

        cb_progress is optional. If present it must be a function that takes no 
        parameters. If cb_progress given, it will be called occasionally to 
        indicate progress of the filtering.
        
        If tupleind is given, id_list is supposed to consist of a list of 
        tuples, with the handle being index tupleind. So 
        handle_0 = id_list[0][tupleind]
        
        :Returns: if id_list given, it is returned with the items that 
                do not match the filter, filtered out.
                if id_list not given, all items in the database that 
                match the filter are returned as a list of handles
        """
        m = self.get_check_func()
        for rule in self.flist:
            rule.requestprepare(db)
        res = m(db, id_list, cb_progress, tupleind)
        for rule in self.flist:
            rule.requestreset()
        return res

class GenericFamilyFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_cursor(self, db):
        return db.get_family_cursor()

    def make_obj(self):
        return Family()

    def find_from_handle(self, db, handle):
        return db.get_family_from_handle(handle)

class GenericEventFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_cursor(self, db):
        return db.get_event_cursor()

    def make_obj(self):
        return Event()

    def find_from_handle(self, db, handle):
        return db.get_event_from_handle(handle)
   
class GenericSourceFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_cursor(self, db):
        return db.get_source_cursor()

    def make_obj(self):
        return Source()

    def find_from_handle(self, db, handle):
        return db.get_source_from_handle(handle)

class GenericCitationFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_cursor(self, db):
        return db.get_citation_cursor()

    def make_obj(self):
        return Citation()

    def find_from_handle(self, db, handle):
        return db.get_citation_from_handle(handle)

class GenericPlaceFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_cursor(self, db):
        return db.get_place_cursor()

    def make_obj(self):
        return Place()

    def find_from_handle(self, db, handle):
        return db.get_place_from_handle(handle)

class GenericMediaFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_cursor(self, db):
        return db.get_media_cursor()

    def make_obj(self):
        return MediaObject()

    def find_from_handle(self, db, handle):
        return db.get_object_from_handle(handle)

class GenericRepoFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_cursor(self, db):
        return db.get_repository_cursor()

    def make_obj(self):
        return Repository()

    def find_from_handle(self, db, handle):
        return db.get_repository_from_handle(handle)

class GenericNoteFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_cursor(self, db):
        return db.get_note_cursor()

    def make_obj(self):
        return Note()

    def find_from_handle(self, db, handle):
        return db.get_note_from_handle(handle)


def GenericFilterFactory(namespace):
    if namespace == 'Person':
        return GenericFilter
    elif namespace == 'Family':
        return GenericFamilyFilter
    elif namespace == 'Event':
        return GenericEventFilter
    elif namespace == 'Source':
        return GenericSourceFilter
    elif namespace == 'Citation':
        return GenericCitationFilter
    elif namespace == 'Place':
        return GenericPlaceFilter
    elif namespace == 'Media':
        return GenericMediaFilter
    elif namespace == 'Repository':
        return GenericRepoFilter
    elif namespace == 'Note':
        return GenericNoteFilter


class DeferredFilter(GenericFilter):
    """
    Filter class allowing for deferred translation of the filter name
    """

    def __init__(self, filter_name, person_name):
        GenericFilter.__init__(self, None)
        self.name_pair = [filter_name, person_name]

    def get_name(self, ulocale=glocale):
        """
        return the filter name, possibly translated

        If ulocale is passed in (a :class:`.GrampsLocale`) then
        the translated value will be returned instead.

        :param ulocale: allow deferred translation of strings
        :type ulocale: a :class:`.GrampsLocale` instance
        """
        self._ = ulocale.translation.gettext
        if self.name_pair[1]:
            return self._(self.name_pair[0]) % self.name_pair[1]
        return self._(self.name_pair[0])
