#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Gabriel Rios
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <https://www.gnu.org/licenses/>.
#

"""Immutable event details and conservative date filters for person search."""

from __future__ import annotations

# ------------------------
# Python modules
# ------------------------
from dataclasses import dataclass

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import Date
from gramps.gen.types import EventHandle

_ = glocale.translation.gettext


# ------------------------------------------------------------
# LocalFact
# ------------------------------------------------------------
@dataclass(frozen=True)
class LocalFact:
    """Keep date precision/quality/calendar and role with the original event."""

    kind: str
    role: str
    event_handle: EventHandle
    year: int = 0
    month: int = 0
    day: int = 0
    modifier: int = Date.MOD_NONE
    quality: int = Date.QUAL_NONE
    calendar: int = Date.CAL_GREGORIAN
    text: str = ""
    place: str = ""


# ------------------------------------------------------------
# SearchPolicy
# ------------------------------------------------------------
@dataclass(frozen=True)
class SearchPolicy:
    """Year margin applied to exact dates when prefilling a person search."""

    year_margin: int = 2

    def __post_init__(self) -> None:
        """Require a finite nonnegative year margin for prefilled searches."""
        if (
            isinstance(self.year_margin, bool)
            or not isinstance(self.year_margin, int)
            or not 0 <= self.year_margin <= 25
        ):
            raise ValueError(_("Invalid search year margin."))


def vital_filters(
    facts: tuple[LocalFact, ...], kind: str, margin: int
) -> tuple[int | None, int | None, str]:
    """Use unambiguous primary Gregorian years and place text; preserve uncertain dates."""
    primary = [fact for fact in facts if fact.kind == kind and fact.role == "Primary"]
    places = {fact.place.strip() for fact in primary if fact.place.strip()}
    place = next(iter(places)) if len(places) == 1 else ""
    dated = [fact for fact in primary if fact.year]
    years = {fact.year for fact in dated}
    if len(years) != 1 or any(
        fact.modifier != Date.MOD_NONE
        or fact.quality != Date.QUAL_NONE
        or fact.calendar != Date.CAL_GREGORIAN
        or isinstance(fact.year, bool)
        or not isinstance(fact.year, int)
        or not -9999 <= fact.year <= 9999
        for fact in dated
    ):
        return None, None, place
    year = next(iter(years))
    # Neither the API nor Gramps' astronomical-free year notation uses year zero.
    lower = max(-9999 if year < 0 else 1, year - margin)
    upper = min(-1 if year < 0 else 9999, year + margin)
    return lower, upper, place
