import unittest
import os
from unittest.mock import Mock, call
from csv import DictReader

from ....gen.db.utils import import_as_dict
from gramps.gen.const import TEST_DIR

from ....gen.user import User

# import the module under test
from ..all_relations import AllRelReport

# find the data directory
this_dir = os.path.dirname(__file__)
data_dir = os.path.join(this_dir, "data")

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

        # the test results depend on specific grampsIds, so we need to use
        # the same prefixes as the example database
        cls.db = import_as_dict(EXAMPLE, User(), person_prefix="I%04d")

    @classmethod
    def tearDownClass(cls):
        """
        Close database.
        """

        cls.db.close()

    def test_all_relations(self):
        """ """
        with open(RELATIONSHIPS) as csvfile:
            text_doc = Mock()
            for rel in DictReader(csvfile):
                gramps_id_a = rel["gramps_id_a"]
                gramps_id_b = rel["gramps_id_b"]
                r = rel["relationship"]
                text_doc.reset_mock()

                with self.subTest(home=gramps_id_a, target=gramps_id_b):
                    home = self.db.get_person_from_gramps_id(gramps_id_a)
                    target = self.db.get_person_from_gramps_id(gramps_id_b)

                    self.db.set_default_person_handle(home.get_handle())
                    AllRelReport(self.db, text_doc, target).run()
                    text_doc.write_text.assert_has_calls([call(Contains(r))])


if __name__ == "__main__":
    unittest.main()
