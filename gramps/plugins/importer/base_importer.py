#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026  Your Name
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""Base classes for generic import framework.

This module defines :class:`BaseImporter`, an abstract base class that
encapsulates the common workflow for importing data from external sources
into Gramps. Concrete importers (file‑based or online) should subclass this
class and implement the abstract methods.
"""

# -------------------------------------------------------------------------
# Standard Python modules
# -------------------------------------------------------------------------
from __future__ import annotations

import abc
import logging
from typing import List, Protocol, runtime_checkable

# -------------------------------------------------------------------------
# Gramps modules
# -------------------------------------------------------------------------
from gramps.gen.types import PersonHandle
from gramps.gen.db import DbWriteBase

# -------------------------------------------------------------------------
# Local imports (none needed here)
# -------------------------------------------------------------------------

LOG = logging.getLogger(__name__)


@runtime_checkable
class Candidate(Protocol):
    """Protocol representing a lightweight candidate record.

    Implementations should provide at least an ``id`` attribute that can be
    used with :meth:`fetch_candidate`.
    """

    id: str


@runtime_checkable
class SourceRecord(Protocol):
    """Protocol for a full source record fetched from an external source.

    The concrete type will depend on the importer (GEDCOM, FamilySearch, …).
    """

    pass


@runtime_checkable
class ComparisonResult(Protocol):
    """Result of comparing a source record with a target Gramps person.

    The result should contain enough information for the UI layer to present
    a side‑by‑side view and for the ``apply`` method to update the database.
    """

    pass


class BaseImporter(abc.ABC):
    """Abstract base class for all importers.

    The typical workflow is:

    1. ``search_candidates`` – return a list of lightweight candidates based
       on a user‑provided query.
    2. ``fetch_candidate`` – retrieve the full record for a selected candidate.
    3. ``compare`` – produce a :class:`ComparisonResult` describing differences
       between the source record and an existing Gramps person.
    4. ``apply`` – persist the accepted changes to the database.
    """

    def __init__(self, db: DbWriteBase) -> None:
        """Create an importer bound to a writable Gramps database.

        :param db: A writable database instance (e.g., ``gramps.gen.db.DbBase``).
        """
        self.db = db
        LOG.debug("%s initialized with DB %s", self.__class__.__name__, db)

    @abc.abstractmethod
    def search_candidates(self, query: str) -> List[Candidate]:
        """Search for potential matches.

        :param query: User supplied search string (name, ID, etc.).
        :return: List of candidate objects.
        """

    @abc.abstractmethod
    def fetch_candidate(self, candidate_id: str) -> SourceRecord:
        """Retrieve the full source record for a candidate.

        :param candidate_id: Identifier returned by :meth:`search_candidates`.
        :return: A source‑record object.
        """

    @abc.abstractmethod
    def compare(
        self, source: SourceRecord, target_handle: PersonHandle
    ) -> ComparisonResult:
        """Compare a source record with an existing Gramps person.

        :param source: The full source record.
        :param target_handle: Handle of the Gramps person to compare against.
        :return: A comparison result used by the UI.
        """

    @abc.abstractmethod
    def apply(self, comparison: ComparisonResult) -> None:
        """Apply the accepted changes to the database.

        Implementations should perform the necessary writes using the bound
        ``self.db`` instance and commit the transaction.
        """
