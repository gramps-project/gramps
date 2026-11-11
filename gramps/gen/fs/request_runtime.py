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

"""Identify the FamilySearch sign-in associated with a pending action."""

from __future__ import annotations

# ------------------------
# Python modules
# ------------------------
import hashlib
import json
from typing import Any


def session_stamp(session: Any) -> str:
    """Fingerprint sign-in identity metadata without retaining bearer tokens."""
    values = (
        str(getattr(session, "auth_provider", "")),
        str(session.api_url).rstrip("/"),
        str(getattr(session, "foundation_login_id", "")),
        int(getattr(session, "auth_generation", 0)),
    )
    return hashlib.sha256(json.dumps(values).encode("utf-8")).hexdigest()
