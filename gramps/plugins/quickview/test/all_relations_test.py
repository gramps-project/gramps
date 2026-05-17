import unittest
import os
from unittest.mock import Mock, call
from csv import DictReader

from ....gen.db.utils import import_as_dict
from ....gen.const import DATA_DIR
from ....gen.user import User

# import the module under test
from ..all_relations import AllRelReport

# find the data directory
this_dir = os.path.dirname(__file__)
data_dir = os.path.join(this_dir, "data")

TEST_DIR = os.path.abspath(os.path.join(DATA_DIR, "tests"))
EXAMPLE = os.path.join(TEST_DIR, "example.gramps")
RELATIONSHIPS = os.path.join(TEST_DIR, "all_relations.csv")


class Contains(str):
    def __eq__(self, other):
        # " " is required, otherwise uncle-in-law in stepuncle-in-law (wrong!)
        return f" {self}" in other


class AllRelReport_Tests(unittest.TestCase):
    """
    AllRelReport tests
    """

    @classmethod
    def setUpClass(cls):
        """
        Import example database.
        """

        cls.db = import_as_dict(EXAMPLE, User())

    @classmethod
    def tearDownClass(cls):
        """
        Close database.
        """
        cls.db._close()

    def test_all_relations(self):
        """ """
        with open(RELATIONSHIPS) as csvfile:
            text_doc_mock = Mock()
            for rel in DictReader(csvfile):
                gramps_id_a = rel["gramps_id_a"]
                gramps_id_b = rel["gramps_id_b"]
                r = rel["relationship"]
                text_doc_mock.reset_mock()

                home_person = self.db.get_person_from_gramps_id(gramps_id_a)
                target_person = self.db.get_person_from_gramps_id(gramps_id_b)

                self.db.set_default_person_handle(home_person.get_handle())

                AllRelReport(self.db, text_doc_mock, target_person).run()

                with self.subTest(home=gramps_id_a, target=gramps_id_b):
                    text_doc_mock.write_text.assert_has_calls([call(Contains(r))])


if __name__ == "__main__":
    unittest.main()
