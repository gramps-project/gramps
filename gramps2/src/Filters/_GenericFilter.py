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

# $Id$

"""
Package providing filtering framework for GRAMPS.
"""

#-------------------------------------------------------------------------
#
# GenericFilter
#
#-------------------------------------------------------------------------
class GenericFilter:
    """Filter class that consists of several rules"""
    
    logical_functions = ['or', 'and', 'xor', 'one']

    def __init__(self,source=None):
        if source:
            self.need_param = source.need_param
            self.flist = source.flist[:]
            self.name = source.name
            self.comment = source.comment
            self.logical_op = source.logical_op
        else:
            self.need_param = 0
            self.flist = []
            self.name = ''
            self.comment = ''
            self.logical_op = 'and'

    def match(self,handle):
        return True

    def is_empty(self):
        return len(self.flist) == 1 and self.flist[0].is_empty()

    def set_logical_op(self,val):
        if val in GenericFilter.logical_functions:
            self.logical_op = val
        else:
            self.logical_op = 'and'

    def get_logical_op(self):
        return self.logical_op

    def get_name(self):
        return self.name
    
    def set_name(self,name):
        self.name = name

    def set_comment(self,comment):
        self.comment = comment

    def get_comment(self):
        return self.comment
    
    def add_rule(self,rule):
        self.flist.append(rule)

    def delete_rule(self,rule):
        self.flist.remove(rule)

    def set_rules(self,rules):
        self.flist = rules

    def get_rules(self):
        return self.flist

    def check_func(self,db,id_list,task):
        final_list = []
        
        if id_list == None:
            cursor = db.get_person_cursor()
            data = cursor.next()
            while data:
                person = RelLib.Person()
                person.unserialize(data[1])
                if not task(db,person):
                    final_list.append(data[0])
                data = cursor.next()
        else:
            for handle in id_list:
                person = db.get_person_from_handle(handle)
                if not task(db,person):
                    final_list.append(handle)
        return final_list

    def check_or(self,db,id_list):
        return self.check_func(db,id_list,self.or_test)

    def check_and(self,db,id_list):
        final_list = []
        flist = self.flist
        if id_list == None:
            cursor = db.get_person_cursor()
            data = cursor.next()
            p = RelLib.Person
            while data:
                person = p(data[1])
                val = True
                for rule in flist:
                    if not rule.apply(db,person):
                        val = False
                        break
                if not val:
                    final_list.append(data[0])
                data = cursor.next()
        else:
            for handle in id_list:
                person = db.get_person_from_handle(handle)
                val = True
                for rule in flist:
                    if not rule.apply(db,person):
                        val = False
                        break
                if val:
                    final_list.append(handle)
        return final_list

    def check_one(self,db,id_list):
        return self.check_func(db,id_list,self.one_test)

    def check_xor(self,db,id_list):
        return self.check_func(db,id_list,self.xor_test)

    def xor_test(self,db,person):
        test = False
        for rule in self.flist:
            test = test ^ rule.apply(db,person)
        return test

    def one_test(self,db,person):
        count = 0
        for rule in self.flist:
            if rule.apply(db,person):
                if count:
                    return False
                count += 1
        return count == 1

    def or_test(self,db,person):
        for rule in self.flist:
            if rule.apply(db,person):
                return True
        return False
    
    def get_check_func(self):
        try:
            m = getattr(self, 'check_' + self.logical_op)
        except AttributeError:
            m = self.check_and
        return m

    def check(self,db,handle):
        return self.get_check_func()(db,[handle])

    def apply(self,db,id_list=None):
        m = self.get_check_func()
        for rule in self.flist:
            rule.prepare(db)
        res = m(db,id_list)
        for rule in self.flist:
            rule.reset()
        return res
