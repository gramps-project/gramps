import random
import unittest


from gramps.gen.db.txn import DbTxn
from gramps.gen.db.utils import make_database
from gramps.gen.lib.childref import ChildRef
from gramps.gen.lib.family import Family
from gramps.gen.lib.familyreltype import FamilyRelType
from gramps.gen.lib.nameorigintype import NameOriginType
from gramps.gen.lib.person import Person
from gramps.gen.lib.surname import Surname
from gramps.gen.lib.name import Name
from gramps.gen.nameguesser import NameGuesser
from ..nameguesser_de import NameGuesser as NameGuesserDE
from ..nameguesser_es import NameGuesser as NameGuesserES
from ..nameguesser_is import NameGuesser as NameGuesserIS
from ..nameguesser_pt import NameGuesser as NameGuesserPT


class NameGuesserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = make_database("sqlite")
        cls.db.load(":memory:")

    def setUp(self):
        self.family_married = Family()
        self.family_married.set_father_handle("123456")
        self.family_married.set_mother_handle("654321")
        self.family_married.set_relationship(FamilyRelType.MARRIED)

        self.family_unmarried = Family()
        self.family_unmarried.set_father_handle("123456")
        self.family_unmarried.set_mother_handle("654321")
        self.family_unmarried.set_relationship(FamilyRelType.UNMARRIED)

        self.family_single_father = Family()
        self.family_single_father.set_father_handle("123456")
        self.family_single_father.set_relationship(FamilyRelType.UNKNOWN)

        self.family_single_mother = Family()
        self.family_single_mother.set_mother_handle("654321")
        self.family_single_mother.set_relationship(FamilyRelType.UNKNOWN)

    def test_example(self):
        self.assertTrue(True)

    def create_person_with_surname(self, surname_str):
        person = Person()
        person.set_handle(str(random.randint(100, 999)))
        name = Name()
        surname = Surname()
        surname.set_surname(surname_str)
        name.add_surname(surname)
        name.set_primary_surname(0)
        person.set_primary_name(name)
        return person

    def create_person_with_surnames(
        self, surname_patrilineal_str, surname_matrilineal_str
    ):
        person = Person()
        person.set_handle(str(random.randint(100, 999)))
        name = Name()
        surname_matr = Surname()
        surname_matr.set_surname(surname_matrilineal_str)
        surname_matr.set_origintype(NameOriginType(NameOriginType.MATRILINEAL))

        surname_patr = Surname()
        surname_patr.set_surname(surname_patrilineal_str)
        surname_patr.set_origintype(NameOriginType(NameOriginType.PATRILINEAL))
        name.set_surname_list([surname_patr, surname_matr])
        name.set_primary_surname(0)
        person.set_primary_name(name)
        return person

    def create_person_with_given_and_surname(
        self, given_str, surname_str, surname_origin_type
    ):
        person = Person()
        person.set_handle(str(random.randint(100, 999)))
        name = Name()
        surname = Surname()
        surname.set_surname(surname_str)
        surname.set_origintype(surname_origin_type)
        name.add_surname(surname)
        name.set_primary_surname(0)
        name.set_first_name(given_str)
        person.set_primary_name(name)
        return person


class NameGuesserTestES(NameGuesserTest):

    def setUp(self):
        self.nameguesser = NameGuesserES()
        mother = self.create_person_with_surnames("García", "López")
        father = self.create_person_with_surnames("Díaz", "Fernández")
        child = self.create_person_with_surnames("Martínez", "Gómez")

        with DbTxn("Add parents", self.db) as self.trans:
            self.db.commit_person(father, self.trans)
            self.db.commit_person(mother, self.trans)
            self.db.commit_person(child, self.trans)

        self.father = father
        self.mother = mother
        self.child = child

    def __get_childs_surname_list(self, has_father, has_mother):
        family = Family()
        if has_father:
            family.set_father_handle(self.father.handle)
        if has_mother:
            family.set_mother_handle(self.mother.handle)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        child_name = self.nameguesser.childs_name(db=self.db, family=family)
        return child_name.get_surname_list()

    def test_child_surname(self):
        surname_list = self.__get_childs_surname_list(True, True)
        self.assertEqual(surname_list[0].get_surname(), "Díaz")
        self.assertEqual(
            int(surname_list[0].get_origintype()), NameOriginType.PATRILINEAL
        )
        self.assertEqual(surname_list[1].get_surname(), "García")
        self.assertEqual(
            int(surname_list[1].get_origintype()), NameOriginType.MATRILINEAL
        )

    def test_child_surname_with_single_mother(self):
        surname_list = self.__get_childs_surname_list(False, True)
        self.assertEqual(surname_list[0].get_surname(), "García")

    def test_child_surname_with_single_father(self):
        surname_list = self.__get_childs_surname_list(True, False)
        self.assertEqual(surname_list[0].get_surname(), "Díaz")

    def test_father_surname(self):
        family = Family()
        ref = ChildRef()
        ref.ref = self.child.get_handle()
        family.add_child_ref(ref)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        father_name = self.nameguesser.fathers_name_from_child(
            db=self.db, family=family
        )
        self.assertEqual(father_name.get_surname_list()[0].get_surname(), "Martínez")
        self.assertEqual(
            int(father_name.get_surname_list()[0].get_origintype()),
            NameOriginType.PATRILINEAL,
        )

    def test_mother_surname(self):
        family = Family()
        ref = ChildRef()
        ref.ref = self.child.get_handle()
        family.add_child_ref(ref)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        mother_name = self.nameguesser.mothers_name_from_child(
            db=self.db, family=family
        )
        self.assertEqual(mother_name.get_surname_list()[0].get_surname(), "Gómez")
        self.assertEqual(
            int(mother_name.get_surname_list()[0].get_origintype()),
            NameOriginType.PATRILINEAL,
        )


class NameGuesserTestDE(NameGuesserTest):

    def setUp(self):
        self.nameguesser = NameGuesserDE()
        mother = self.create_person_with_surname("Meier")
        father = self.create_person_with_surname("Müller")
        child = self.create_person_with_surname("Schmidt")

        with DbTxn("Add parents", self.db) as self.trans:
            self.db.commit_person(father, self.trans)
            self.db.commit_person(mother, self.trans)
            self.db.commit_person(child, self.trans)

        self.father = father
        self.mother = mother
        self.child = child

    def __test_childs_surname(self, rel_type, expected_surname):
        family = Family()
        family.set_relationship(rel_type)
        family.set_father_handle(self.father.handle)
        family.set_mother_handle(self.mother.handle)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        child_name = self.nameguesser.childs_name(db=self.db, family=family)
        self.assertEqual(
            child_name.get_surname_list()[0].get_surname(), expected_surname
        )

    def __test_father_surname(self, rel_type, expected_surname):
        family = Family()
        family.set_relationship(rel_type)
        family.set_mother_handle(self.mother.handle)
        ref = ChildRef()
        ref.ref = self.child.get_handle()
        family.add_child_ref(ref)

        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        father_name = self.nameguesser.fathers_name_from_child(
            db=self.db, family=family
        )
        self.assertEqual(
            father_name.get_surname_list()[0].get_surname(), expected_surname
        )

    def __test_mother_surname(self, rel_type, expected_surname):
        family = Family()
        family.set_relationship(rel_type)
        family.set_father_handle(self.father.handle)
        ref = ChildRef()
        ref.ref = self.child.get_handle()
        family.add_child_ref(ref)

        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        mother_name = self.nameguesser.mothers_name_from_child(
            db=self.db, family=family
        )
        self.assertEqual(
            mother_name.get_surname_list()[0].get_surname(), expected_surname
        )

    def test_childs_surname_unmarried(self):
        self.__test_childs_surname(FamilyRelType.UNMARRIED, "Meier")

    def test_childs_surname_married(self):
        self.__test_childs_surname(FamilyRelType.MARRIED, "Müller")

    def test_fathers_surname_unmarried(self):
        self.__test_father_surname(FamilyRelType.UNMARRIED, "")

    def test_fathers_surname_married(self):
        self.__test_father_surname(FamilyRelType.MARRIED, "Schmidt")

    def test_mothers_surname_unmarried(self):
        self.__test_mother_surname(FamilyRelType.UNMARRIED, "Schmidt")

    def test_mothers_surname_married(self):
        self.__test_mother_surname(FamilyRelType.MARRIED, "")


class NameGuesserTestPT(NameGuesserTest):

    def setUp(self):
        self.nameguesser = NameGuesserPT()
        mother = self.create_person_with_surnames("Silva", "Santos")
        father = self.create_person_with_surnames("Oliveira", "Sousa")
        child = self.create_person_with_surnames("Alves", "Pereira")

        with DbTxn("Add parents", self.db) as self.trans:
            self.db.commit_person(father, self.trans)
            self.db.commit_person(mother, self.trans)
            self.db.commit_person(child, self.trans)

        self.father = father
        self.mother = mother
        self.child = child

    def __get_childs_surname_list(self, has_father, has_mother):
        family = Family()
        if has_father:
            family.set_father_handle(self.father.handle)
        if has_mother:
            family.set_mother_handle(self.mother.handle)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        child_name = self.nameguesser.childs_name(db=self.db, family=family)
        return child_name.get_surname_list()

    def test_child_surname(self):
        surname_list = self.__get_childs_surname_list(True, True)
        self.assertEqual(surname_list[0].get_surname(), "Silva")
        self.assertEqual(
            int(surname_list[0].get_origintype()), NameOriginType.MATRILINEAL
        )
        self.assertEqual(surname_list[1].get_surname(), "Oliveira")
        self.assertEqual(
            int(surname_list[1].get_origintype()), NameOriginType.PATRILINEAL
        )

    def test_child_surname_with_single_mother(self):
        surname_list = self.__get_childs_surname_list(False, True)
        self.assertEqual(surname_list[0].get_surname(), "Silva")

    def test_child_surname_with_single_father(self):
        surname_list = self.__get_childs_surname_list(True, False)
        self.assertEqual(surname_list[0].get_surname(), "Oliveira")

    def test_father_surname(self):
        family = Family()
        ref = ChildRef()
        ref.ref = self.child.get_handle()
        family.add_child_ref(ref)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        father_name = self.nameguesser.fathers_name_from_child(
            db=self.db, family=family
        )
        self.assertEqual(father_name.get_surname_list()[0].get_surname(), "Pereira")
        self.assertEqual(
            int(father_name.get_surname_list()[0].get_origintype()),
            NameOriginType.MATRILINEAL,
        )

    def test_mother_surname(self):
        family = Family()
        ref = ChildRef()
        ref.ref = self.child.get_handle()
        family.add_child_ref(ref)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        mother_name = self.nameguesser.mothers_name_from_child(
            db=self.db, family=family
        )
        self.assertEqual(mother_name.get_surname_list()[0].get_surname(), "Alves")
        self.assertEqual(
            int(mother_name.get_surname_list()[0].get_origintype()),
            NameOriginType.MATRILINEAL,
        )


class NameGuesserTestIS(NameGuesserTest):

    def setUp(self):
        self.nameguesser = NameGuesserIS()
        mother = self.create_person_with_given_and_surname(
            "Margrét", "Jóhannsdóttir", NameOriginType.PATRONYMIC
        )
        father = self.create_person_with_given_and_surname(
            "Gunnar", "Björnsson", NameOriginType.PATRONYMIC
        )
        son_matr = self.create_person_with_given_and_surname(
            "Jón", "Annasson", NameOriginType.MATRONYMIC
        )
        son_patr = self.create_person_with_given_and_surname(
            "Jón", "Agnarsson", NameOriginType.PATRONYMIC
        )
        daughter_matr = self.create_person_with_given_and_surname(
            "Anna", "Kristínsdóttir", NameOriginType.MATRONYMIC
        )
        daughter_patr = self.create_person_with_given_and_surname(
            "Anna", "Alexandersdóttir", NameOriginType.PATRONYMIC
        )

        with DbTxn("Add persons", self.db) as self.trans:
            self.db.commit_person(father, self.trans)
            self.db.commit_person(mother, self.trans)
            self.db.commit_person(son_matr, self.trans)
            self.db.commit_person(son_patr, self.trans)
            self.db.commit_person(daughter_matr, self.trans)
            self.db.commit_person(daughter_patr, self.trans)

        self.father = father
        self.mother = mother
        self.son_matr = son_matr
        self.son_patr = son_patr
        self.daughter_matr = daughter_matr
        self.daughter_patr = daughter_patr

    def test_child_surname(self):
        family = Family()
        family.set_father_handle(self.father.handle)
        family.set_mother_handle(self.mother.handle)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        child_name = self.nameguesser.childs_name(db=self.db, family=family)
        self.assertEqual(child_name.get_surname(), "Gunnarsson")

        self.assertEqual(
            int(child_name.get_primary_surname().get_origintype()),
            NameOriginType.PATRONYMIC,
        )

    def test_child_surname_with_single_mother(self):
        family = Family()
        family.set_mother_handle(self.mother.handle)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        child_name = self.nameguesser.childs_name(db=self.db, family=family)
        self.assertEqual(child_name.get_surname(), "Margrétsson")

        self.assertEqual(
            int(child_name.get_primary_surname().get_origintype()),
            NameOriginType.MATRONYMIC,
        )

    def test_father_given_name_from_sons_patronymic_name(self):
        family = Family()
        ref = ChildRef()
        ref.ref = self.son_patr.get_handle()
        family.add_child_ref(ref)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        father_name = self.nameguesser.fathers_name_from_child(
            db=self.db, family=family
        )
        self.assertEqual(father_name.get_first_name(), "Agnar")

    def test_father_given_name_from_sons_matronymic_name(self):
        family = Family()
        ref = ChildRef()
        ref.ref = self.son_matr.get_handle()
        family.add_child_ref(ref)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        father_name = self.nameguesser.fathers_name_from_child(
            db=self.db, family=family
        )
        self.assertEqual(father_name.get_first_name(), "")

    def test_father_given_name_from_daughters_patronymic_name(self):
        family = Family()
        ref = ChildRef()
        ref.ref = self.daughter_patr.get_handle()
        family.add_child_ref(ref)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        father_name = self.nameguesser.fathers_name_from_child(
            db=self.db, family=family
        )
        self.assertEqual(father_name.get_first_name(), "Alexander")

    def test_father_given_name_from_daughters_matronymic_name(self):
        family = Family()
        ref = ChildRef()
        ref.ref = self.daughter_matr.get_handle()
        family.add_child_ref(ref)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        father_name = self.nameguesser.fathers_name_from_child(
            db=self.db, family=family
        )
        self.assertEqual(father_name.get_first_name(), "")

    def test_mother_given_name_from_sons_patronymic_name(self):
        family = Family()
        ref = ChildRef()
        ref.ref = self.son_patr.get_handle()
        family.add_child_ref(ref)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        mother_name = self.nameguesser.mothers_name_from_child(
            db=self.db, family=family
        )
        self.assertEqual(mother_name.get_first_name(), "")

    def test_mother_given_name_from_sons_matronymic_name(self):
        family = Family()
        ref = ChildRef()
        ref.ref = self.son_matr.get_handle()
        family.add_child_ref(ref)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        mother_name = self.nameguesser.mothers_name_from_child(
            db=self.db, family=family
        )
        self.assertEqual(mother_name.get_first_name(), "Anna")

    def test_mother_given_name_from_daughters_patronymic_name(self):
        family = Family()
        ref = ChildRef()
        ref.ref = self.daughter_patr.get_handle()
        family.add_child_ref(ref)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        mother_name = self.nameguesser.mothers_name_from_child(
            db=self.db, family=family
        )
        self.assertEqual(mother_name.get_first_name(), "")

    def test_mother_given_name_from_daughters_matronymic_name(self):
        family = Family()
        ref = ChildRef()
        ref.ref = self.daughter_matr.get_handle()
        family.add_child_ref(ref)
        with DbTxn("Add Family", self.db) as trans:
            self.db.add_family(family, trans)

        mother_name = self.nameguesser.mothers_name_from_child(
            db=self.db, family=family
        )
        self.assertEqual(mother_name.get_first_name(), "Kristín")
