#! /usr/bin/env python3
"""
Gramps - a GTK+/GNOME based genealogy program

Copyright (c) 2016 Gramps Development Team

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
"""

import unittest

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.utils.id import set_det_id
from gramps.gen.db import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.dbstate import DbState
from gramps.cli.clidbman import CLIDbManager
from gramps.gen.lib import Person, Family, Note, Surname
from gramps.gen.merge import MergeFamilyQuery
from gramps.gen.utils.callman import CallbackManager


class DbTestClassBase(object):
    # Inherit from `object` so unittest doesn't think these are tests which
    # should be run

    @classmethod
    def setUpClass(cls):
        # print("doing setup with", cls.param)
        set_det_id(True)  # handles must be deterministic for this test
        cls.dbstate = DbState()
        cls.dbman = CLIDbManager(cls.dbstate)
        dirpath, _name = cls.dbman.create_new_db_cli(
            "Test: %s" % cls.param, dbid=cls.param
        )
        cls.db = make_database(cls.param)
        cls.db.load(dirpath, None)

    @classmethod
    def tearDownClass(cls):
        # print("tear down", cls.param)
        cls.db.close()
        cls.dbman.remove_database("Test: %s" % cls.param)

    def __add_person(self, gender, first_name, surname, trans):
        person = Person()
        person.gender = gender
        _name = person.primary_name
        _name.first_name = first_name
        surname1 = Surname()
        surname1.surname = surname
        _name.set_surname_list([surname1])
        self.db.add_person(person, trans)
        return person

    def __add_note(self, text, trans):
        note = Note(text=text)
        self.db.add_note(note, trans)
        return note

    def __add_family(self, father, mother, trans):
        family = Family()
        family.set_father_handle(father.handle)
        family.set_mother_handle(mother.handle)
        fam_handle = self.db.add_family(family, trans)
        father.add_family_handle(fam_handle)
        mother.add_family_handle(fam_handle)
        self.db.commit_person(father, trans)
        self.db.commit_person(mother, trans)
        return family

    def __setup_callbacks(self):
        self.db.connect("family-add", self._family_add)
        self.db.connect("family-update", self._family_update)
        self.db.connect("family-delete", self._family_delete)
        self.db.connect("person-add", self._person_add)
        self.db.connect("person-update", self._person_update)
        self.db.connect("person-delete", self._person_delete)
        self.db.connect("note-add", self._note_add)
        self.db.connect("note-update", self._note_update)
        self.db.connect("note-delete", self._note_delete)
        # we will also test the CallbackManager by watching a single person
        self.cm_sigs = []
        self.callman = CallbackManager(self.db)
        self.callman.register_callbacks(
            {
                "person-delete": self._cm_pers_delete,
                "person-update": self._cm_pers_update,
                "person-add": self._cm_pers_add,
            }
        )
        self.callman.connect_all(keys=["person"])
        self.callman.register_handles(
            {"person": ["0000000300000003", "0000000700000007"]}
        )

    def _family_add(self, *args):
        self._log_sig("family-add", args)

    def _family_update(self, *args):
        self._log_sig("family-update", args)

    def _family_delete(self, *args):
        self._log_sig("family-delete", args)

    def _person_add(self, *args):
        self._log_sig("person-add", args)

    def _person_update(self, *args):
        self._log_sig("person-update", args)

    def _person_delete(self, *args):
        self._log_sig("person-delete", args)

    def _note_add(self, *args):
        self._log_sig("note-add", args)

    def _note_update(self, *args):
        self._log_sig("note-update", args)

    def _note_delete(self, *args):
        self._log_sig("note-delete", args)

    def _log_sig(self, sig, args):
        # print("('%s', %s)," % (sig, args))
        self.sigs.append((sig, args[0]))

    def _cm_pers_add(self, *args):
        self.cm_sigs.append(("person-add", args[0]))

    def _cm_pers_update(self, *args):
        self.cm_sigs.append(("person-update", args[0]))

    def _cm_pers_delete(self, *args):
        self.cm_sigs.append(("person-delete", args[0]))

    def test_one(self):
        self.__setup_callbacks()
        self.sigs = []
        with DbTxn("Add test objects", self.db) as trans:
            father1 = self.__add_person(Person.MALE, "John", "Allen", trans)
            mother1 = self.__add_person(Person.FEMALE, "Mary", "Allen", trans)
            father2 = self.__add_person(Person.MALE, "John", "Baker", trans)
            mother2 = self.__add_person(Person.FEMALE, "Mary", "Baker", trans)
            family1 = self.__add_family(father1, mother1, trans)
            family2 = self.__add_family(father2, mother2, trans)
        self.callman.register_obj(father2, directonly=True)
        self.callman.register_obj(father2, directonly=False)
        sigs = [
            (
                "person-add",
                [
                    "0000000100000001",
                    "0000000200000002",
                    "0000000300000003",
                    "0000000400000004",
                ],
            ),
            ("family-add", ["0000000500000005", "0000000600000006"]),
            (
                "person-update",
                [
                    "0000000100000001",
                    "0000000200000002",
                    "0000000300000003",
                    "0000000400000004",
                ],
            ),
        ]
        self.assertEqual(sigs, self.sigs, msg="make families")
        # save state for later undo/redo check
        step1 = (family1, father1, mother1, family2, father2, mother2)
        fam_cnt = self.db.get_number_of_families()
        pers_cnt = self.db.get_number_of_people()
        self.assertEqual(fam_cnt, 2, msg="make families check")
        self.assertEqual(pers_cnt, 4, msg="make families persons check")

        # lets do a family merge, this will not only combine the families, but
        # also combine the the fathers and mothers as well
        self.sigs = []
        query = MergeFamilyQuery(
            self.db, family1, family2, father1.handle, mother1.handle
        )
        query.execute()
        sigs = [
            ("person-delete", ["0000000300000003", "0000000400000004"]),
            ("family-delete", ["0000000600000006"]),
            (
                "person-update",
                [
                    "0000000100000001",
                    "0000000200000002",
                    "0000000100000001",
                    "0000000200000002",
                ],
            ),
            ("family-update", ["0000000500000005", "0000000500000005"]),
        ]
        self.assertEqual(sigs, self.sigs, msg="merge families")
        fam_cnt = self.db.get_number_of_families()
        pers_cnt = self.db.get_number_of_people()
        self.assertEqual(fam_cnt, 1, msg="merge families check")
        self.assertEqual(pers_cnt, 2, msg="merge families persons check")
        # save new family'people for later redo check
        family1 = self.db.get_family_from_handle(family1.handle)
        father1 = self.db.get_person_from_handle(father1.handle)
        mother1 = self.db.get_person_from_handle(mother1.handle)
        step2 = (family1, father1, mother1)

        # we check that update and add signals are not emitted if the same
        # object is deleted in the same transation
        self.sigs = []
        with DbTxn("Note add/update/delete", self.db) as trans:
            note = self.__add_note("some text", trans)
            note.set("some other text")
            self.db.commit_note(note, trans)
            self.db.remove_note(note.handle, trans)
        sigs = [("note-delete", ["0000000700000007"])]
        self.assertEqual(sigs, self.sigs, msg="note signals check")
        note_cnt = self.db.get_number_of_notes()
        self.assertEqual(note_cnt, 0, msg="note check")

        # Test some undos, start with the note undo
        self.sigs = []
        self.db.undo()
        sigs = [("note-delete", ["0000000700000007"])]
        self.assertEqual(sigs, self.sigs, msg="undo note signals check")

        # Test merge undo
        self.sigs = []
        self.db.undo()
        sigs = [
            ("person-add", ["0000000400000004", "0000000300000003"]),
            ("family-add", ["0000000600000006"]),
            (
                "person-update",
                [
                    "0000000200000002",
                    "0000000100000001",
                    "0000000200000002",
                    "0000000100000001",
                ],
            ),
            (
                "family-update",
                [
                    "0000000500000005",
                    "0000000600000006",
                    "0000000600000006",
                    "0000000500000005",
                ],
            ),
        ]
        self.assertEqual(sigs, self.sigs, msg="undo merge signals check")
        fam_cnt = self.db.get_number_of_families()
        pers_cnt = self.db.get_number_of_people()
        self.assertEqual(fam_cnt, 2, msg="undo merge families check")
        self.assertEqual(pers_cnt, 4, msg="undo merge families persons check")
        # step1 = (family1, father1, mother1, family2, father2, mother2)
        obj_s = self.db.get_family_from_handle(family1.handle).serialize()
        self.assertEqual(
            obj_s, step1[0].serialize(), msg="undo merge families fam1 check"
        )
        obj_s = self.db.get_person_from_handle(father1.handle).serialize()
        self.assertEqual(
            obj_s, step1[1].serialize(), msg="undo merge families father1 check"
        )
        obj_s = self.db.get_person_from_handle(mother1.handle).serialize()
        self.assertEqual(
            obj_s, step1[2].serialize(), msg="undo merge families mother1 check"
        )
        obj_s = self.db.get_family_from_handle(family2.handle).serialize()
        self.assertEqual(
            obj_s, step1[3].serialize(), msg="undo merge families fam2 check"
        )
        obj_s = self.db.get_person_from_handle(father2.handle).serialize()
        self.assertEqual(
            obj_s, step1[4].serialize(), msg="undo merge families father2 check"
        )
        obj_s = self.db.get_person_from_handle(mother2.handle).serialize()
        self.assertEqual(
            obj_s, step1[5].serialize(), msg="undo merge families mother2 check"
        )

        # Test family build undo
        self.sigs = []
        self.db.undo()
        sigs = [
            (
                "person-delete",
                [
                    "0000000400000004",
                    "0000000300000003",
                    "0000000200000002",
                    "0000000100000001",
                ],
            ),
            ("family-delete", ["0000000600000006", "0000000500000005"]),
        ]
        self.assertEqual(sigs, self.sigs, msg="undo family build signals check")
        fam_cnt = self.db.get_number_of_families()
        pers_cnt = self.db.get_number_of_people()
        self.assertEqual(fam_cnt, 0, msg="undo make families check")
        self.assertEqual(pers_cnt, 0, msg="undo make families persons check")

        # Test family build redo
        self.sigs = []
        self.db.redo()
        sigs = [
            (
                "person-add",
                [
                    "0000000100000001",
                    "0000000200000002",
                    "0000000300000003",
                    "0000000400000004",
                ],
            ),
            ("family-add", ["0000000500000005", "0000000600000006"]),
            (
                "person-update",
                [
                    "0000000100000001",
                    "0000000200000002",
                    "0000000300000003",
                    "0000000400000004",
                ],
            ),
        ]
        self.assertEqual(sigs, self.sigs, msg="redo family build signals check")
        fam_cnt = self.db.get_number_of_families()
        pers_cnt = self.db.get_number_of_people()
        self.assertEqual(fam_cnt, 2, msg="redo make families check")
        self.assertEqual(pers_cnt, 4, msg="redo make families persons check")
        # step1 = (family1, father1, mother1, family2, father2, mother2)
        obj_s = self.db.get_family_from_handle(family1.handle).serialize()
        self.assertEqual(
            obj_s, step1[0].serialize(), msg="redo merge families fam1 check"
        )
        obj_s = self.db.get_person_from_handle(father1.handle).serialize()
        self.assertEqual(
            obj_s, step1[1].serialize(), msg="redo merge families father1 check"
        )
        obj_s = self.db.get_person_from_handle(mother1.handle).serialize()
        self.assertEqual(
            obj_s, step1[2].serialize(), msg="redo merge families mother1 check"
        )
        obj_s = self.db.get_family_from_handle(family2.handle).serialize()
        self.assertEqual(
            obj_s, step1[3].serialize(), msg="redo merge families fam2 check"
        )
        obj_s = self.db.get_person_from_handle(father2.handle).serialize()
        self.assertEqual(
            obj_s, step1[4].serialize(), msg="redo merge families father2 check"
        )
        obj_s = self.db.get_person_from_handle(mother2.handle).serialize()
        self.assertEqual(
            obj_s, step1[5].serialize(), msg="redo merge families mother2 check"
        )

        # Test family merge redo
        self.sigs = []
        self.db.redo()
        sigs = [
            ("person-delete", ["0000000300000003", "0000000400000004"]),
            ("family-delete", ["0000000600000006"]),
            (
                "person-update",
                [
                    "0000000100000001",
                    "0000000200000002",
                    "0000000100000001",
                    "0000000200000002",
                ],
            ),
            ("family-update", ["0000000500000005", "0000000500000005"]),
        ]
        self.assertEqual(sigs, self.sigs, msg="merge families")
        fam_cnt = self.db.get_number_of_families()
        pers_cnt = self.db.get_number_of_people()
        self.assertEqual(fam_cnt, 1, msg="merge families check")
        self.assertEqual(pers_cnt, 2, msg="merge families persons check")
        # step2 = (family1, father1, mother1)
        obj_s = self.db.get_family_from_handle(family1.handle).serialize()
        self.assertEqual(
            obj_s, step2[0].serialize(), msg="undo merge families fam1 check"
        )
        obj_s = self.db.get_person_from_handle(father1.handle).serialize()
        self.assertEqual(
            obj_s, step2[1].serialize(), msg="undo merge families father1 check"
        )
        obj_s = self.db.get_person_from_handle(mother1.handle).serialize()
        self.assertEqual(
            obj_s, step2[2].serialize(), msg="undo merge families mother1 check"
        )

        # Test note redo
        self.sigs = []
        self.db.redo()
        sigs = [("note-delete", ["0000000700000007"])]
        self.assertEqual(sigs, self.sigs, msg="undo note signals check")

        # now lets see if the callback manager is doing its job
        # print(self.cm_sigs)
        sigs = [
            ("person-add", ["0000000300000003"]),
            ("person-update", ["0000000300000003"]),
            ("person-delete", ["0000000300000003"]),
            ("person-add", ["0000000300000003"]),
            ("person-delete", ["0000000300000003"]),
            ("person-add", ["0000000300000003"]),
            ("person-update", ["0000000300000003"]),
            ("person-delete", ["0000000300000003"]),
        ]

        self.assertEqual(sigs, self.cm_sigs, msg="callback manager signals check")
        self.callman.unregister_handles({"person": ["0000000300000003"]})
        # we have to look deep into cm to see if handles are really deleted
        cm_persons = self.callman._CallbackManager__handles["person"]
        self.assertEqual(
            cm_persons, ["0000000700000007"], msg="Callback Manager unregister check"
        )
        self.callman.unregister_all()
        # we have to look deep into cm to see if handles are really deleted
        cm_persons = self.callman._CallbackManager__handles["person"]
        self.assertEqual(cm_persons, [], msg="Callback Manager unregister check")
        # we have to look deep into cm to see if callbacks are really deleted
        cm_padd_key = self.callman._CallbackManager__callbacks["person-add"][1]
        self.assertEqual(cm_padd_key, 10, msg="Callback Manager cb check")
        self.callman.disconnect_all()
        # we have to look deep into cm to see if callbacks are really deleted
        cm_padd_key = self.callman._CallbackManager__callbacks["person-add"][1]
        self.assertEqual(cm_padd_key, None, msg="Callback Manager disconnect cb check")


params = [("SQLite", "sqlite")]

for name, param in params:
    cls_name = "TestMyTestClass_%s" % (name,)
    globals()[cls_name] = type(
        cls_name,
        (DbTestClassBase, unittest.TestCase),
        {
            "param": param,
        },
    )

if __name__ == "__main__":
    unittest.main()
