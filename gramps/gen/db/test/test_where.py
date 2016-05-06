#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2016       Gramps Development Team
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

from gramps.gen.db.where import eval_where
from gramps.gen.lib import Person
import unittest

##########
# Tests:

def make_closure(surname):
    """
    Test closure.
    """
    from gramps.gen.lib import Person
    return (lambda person: 
            (person.primary_name.surname_list[0].surname == surname and
             person.gender == Person.MALE))

class Thing(object):
    def __init__(self):
        self.list = ["I0", "I1", "I2"]

    def where(self):
        return lambda person: person.gramps_id == self.list[1]

    def apply(self, db, person):
        return person.gender == Person.MALE

class ClosureTest(unittest.TestCase):
    def check(self, test):
        result = eval_where(test[0])
        self.assertTrue(result == test[1], "%s is not %s" % (result, test[1]))

    def test_01(self):
        self.check(
            (lambda family: (family.private and 
                             family.mother_handle.gramps_id != "I0001"), 
             ['AND', [['private', '==', True], 
                      ['mother_handle.gramps_id', '!=', 'I0001']]]))

    def test_02(self):
        self.check(
            (lambda person: LIKE(person.gramps_id, "I0001"),
             ['gramps_id', 'LIKE', 'I0001']))

    def test_03(self):
        self.check(
            (lambda note: note.gramps_id == "N0001",
             ['gramps_id', '==', 'N0001']))

    def test_04(self):
        self.check(
            (lambda person: person.event_ref_list.ref.gramps_id == "E0001",
             ['event_ref_list.ref.gramps_id', '==', 'E0001']))

    def test_05(self):
        self.check(
            (lambda person: LIKE(person.gramps_id, "I0001") or person.private,
             ["OR", [['gramps_id', 'LIKE', 'I0001'],
                     ["private", "==", True]]]))

    def test_06(self):
        self.check(
            (lambda person: person.event_ref_list <= 0,
             ["event_ref_list", "<=", 0]))

    def test_07(self):
        self.check(
            (lambda person: person.primary_name.surname_list[0].surname == "Smith",
             ["primary_name.surname_list.0.surname", "==", "Smith"]))

    def test_08(self):
        self.check(
            (make_closure("Smith"),
             ["AND", [["primary_name.surname_list.0.surname", "==", "Smith"],
                      ["gender", "==", 1]]]))

    def test_09(self):
        self.check(
            [Thing().where(), ["gramps_id", "==", "I1"]])

    def test_10(self):
        self.check(
            (lambda person: LIKE(person.gramps_id, "I000%"),
             ["gramps_id", "LIKE", "I000%"]))

    def test_11(self):
        self.check(
            [Thing().apply, ["gender", "==", 1]])

if __name__ == "__main__":
    unittest.main()
