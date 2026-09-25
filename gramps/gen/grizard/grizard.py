#
# Gramps - a GTK+/GNOME based genealogy program
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
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
Base class and interfaces for the Grizard import framework.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from __future__ import annotations
import abc
import difflib
import logging
import re
from typing import Any, NamedTuple

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.db.base import DbWriteBase
from gramps.gen.types import PersonHandle
from gramps.gen.lib import Person, Event, Name
from gramps.gen.soundex import soundex
from gramps.gen.const import GRAMPS_LOCALE as glocale

# -------------------------------------------------------------------------
#
# Log
#
# -------------------------------------------------------------------------
LOG = logging.getLogger(__name__)

_ = glocale.translation.gettext


# ------------------------------------------------------------
#
# GrizardCompareRow
#
# ------------------------------------------------------------
class GrizardCompareRow(NamedTuple):
    """
    Represent a single side-by-side comparative difference between a source
    and a target person record.
    """

    status: str  # "match", "differ", "source_only", "target_only"
    field: str  # e.g., "Given Name", "Surname", "Birth Date", etc.
    source_val: str  # value in external source (e.g. GEDCOM or FamilySearch)
    target_val: str  # value in main target Gramps DB
    source_date: str = ""
    target_date: str = ""
    field_type: str = ""  # metadata describing field type for apply routing
    extra_data: Any = None  # arbitrary custom data payload (e.g., event references)


# ------------------------------------------------------------
#
# GrizardBase
#
# ------------------------------------------------------------
class GrizardBase(abc.ABC):
    """
    Abstract base class representing the step-by-step wizard workflow (Grizard).

    The workflow sequence is:
    connect -> load -> match -> compare -> apply.
    """

    def __init__(self, db: DbWriteBase) -> None:
        """
        Initialize the Grizard workflow.

        :param db: The target Gramps database instance.
        """
        self.db = db
        self.context: dict[str, Any] = {}
        self.current_step: str = ""

    def get_steps(self) -> list[str]:
        """
        Return the list of step names in the wizard sequence.

        :returns: A list of step identifiers in order.
        :rtype: list[str]
        """
        return ["connect", "load", "match", "compare", "apply"]

    def get_step_title(self, step: str) -> str:
        """
        Return a user-friendly, translatable title for the step.

        :param step: The step identifier.
        :returns: Translatable step title.
        :rtype: str
        """
        titles = {
            "connect": _("Configure Connection"),
            "load": _("Load Data"),
            "match": _("Find Matching Persons"),
            "compare": _("Compare Differences"),
            "apply": _("Apply Changes"),
        }
        return titles.get(step, step)

    def get_step_description(self, step: str) -> str:
        """
        Return a user-friendly, translatable description for the step.

        :param step: The step identifier.
        :returns: Translatable step description.
        :rtype: str
        """
        descriptions = {
            "connect": _("Configure file path or authenticate with online service."),
            "load": _("Load/parse the external genealogy data into memory."),
            "match": _("Search for potential matches in your database."),
            "compare": _("Compare fields side-by-side between the source and target."),
            "apply": _("Merge selected changes or add new records to the database."),
        }
        return descriptions.get(step, step)

    def run_step(self, step: str, **kwargs: Any) -> Any:
        """
        Execute the hook corresponding to the specified step.

        :param step: The step identifier.
        :returns: The result of the step execution.
        """
        self.current_step = step
        LOG.debug("Running Grizard step: %s with args: %s", step, kwargs)

        if step == "connect":
            return self._connect(**kwargs)
        elif step == "load":
            return self._load(**kwargs)
        elif step == "match":
            return self._match(**kwargs)
        elif step == "compare":
            return self._compare(**kwargs)
        elif step == "apply":
            return self._apply(**kwargs)
        else:
            raise ValueError(f"Unknown step: {step}")

    @abc.abstractmethod
    def _connect(self, **kwargs: Any) -> bool:
        """
        Establish connection details.

        :returns: True if successful, False otherwise.
        :rtype: bool
        """

    @abc.abstractmethod
    def _load(self, **kwargs: Any) -> Any:
        """
        Load records from source into the wizard context.

        :returns: Loaded data/records.
        """

    @abc.abstractmethod
    def _match(self, **kwargs: Any) -> list[dict[str, Any]]:
        """
        Find candidates in target db matching source records.

        :returns: List of match candidates.
        :rtype: list[dict[str, Any]]
        """

    @abc.abstractmethod
    def _compare(self, **kwargs: Any) -> list[GrizardCompareRow]:
        """
        Perform a field-by-field comparison of a source person and target person.

        :returns: List of comparison rows.
        :rtype: list[GrizardCompareRow]
        """

    @abc.abstractmethod
    def _apply(self, **kwargs: Any) -> bool:
        """
        Apply selected changes to the target database.

        :returns: True if successful, False otherwise.
        :rtype: bool
        """


# ------------------------------------------------------------
#
# Given-name matching helpers
#
# ------------------------------------------------------------
_QUOTED_NICK_RE = re.compile(r'"[^"]*"|\([^)]*\)|\'[^\']*\'')


def _strip_embedded_nickname(given: str) -> str:
    """
    Remove embedded nicknames in quotes or parentheses.
    """
    return _QUOTED_NICK_RE.sub(" ", given)


def _given_tokens(given: str) -> list[str]:
    """
    Split a given-name string into lowercase tokens.
    """
    cleaned = _strip_embedded_nickname(given)
    cleaned = cleaned.replace("-", " ")
    return [tok.lower() for tok in cleaned.split() if tok]


def score_given_names(source_given: str, target_given: str) -> float:
    """
    Score two given-name strings from 0.0 to 1.0.
    """
    s_raw = (source_given or "").strip()
    t_raw = (target_given or "").strip()
    if not s_raw or not t_raw:
        return 0.0
    if s_raw.lower() == t_raw.lower():
        return 1.0
    s_tokens = _given_tokens(s_raw)
    t_tokens = _given_tokens(t_raw)
    if not s_tokens or not t_tokens:
        return 0.0
    if s_tokens == t_tokens:
        return 1.0
    # Reversed / reordered tokens: same set regardless of order
    if sorted(s_tokens) == sorted(t_tokens):
        return 0.9
    # Partial token overlap (e.g. shared middle name only)
    if set(s_tokens) & set(t_tokens):
        return 0.5
    # Fuzzy similarity on the cleaned full strings
    ratio = difflib.SequenceMatcher(
        None, " ".join(s_tokens), " ".join(t_tokens)
    ).ratio()
    if ratio >= 0.8:
        return 0.6
    if s_tokens[0][0] == t_tokens[0][0]:
        return 0.25
    return 0.0


# ------------------------------------------------------------
#
# CandidateMatcher
#
# ------------------------------------------------------------
class CandidateMatcher:
    """
    Match engine to identify potential matches in a Gramps DB for a source person.
    """

    def __init__(self, db: DbWriteBase) -> None:
        """
        Initialize the CandidateMatcher.

        :param db: The database to search for matches in.
        """
        self.db = db

    def get_surnames(self, name: Name) -> str:
        """
        Helper to extract all surnames from a name object as a space-separated string.

        :param name: The name object.
        :returns: Space-separated surnames.
        :rtype: str
        """
        return " ".join(
            [s.get_surname() for s in name.get_surname_list() if s.get_surname()]
        )

    def score_match(
        self,
        source: Person,
        target: Person,
        source_db: Any | None = None,
    ) -> float:
        """
        Score how closely two Person records match. Returns -1.0 for a complete mismatch,
        otherwise a non-negative float matching score.

        :param source: The source person object.
        :param target: The target person object.
        :param source_db: Database holding the source person (for birth events).
            Defaults to the target database when omitted.
        :returns: The calculated match score or -1.0.
        :rtype: float
        """
        # Gender must match, or be unknown/other in either
        s_gender = source.get_gender()
        t_gender = target.get_gender()
        if s_gender in (Person.MALE, Person.FEMALE) and t_gender in (
            Person.MALE,
            Person.FEMALE,
        ):
            if s_gender != t_gender:
                return -1.0

        score = 0.0

        # Compare surnames via exact and soundex
        s_name = source.get_primary_name()
        t_name = target.get_primary_name()

        s_surnames = self.get_surnames(s_name).strip()
        t_surnames = self.get_surnames(t_name).strip()

        s_lookup_db = source_db if source_db is not None else self.db
        # Given name match (token-aware: reorderings, quoted nicknames,
        # fuzzy similarity, same-initial fallback)
        s_given = s_name.first_name.strip()
        t_given = t_name.first_name.strip()

        given_score = 0.0
        if s_given and t_given:
            given_score = score_given_names(s_given, t_given)
            score += given_score

        # Avoid pairing newcomers on surname alone: when both given
        # names are present but totally dissimilar, cap the surname
        # credit so a shared surname cannot auto-match by itself.
        surname_score = 0.0
        if s_surnames and t_surnames:
            if s_surnames.lower() == t_surnames.lower():
                surname_score = 1.0
            else:
                try:
                    if soundex(s_surnames) == soundex(t_surnames):
                        surname_score = 0.75
                except Exception:
                    pass
            if given_score == 0.0 and s_given and t_given:
                surname_score = min(surname_score, 0.25)
            score += surname_score

        # Birth date match helper (partial-date aware)
        s_birth_ref = source.get_birth_ref()
        t_birth_ref = target.get_birth_ref()

        if s_birth_ref and t_birth_ref:
            try:
                s_birth = s_lookup_db.get_event_from_handle(s_birth_ref.ref)
                t_birth = self.db.get_event_from_handle(t_birth_ref.ref)
                s_date = s_birth.get_date_object()
                t_date = t_birth.get_date_object()
                s_year = s_date.get_year()
                t_year = t_date.get_year()
                if s_year > 0 and t_year > 0:
                    diff = abs(s_year - t_year)
                    if diff != 0:
                        if diff <= 2:
                            score += 0.5
                        elif diff <= 5:
                            score += 0.25
                    else:
                        s_mon = s_date.get_month()
                        t_mon = t_date.get_month()
                        s_day = s_date.get_day()
                        t_day = t_date.get_day()
                        if s_mon <= 0 or t_mon <= 0:
                            # One side is year-only: same year, partial info
                            score += 0.75
                        elif s_mon != t_mon:
                            score += 0.5
                        elif s_day <= 0 or t_day <= 0:
                            score += 0.85
                        elif s_day != t_day:
                            score += 0.75
                        else:
                            score += 1.0
            except Exception:
                pass

        return score

    def find_matches(
        self,
        source: Person,
        threshold: float = 1.0,
        source_db: Any | None = None,
    ) -> list[tuple[PersonHandle, float]]:
        """
        Search the target database for potential matching candidates.

        :param source: The source person object to find matches for.
        :param threshold: The minimum matching score required to include a candidate.
        :param source_db: Database holding the source person (for birth events).
        :returns: List of tuples containing target person handles and their match scores.
        :rtype: list[tuple[PersonHandle, float]]
        """
        results: list[tuple[PersonHandle, float]] = []

        for handle in self.db.iter_person_handles():
            try:
                target = self.db.get_person_from_handle(handle)
                score = self.score_match(source, target, source_db=source_db)
                if score >= threshold:
                    results.append((PersonHandle(handle), score))
            except Exception:
                continue

        # Sort descending by score
        results.sort(key=lambda item: item[1], reverse=True)
        return results
