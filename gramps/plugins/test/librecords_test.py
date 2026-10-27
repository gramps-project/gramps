#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026 John Vitlin
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

"""Tests for Notable Records sorting."""

import unittest

from gramps.gen.lib import Date
from gramps.plugins.lib.librecords import _record


class TestRecordSorting(unittest.TestCase):
    """Test alphabetical ordering of records with equal values."""

    def test_highest_alpha_ties(self):
        """Equal highest values should be ordered by name, A-Z."""
        highest = []

        for name in ("Zara", "Anna", "Mike"):
            _record(None, highest, 5, name, "Person", name, 10)

        self.assertEqual(
            [str(record[2]) for record in highest],
            ["Anna", "Mike", "Zara"],
        )

    def test_lowest_alpha_ties(self):
        """Equal lowest values should be ordered by name, A-Z."""
        lowest = []

        for name in ("Zara", "Anna", "Mike"):
            _record(lowest, None, 5, name, "Person", name, 10)

        self.assertEqual(
            [str(record[2]) for record in lowest],
            ["Anna", "Mike", "Zara"],
        )

    def test_highest_value_priority(self):
        """Higher values must rank before names alphabetically."""
        highest = []

        for name, value in (
            ("Anna", 2),
            ("Zara", 5),
            ("Mike", 3),
            ("Bella", 5),
        ):
            _record(None, highest, value, name, "Person", name, 10)

        self.assertEqual(
            [(str(record[2]), record[0]) for record in highest],
            [
                ("Bella", 5),
                ("Zara", 5),
                ("Mike", 3),
                ("Anna", 2),
            ],
        )

    def test_highest_cutoff_ties(self):
        """All records tied at the cutoff should be retained."""
        highest = []

        for name, value in (
            ("Zara", 5),
            ("Anna", 5),
            ("Mike", 5),
            ("Bella", 3),
        ):
            _record(None, highest, value, name, "Person", name, 2)

        self.assertEqual(
            [str(record[2]) for record in highest],
            ["Anna", "Mike", "Zara"],
        )

    def test_lowest_cutoff_ties(self):
        """All lowest-value records tied at the cutoff should be retained."""
        lowest = []

        for name, value in (
            ("Zara", 2),
            ("Anna", 2),
            ("Mike", 2),
            ("Bella", 5),
        ):
            _record(lowest, None, value, name, "Person", name, 2)

        self.assertEqual(
            [str(record[2]) for record in lowest],
            ["Anna", "Mike", "Zara"],
        )

    def test_span_alpha_ties(self):
        """Equal age spans should be ordered alphabetically."""
        highest = []
        lowest = []

        birth_date = Date(1900, 1, 1)
        death_date = Date(1980, 1, 1)
        age = death_date - birth_date

        for name in ("Zara", "Anna", "Mike"):
            _record(
                lowest,
                highest,
                age,
                name,
                "Person",
                name,
                10,
            )

        expected = ["Anna", "Mike", "Zara"]

        self.assertEqual(
            [str(record[2]) for record in highest],
            expected,
        )
        self.assertEqual(
            [str(record[2]) for record in lowest],
            expected,
        )


if __name__ == "__main__":
    unittest.main()
