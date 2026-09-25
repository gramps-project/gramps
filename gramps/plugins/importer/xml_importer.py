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

"""XML file importer implementation.

Provides a thin wrapper around the legacy ``importxml`` plugin so that it fits
the new :class:`BaseImporter` abstraction. The implementation mirrors the
``GedcomImporter`` – it treats the file path as the sole candidate and defers
the heavy lifting to the existing ``importData`` function.
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

# Legacy XML import function.
from .importxml import importData

# -------------------------------------------------------------------------
# Local imports
# -------------------------------------------------------------------------
from .base_importer import BaseImporter, Candidate, SourceRecord, ComparisonResult

LOG = logging.getLogger(__name__)


class XmlImporter(BaseImporter):
    """Concrete importer for Gramps XML files.

    Like :class:`GedcomImporter`, this class provides a minimal implementation
    that satisfies the abstract interface. A full incremental comparison is
    beyond the scope of this initial commit.
    """

    def __init__(self, db: DbWriteBase, user) -> None:
        super().__init__(db)
        self.user = user

    def search_candidates(self, query: str) -> List[Candidate]:
        class _FileCandidate:
            def __init__(self, path: str) -> None:
                self.id = path

        LOG.debug("XmlImporter.search_candidates called with query=%s", query)
        return [_FileCandidate(query)]

    def fetch_candidate(self, candidate_id: str) -> SourceRecord:
        LOG.debug("XmlImporter.fetch_candidate called with id=%s", candidate_id)
        return candidate_id  # type: ignore[return-value]

    def compare(self, source: SourceRecord, target_handle) -> ComparisonResult:
        LOG.debug("XmlImporter.compare called – not implemented for XML")

        class _SimpleResult:
            pass

        return _SimpleResult()  # type: ignore[return-value]

    def apply(self, comparison: ComparisonResult) -> None:
        LOG.debug("XmlImporter.apply called – invoking legacy importData")
        raise NotImplementedError(
            "XML apply step requires integration with the legacy importData"
        )
