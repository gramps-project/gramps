#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2024-2026  Gabriel Rios
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

from __future__ import annotations

from .formatters import person_dates_str, fs_person_dates_str
from .comparators import (
    compare_gender,
    compare_fact,
    compare_names,
    compare_parents,
    compare_spouse_notes,
    compare_spouses,
    compare_other_facts,
)
from .aggregate import compare_fs_to_gramps

__all__ = [
    "person_dates_str",
    "fs_person_dates_str",
    "compare_gender",
    "compare_fact",
    "compare_names",
    "compare_parents",
    "compare_spouse_notes",
    "compare_spouses",
    "compare_other_facts",
    "compare_fs_to_gramps",
]
