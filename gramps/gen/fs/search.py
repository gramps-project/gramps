#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026            Gabriel Rios
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


"""Structured FamilySearch retrieval, independent of GTK and identity assignment."""

from __future__ import annotations

# ------------------------
# Python modules
# ------------------------
import re
import hashlib
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse, parse_qsl

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.fs.session import FSException

_ = glocale.translation.gettext
_PERSON_ID = re.compile(r"[A-Z0-9]{4}-[A-Z0-9]{3}")
_FS_HOSTS = {
    "familysearch.org",
    "www.familysearch.org",
    "beta.familysearch.org",
    "api.familysearch.org",
    "apibeta.familysearch.org",
}


def person_id_from_text(value: str) -> str:
    """Read a person PID or recognized person URL, never a historical-record ARK.

    :param value: A bare person identifier or FamilySearch person URL.
    :returns: The uppercase PID, or an empty string for another resource.
    """
    value = value.strip()
    if _PERSON_ID.fullmatch(value.upper()):
        return value.upper()
    parsed = urlparse(value)
    if parsed.scheme == "ark":
        path = parsed.path
    elif parsed.scheme == "https" and parsed.hostname in _FS_HOSTS:
        path = parsed.path
    else:
        return ""
    match = re.fullmatch(
        r"(?:/(?:[a-z]{2}/)?tree/person/(?:details|sources|memories)/|"
        r"/platform/tree/persons/|/?(?:ark:/)?61903/4:1:)([A-Za-z0-9]{4}-[A-Za-z0-9]{3})/?",
        path,
    )
    return match.group(1).upper() if match else ""


# ------------------------------------------------------------
# SearchQuery
# ------------------------------------------------------------
@dataclass(frozen=True)
class SearchQuery:
    """Search fields supplied by a user or supported local snapshot."""

    given_name: str = ""
    surname: str = ""
    birth_place: str = ""
    birth_from: int | None = None
    birth_to: int | None = None
    death_place: str = ""
    death_from: int | None = None
    death_to: int | None = None
    father_given: str = ""
    father_surname: str = ""
    mother_given: str = ""
    mother_surname: str = ""
    spouse_given: str = ""
    spouse_surname: str = ""
    advanced: str = ""
    parent_given: str = ""
    parent_surname: str = ""

    def parameters(self, count: int = 25) -> dict[str, str]:
        """Build structured API parameters without changing original local values.

        :param count: Page size between one and one hundred.
        :returns: Query parameters ready for the session transport.
        :raises ValueError: If the query is empty or date bounds are invalid.
        """
        if (
            isinstance(count, bool)
            or not isinstance(count, int)
            or not 1 <= count <= 100
        ):
            raise ValueError(_("Search page size must be between 1 and 100."))
        params = {"count": str(count)}
        fields = {
            "givenName": self.given_name,
            "surname": self.surname,
            "birthLikePlace": self.birth_place,
            "deathLikePlace": self.death_place,
            "fatherGivenName": self.father_given,
            "fatherSurname": self.father_surname,
            "motherGivenName": self.mother_given,
            "motherSurname": self.mother_surname,
            "spouseGivenName": self.spouse_given,
            "spouseSurname": self.spouse_surname,
            "parentGivenName": self.parent_given,
            "parentSurname": self.parent_surname,
        }
        params.update(
            {
                "q." + key: value.strip()
                for key, value in fields.items()
                if value.strip()
            }
        )
        for label, lower, upper in [
            ("birthLikeDate", self.birth_from, self.birth_to),
            ("deathLikeDate", self.death_from, self.death_to),
        ]:
            for year in (lower, upper):
                if year is not None and (
                    isinstance(year, bool)
                    or not isinstance(year, int)
                    or not -9999 <= year <= 9999
                    or year == 0
                ):
                    raise ValueError(_("Enter a valid nonzero year."))
            if lower is not None and upper is not None and lower > upper:
                raise ValueError(
                    _("The beginning of a date range must precede its end.")
                )
            for suffix, year in [("from", lower), ("to", upper)]:
                if year is not None:
                    params[f"q.{label}.{suffix}"] = f"{year:+05d}"
        if self.advanced.strip():
            params["q"] = self.advanced.strip()
        if len(params) == 1:
            raise ValueError(_("Enter a name, date, place or family detail to search."))
        return params


# ------------------------------------------------------------
# SearchResult and SearchPage
# ------------------------------------------------------------
@dataclass(frozen=True)
class SearchResult:
    """A discovery result; its content is not canonical identity evidence."""

    person_id: str
    name: str
    lifespan: str = ""
    birth_place: str = ""
    death_place: str = ""
    canonical_verified: bool = False


@dataclass(frozen=True)
class SearchPage:
    """One result page, including withheld ambiguous response entries."""

    results: tuple[SearchResult, ...] = ()
    next_url: str = ""
    warnings: tuple[str, ...] = ()


def _subject(entry: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve the entry's actual main person instead of taking the first person."""
    content = entry.get("content") or {}
    if not isinstance(content, dict):
        return None
    gedcomx = content.get("gedcomx") or content.get("gedcomX") or {}
    if not isinstance(gedcomx, dict):
        return None
    persons = gedcomx.get("persons") or entry.get("persons") or []
    if not isinstance(persons, list):
        return None
    people = [p for p in persons if isinstance(p, dict)]
    description = gedcomx.get("description", "")
    descriptions = gedcomx.get("sourceDescriptions") or []
    if not isinstance(descriptions, list):
        return None
    for source in descriptions:
        if isinstance(source, dict) and description == "#" + str(source.get("id")):
            about = source.get("about", "")
            chosen = [
                p
                for p in people
                if about == "#" + str(p.get("id"))
                or person_id_from_text(str(about)) == p.get("id")
            ]
            if len(chosen) == 1:
                return chosen[0]
            return None
    entry_pid = person_id_from_text(str(entry.get("id", "")))
    chosen = [p for p in people if entry_pid and p.get("id") == entry_pid]
    if len(chosen) == 1:
        return chosen[0]
    return people[0] if len(people) == 1 else None


def parse_search_page(data: Any) -> SearchPage:
    """Parse search results while withholding entries with an ambiguous subject.

    :param data: A GEDCOM X Atom search response.
    :returns: The parsed page, with ambiguity warnings.
    :raises FSException: If the response is not a valid result feed.
    """
    if not isinstance(data, dict):
        raise FSException(_("FamilySearch search returned invalid data."))
    feed = data.get("feed", data)
    if not isinstance(feed, dict) or not isinstance(feed.get("entries"), list):
        raise FSException(_("FamilySearch search returned an invalid result feed."))
    results: dict[str, SearchResult] = {}
    warnings = []
    for entry in feed["entries"]:
        if not isinstance(entry, dict):
            warnings.append(_("An invalid search result was withheld."))
            continue
        person = _subject(entry)
        pid = person_id_from_text(str((person or {}).get("id", "")))
        if not person or not pid:
            warnings.append(
                _("A search result without an identifiable subject was withheld.")
            )
            continue
        display = person.get("display") or {}
        if not isinstance(display, dict):
            display = {}
        results[pid] = SearchResult(
            pid,
            str(display.get("name") or entry.get("title") or pid),
            str(display.get("lifespan") or display.get("lifeSpan") or ""),
            str(display.get("birthPlace") or ""),
            str(display.get("deathPlace") or ""),
        )
    links = feed.get("links") or {}
    next_link = links.get("next", {}) if isinstance(links, dict) else {}
    next_url = str(next_link.get("href") or "") if isinstance(next_link, dict) else ""
    return SearchPage(tuple(results.values()), next_url, tuple(warnings))


# ------------------------------------------------------------
# SearchService
# ------------------------------------------------------------
class SearchService:
    """Retrieve search pages using the existing authorized session transport."""

    def __init__(self, session: Any) -> None:
        """Store the session without modifying its authentication or tree selection."""
        self.session = session

    def page_identity(self, url: str) -> str:
        """Validate a continuation and hash its normalized identity without logging it."""
        try:
            if not isinstance(url, str) or len(url) > 65536:
                raise ValueError
            parsed = urlparse(url)
            expected_host = urlparse(str(getattr(self.session, "api_url", ""))).netloc
            pairs = parse_qsl(parsed.query, keep_blank_values=True, max_num_fields=512)
            keys = [key for key, _value in pairs]
            if (
                (parsed.scheme and parsed.scheme != "https")
                or (parsed.scheme and not parsed.netloc)
                or (
                    parsed.netloc
                    and (not expected_host or parsed.netloc != expected_host)
                )
                or parsed.path.rstrip("/") != "/platform/tree/search"
                or parsed.fragment
                or parsed.username is not None
                or parsed.password is not None
                or len(keys) != len(set(keys))
                or any(
                    key not in {"q", "count", "start", "offset"}
                    and re.fullmatch(
                        r"[qfc]\.[A-Za-z][A-Za-z0-9]*(?:\.[A-Za-z0-9]+)*", key
                    )
                    is None
                    for key in keys
                )
            ):
                raise ValueError
            for key, value in pairs:
                if key == "f.treeId" and value != getattr(
                    self.session, "selected_tree_id", "GLOBAL"
                ):
                    raise ValueError
                if key in {"count", "start", "offset"}:
                    if not re.fullmatch(r"[0-9]+", value) or len(value) > 10:
                        raise ValueError
                    lower, upper = (1, 100) if key == "count" else (0, 2147483647)
                    if not lower <= int(value) <= upper:
                        raise ValueError
            identity = (expected_host, parsed.path.rstrip("/"), tuple(sorted(pairs)))
            return hashlib.sha256(repr(identity).encode("utf-8")).hexdigest()
        except ValueError as error:
            raise FSException(
                _("FamilySearch returned an unsafe result-page link.")
            ) from error

    def search(self, query: SearchQuery, *, next_url: str = "") -> SearchPage:
        """Search or follow a same-environment result page through the middleware.

        :param query: The original search fields.
        :param next_url: A next-page link returned by a prior search.
        :returns: A discovery page; no binding is changed.
        :raises FSException: On access, service or malformed-response failures.
        """
        params = query.parameters()
        endpoint = "/platform/tree/search"
        if next_url:
            self.page_identity(next_url)
            endpoint = next_url
            params = {}
        response = self.session.get_url(
            endpoint,
            headers={"Accept": "application/x-gedcomx-atom+json"},
            params=params,
        )
        if isinstance(response, dict):
            return parse_search_page(response)
        status = getattr(response, "status_code", None)
        if status == 204:
            return SearchPage()
        if status != 200:
            raise FSException(_("FamilySearch search failed (HTTP %s).") % status)
        try:
            data = response.json()
        except (ValueError, TypeError) as exc:
            raise FSException(_("FamilySearch search returned invalid data.")) from exc
        return parse_search_page(data)
