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

"""GEDCOM file importer implementation.

This class adapts the existing ``importgedcom`` plugin to the new
``BaseImporter`` abstraction. For the purpose of the generic framework we
provide very simple implementations of the abstract methods. A full‑featured
search UI is out of scope for this initial commit.
"""

# -------------------------------------------------------------------------
# Standard Python modules
# -------------------------------------------------------------------------
from __future__ import annotations

import logging
from typing import List

# -------------------------------------------------------------------------
# Gramps modules
# -------------------------------------------------------------------------
from gramps.gen.db import DbWriteBase

# Import the legacy GEDCOM import function so we can reuse it.
from .importgedcom import importData

# -------------------------------------------------------------------------
# Local imports
# -------------------------------------------------------------------------
from .base_importer import BaseImporter, Candidate, SourceRecord, ComparisonResult

LOG = logging.getLogger(__name__)


class GedcomImporter(BaseImporter):
    """Concrete importer for GEDCOM files.

    The current implementation treats the GEDCOM file itself as the source
    record. ``search_candidates`` simply returns a single candidate that
    represents the file path supplied by the user. ``fetch_candidate``
    returns the file path again – the ``compare`` step is a no‑op because the
    legacy ``importData`` function performs a full import directly.
    """

    def __init__(self, db: DbWriteBase, user) -> None:
        super().__init__(db)
        self.user = user

    def search_candidates(self, query: str) -> List[Candidate]:
        # In a real implementation this would search a remote service. Here we
        # treat the query as a file path and return a single candidate.
        class _FileCandidate:
            def __init__(self, path: str) -> None:
                self.id = path

        LOG.debug("GedcomImporter.search_candidates called with query=%s", query)
        return [_FileCandidate(query)]

    def fetch_candidate(self, candidate_id: str) -> SourceRecord:
        # The candidate_id is the file path.
        LOG.debug("GedcomImporter.fetch_candidate called with id=%s", candidate_id)
        return candidate_id  # type: ignore[return-value]

    def compare(self, source: SourceRecord, target_handle) -> ComparisonResult:
        # GEDCOM import does not support incremental comparison yet. We return a
        # simple placeholder object.
        LOG.debug("GedcomImporter.compare called – not implemented for GEDCOM")

        class _SimpleResult:
            pass

        return _SimpleResult()  # type: ignore[return-value]

    def apply(self, comparison: ComparisonResult) -> None:
        # ``comparison`` is ignored; we invoke the legacy import directly.
        LOG.debug("GedcomImporter.apply called – invoking legacy importData")
        # ``source`` is the file path stored in the comparison placeholder – we
        # cannot retrieve it here, so this method expects the caller to have
        # performed the import already. For now we raise NotImplementedError to
        # signal that a proper implementation is needed.
        raise NotImplementedError(
            "GEDCOM apply step requires integration with the legacy importData"
        )
