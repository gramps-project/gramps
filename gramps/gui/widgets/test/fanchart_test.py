# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gramps developers
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
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""
Regression tests for fan chart widget data-structure initialisation.

Bug 0013395 reported that Gramps crashed at startup with::

    AttributeError: 'NoneType' object has no attribute 'append'

in ``fanchart.py:set_userdata_age`` when:

* the Fan Chart was the last view displayed,
* "Remember last view displayed" was enabled,
* the Background was "Age (0-100) based gradient".

Root cause: :meth:`FanChartWidget.set_generations` initialised every
``self.data[i]`` slot to a shared ``(None,) * 4`` tuple, leaving the
4th element (``userdata``) as ``None``.  When
:meth:`_fill_data_structures` short-circuited (no ``rootpersonh`` yet),
``prepare_background_box`` later iterated over the unfilled slots and
called ``userdata.append(...)`` on ``None``.

These tests verify the invariant: after ``set_generations`` every data
slot's ``userdata`` is a list, regardless of whether
``_fill_data_structures`` has populated the slot.
"""

import unittest

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: F401  pylint: disable=unused-import

from ..fanchart import FORM_CIRCLE, FanChartWidget
from ..fanchart2way import FanChart2WayWidget


class TestFanChartWidgetSetGenerations(unittest.TestCase):
    """Ancestor fan chart (``FanChartWidget``)."""

    def setUp(self):
        # Bypass __init__ so the test does not require a Gtk display.
        # set_generations is pure-Python data structure initialisation.
        self.widget = FanChartWidget.__new__(FanChartWidget)
        self.widget.generations = 3
        self.widget.form = FORM_CIRCLE
        self.widget.childring = False

    def test_userdata_is_list_in_every_data_slot(self):
        """Every data[i][j][3] must be a list, never None (bug 0013395)."""
        self.widget.set_generations()
        for gen, slots in self.widget.data.items():
            for index, slot in enumerate(slots):
                self.assertIsInstance(
                    slot[3],
                    list,
                    f"data[{gen}][{index}][3] expected list, "
                    f"got {type(slot[3]).__name__}",
                )

    def test_each_data_slot_has_its_own_userdata_list(self):
        """Slots must not share a single list reference."""
        self.widget.set_generations()
        # Mutate one userdata and check no other slot was affected.
        sentinel = object()
        self.widget.data[2][0][3].append(sentinel)
        for gen, slots in self.widget.data.items():
            for index, slot in enumerate(slots):
                if (gen, index) == (2, 0):
                    continue
                self.assertNotIn(
                    sentinel,
                    slot[3],
                    f"data[{gen}][{index}][3] shares its list "
                    "reference with data[2][0][3]",
                )


class TestFanChart2WayWidgetSetGenerations(unittest.TestCase):
    """Two-way fan chart ascendance side (``FanChart2WayWidget``)."""

    def setUp(self):
        self.widget = FanChart2WayWidget.__new__(FanChart2WayWidget)
        self.widget.generations_asc = 3
        self.widget.generations_desc = 3

    def test_ascendance_userdata_is_list_in_every_data_slot(self):
        """Every ascendance data[i][j][3] must be a list (bug 0013395)."""
        self.widget.set_generations()
        for gen, slots in self.widget.data.items():
            for index, slot in enumerate(slots):
                self.assertIsInstance(
                    slot[3],
                    list,
                    f"data[{gen}][{index}][3] expected list, "
                    f"got {type(slot[3]).__name__}",
                )


if __name__ == "__main__":
    unittest.main()
