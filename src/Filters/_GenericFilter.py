#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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

# $Id:_GenericFilter.py 9912 2008-01-22 09:17:46Z acraphae $

"""
Package providing filtering framework for GRAMPS.
"""
from __future__ import with_statement
import gen.lib
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
        return len(self.flist) == 0 or \
              (len(self.flist) == 1 and self.flist[0].is_empty())

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

    def get_name(self):
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
        return gen.lib.Person()

    def find_from_handle(self, db, handle):
        return db.get_person_from_handle(handle)

    def check_func(self, db, id_list, task, progress=None, tupleind=None):
        final_list = []
        
        if id_list is None:
            with self.get_cursor(db) as cursor:
                for handle, data in cursor:
                    person = self.make_obj()
                    person.unserialize(data)
                    if progress:
                        progress.step()
                    if task(db, person) != self.invert:
                        final_list.append(handle)
        else:
            for data in id_list:
                if tupleind is None:
                    handle = data
                else:
                    handle = data[tupleind]
                person = self.find_from_handle(db, handle)
                if progress:
                    progress.step()
                if task(db, person) != self.invert:
                    final_list.append(data)
        return final_list

    def check_and(self, db, id_list, progress=None, tupleind=None):
        final_list = []
        flist = self.flist

        if id_list is None:
            with self.get_cursor(db) as cursor:
                for handle, data in cursor:
                    person = self.make_obj()
                    person.unserialize(data)
                    if progress:
                        progress.step()
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
                if progress:
                    progress.step()
                val = all(rule.apply(db, person) for rule in flist if person)
                if val != self.invert:
                    final_list.append(data)
        return final_list

    def check_or(self, db, id_list, progress=None, tupleind=None):
        return self.check_func(db, id_list, self.or_test, progress,
                                tupleind)

    def check_one(self, db, id_list, progress=None, tupleind=None):
        return self.check_func(db, id_list, self.one_test, progress,
                                tupleind)

    def check_xor(self, db, id_list, progress=None, tupleind=None):
        return self.check_func(db, id_list, self.xor_test, progress,
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

    # progress is optional. If present it must be an instance of 
    #  gui.utils.ProgressMeter
    def apply(self, db, id_list=None, progress=None, tupleind=None):
        """
        Apply the filter using db.
        If id_list given, the handles in id_list are used. If not given
        a database cursor will be used over all entries.
        
        If progress given, it will be used to indicate progress of the
        Filtering
        
        If typleind is given, id_list is supposed to consist of a list of 
        tuples, with the handle being index tupleind. So 
        handle_0 = id_list[0][tupleind]
        
        :Returns: if id_list given, it is returned with the items that 
                do not match the filter, filtered out.
                if id_list not given, all items in the database that 
                match the filter are returned as a list of handles
        """
        m = self.get_check_func()
        for rule in self.flist:
            rule.prepare(db)
        res = m(db, id_list, progress, tupleind)
        for rule in self.flist:
            rule.reset()
        return res

class GenericFamilyFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_cursor(self, db):
        return db.get_family_cursor()

    def make_obj(self):
        return gen.lib.Family()

    def find_from_handle(self, db, handle):
        return db.get_family_from_handle(handle)

class GenericEventFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_cursor(self, db):
        return db.get_event_cursor()

    def make_obj(self):
        return gen.lib.Event()

    def find_from_handle(self, db, handle):
        return db.get_event_from_handle(handle)
   
class GenericSourceFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_cursor(self, db):
        return db.get_source_cursor()

    def make_obj(self):
        return gen.lib.Source()

    def find_from_handle(self, db, handle):
        return db.get_source_from_handle(handle)

class GenericPlaceFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_cursor(self, db):
        return db.get_place_cursor()

    def make_obj(self):
        return gen.lib.Place()

    def find_from_handle(self, db, handle):
        return db.get_place_from_handle(handle)

class GenericMediaFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_cursor(self, db):
        return db.get_media_cursor()

    def make_obj(self):
        return gen.lib.MediaObject()

    def find_from_handle(self, db, handle):
        return db.get_object_from_handle(handle)

class GenericRepoFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_cursor(self, db):
        return db.get_repository_cursor()

    def make_obj(self):
        return gen.lib.Repository()

    def find_from_handle(self, db, handle):
        return db.get_repository_from_handle(handle)

class GenericNoteFilter(GenericFilter):

    def __init__(self, source=None):
        GenericFilter.__init__(self, source)

    def get_cursor(self, db):
        return db.get_note_cursor()

    def make_obj(self):
        return gen.lib.Note()

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
    elif namespace == 'Place':
        return GenericPlaceFilter
    elif namespace == 'MediaObject':
        return GenericMediaFilter
    elif namespace == 'Repository':
        return GenericRepoFilter
    elif namespace == 'Note':
        return GenericNoteFilter
