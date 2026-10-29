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

"""Shared FamilySearch request coordination, fresh reads and immutable JSON views.

This infrastructure has no matching scheduler, job store, native edit or GTK
dependency. Legacy matching modules re-export their former helper names.
"""

from __future__ import annotations

# ------------------------
# Python modules
# ------------------------
from dataclasses import asdict
from email.utils import parsedate_to_datetime
import hashlib
import json
import math
import threading
import time
from typing import Any, Callable

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.fs.session import FSException

_ = glocale.translation.gettext


# ------------------------------------------------------------
# FSAccessError
# ------------------------------------------------------------
class FSAccessError(FSException):
    """Safe structured failure; an unavailable route is never an empty result."""

    def __init__(
        self,
        status: int | None,
        *,
        retryable: bool,
        reauth_required: bool = False,
        retry_after: float = 0,
    ) -> None:
        """Expose classifications without provider bodies, credentials or URLs."""
        super().__init__(_("FamilySearch request unavailable"))
        self.status = status
        self.retryable = retryable
        self.reauth_required = reauth_required
        self.retry_after = retry_after


# ------------------------------------------------------------
# ResponseReader
# ------------------------------------------------------------
class ResponseReader:
    """Shared status, retry and JSON validation for supported API reads."""

    def __init__(self, session: Any) -> None:
        """Retain the authorized transport; no private research harness is needed."""
        self.session = session

    def response_data(self, response: Any) -> dict[str, Any] | None:
        """Parse status and retry hints, preserving access failures as failures."""
        status = getattr(response, "status_code", None)
        if status == 204:
            return None
        if status != 200:
            retry_after = 0.0
            value = str(getattr(response, "headers", {}).get("Retry-After", ""))
            try:
                retry_after = max(0.0, float(value))
            except ValueError:
                try:
                    retry_after = max(
                        0.0, parsedate_to_datetime(value).timestamp() - time.time()
                    )
                except (ValueError, TypeError, OverflowError):
                    pass
            kind = getattr(self.session, "last_recovery_kind", "")
            if not math.isfinite(retry_after):
                retry_after = 0.0
            raise FSAccessError(
                status,
                retryable=status in {429, 502, 503, 504},
                reauth_required=kind == "auth_required" or status == 401,
                retry_after=retry_after,
            )
        try:
            data = response.json()
        except (ValueError, TypeError) as error:
            raise FSAccessError(status, retryable=True) from error
        if not isinstance(data, dict):
            raise FSAccessError(status, retryable=True)
        return data


# ------------------------------------------------------------
# plain_data
# ------------------------------------------------------------
def plain_data(value: Any) -> Any:
    """Encode immutable app models as JSON values, never native database tuples."""
    if hasattr(value, "__dataclass_fields__"):
        return plain_data(asdict(value))
    if isinstance(value, dict):
        return {key: plain_data(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain_data(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted(plain_data(item) for item in value)
    return value


# ------------------------------------------------------------
# RateGate
# ------------------------------------------------------------
class RateGate:
    """Share a bounded request cadence across all jobs using one session."""

    _creation_lock = threading.Lock()

    def __init__(self, requests_per_minute: float = 120) -> None:
        """Set a finite positive request budget; upstream429 still controls retries."""
        if not 0 < requests_per_minute <= 600:
            raise ValueError(_("Invalid FamilySearch request rate."))
        self.interval = 60 / requests_per_minute
        self.next_request = 0.0
        self.blocked_until = 0.0
        self.lock = threading.Lock()

    @classmethod
    def for_session(cls, session: Any) -> RateGate:
        """Use one rate gate per authorized transport, not per local person."""
        with cls._creation_lock:
            gate = getattr(session, "_fs_matching_rate_gate", None)
            if not isinstance(gate, cls):
                gate = cls()
                setattr(session, "_fs_matching_rate_gate", gate)
            return gate

    def acquire(self, check: Callable[[], None]) -> None:
        """Wait off the GUI thread, retaining responsive pause/cancellation checks."""
        with self.lock:
            when = max(time.monotonic(), self.next_request, self.blocked_until)
            self.next_request = when + self.interval
        while True:
            check()
            with self.lock:
                if self.blocked_until > when:
                    when = self.blocked_until
                    self.next_request = max(self.next_request, when + self.interval)
            delay = when - time.monotonic()
            if delay <= 0:
                return
            time.sleep(min(0.1, delay))

    def defer(self, seconds: float) -> None:
        """Apply an upstream delay to the whole session, not just one person."""
        with self.lock:
            self.blocked_until = max(
                self.blocked_until, time.monotonic() + max(0, seconds)
            )


# ------------------------------------------------------------
# FreshPreviewTransport
# ------------------------------------------------------------
class FreshPreviewTransport:
    """Use uncached, rate-limited reads with cancellation between network calls."""

    def __init__(self, session: Any, check: Callable[[], None]) -> None:
        """Share the matching session's cadence without reading native objects."""
        self.session = session
        self.api_url = session.api_url
        self.check = check
        self.gate = RateGate.for_session(session)

    def get_url(self, url: str, **kwargs: Any) -> Any:
        """Bound each fresh read and reject a response after its context changed."""
        self.gate.acquire(self.check)
        kwargs.setdefault("timeout", 30)
        result = self.session.get_url(url, **kwargs)
        self.check()
        if getattr(result, "status_code", None) in {401, 429, 502, 503, 504}:
            try:
                ResponseReader(self).response_data(result)
            except FSAccessError as error:
                self.gate.defer(error.retry_after)
                raise
        return result


def session_stamp(session: Any) -> str:
    """Fingerprint sign-in identity metadata without retaining bearer tokens."""
    values = (
        str(getattr(session, "auth_provider", "")),
        str(session.api_url).rstrip("/"),
        str(getattr(session, "foundation_login_id", "")),
        int(getattr(session, "auth_generation", 0)),
    )
    return hashlib.sha256(json.dumps(values).encode("utf-8")).hexdigest()
