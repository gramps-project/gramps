# -*- coding: utf-8 -*-
#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2026 Gabriel Rios
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

"""
helpers for syncing between Gramps and FamilySearch.
a lot of this file is fetch/normalize/build for notes, sources, memories,
and relationship pushes.
"""

# -------------------------------------------------------------------------
#
# Future imports
#
# -------------------------------------------------------------------------
from __future__ import annotations

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import mimetypes
import os
import re
import urllib.parse
from typing import Any, Dict, List, Optional, Set, Tuple

# -------------------------------------------------------------------------
#
# Third-party modules
#
# -------------------------------------------------------------------------
import requests  # type: ignore

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.db import DbTxn
from gramps.gen.display.place import displayer as place_displayer
from gramps.gen.lib import Attribute, AttributeType, Family, Person
from gramps.gen.utils.db import get_birth_or_fallback
from gramps.gen.utils.db import get_death_or_fallback

from gramps.gen.fs import utils as fs_utilities
from gramps.gen.fs.fs_import import deserializer as deserialize

_ = glocale.translation.gettext


def _response_status(resp: Any) -> int:
    """return an int status code"""
    try:
        return int(getattr(resp, "status_code", 0) or 0)
    except (TypeError, ValueError):
        return 0


def _response_headers(resp: Any) -> Dict[str, Any]:
    """return response headers or an empty dict."""
    headers = getattr(resp, "headers", None)
    return headers if headers is not None else {}


def _debug_enabled() -> bool:
    return os.environ.get("GRAMPS_FS_DEBUG", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _person_handle(obj: Any) -> Optional[str]:
    """pull a handle off an object if it exposes one."""
    handle = getattr(obj, "handle", None)
    if handle:
        return str(handle)

    getter = getattr(obj, "get_handle", None)
    if callable(getter):
        value = getter()
        return str(value) if value else None

    return None


def _extract_sdid_from_refish(obj: Any) -> str:
    if obj is None:
        return ""

    if isinstance(obj, str):
        text = obj.strip()
        if not text:
            return ""
        match = re.search(r"/descriptions/([^/?#]+)", text)
        return match.group(1).strip() if match else ""

    if not isinstance(obj, dict):
        return ""

    value = str(obj.get("descriptionId") or "").strip()
    if value:
        return value

    desc = obj.get("description")
    if isinstance(desc, dict):
        value = str(desc.get("resourceId") or desc.get("descriptionId") or "").strip()
        if value:
            return value

        ref = str(desc.get("resource") or desc.get("href") or "").strip()
        if ref:
            match = re.search(r"/descriptions/([^/?#]+)", ref)
            if match:
                return match.group(1).strip()

    elif isinstance(desc, str):
        match = re.search(r"/descriptions/([^/?#]+)", desc)
        if match:
            return match.group(1).strip()

    for key in ("resource", "href", "about"):
        ref = str(obj.get(key) or "").strip()
        if not ref:
            continue
        match = re.search(r"/descriptions/([^/?#]+)", ref)
        if match:
            return match.group(1).strip()

    return ""


def _load_attached_person_source_description_ids(
    session: Any, person_fsid: str
) -> Optional[Set[str]]:
    """Load the source description ids already attached to a person."""
    person_fsid = (person_fsid or "").strip()
    if not person_fsid:
        return set()

    data = _session_get_json(session, f"/platform/tree/persons/{person_fsid}/sources")
    if not isinstance(data, dict) or not data:
        return None

    attached: Set[str] = set()

    for person_data in data.get("persons") or []:
        if not isinstance(person_data, dict):
            continue

        pid = str(person_data.get("id") or "").strip()
        if pid and pid != person_fsid:
            continue

        for source_ref in person_data.get("sources") or []:
            sdid = _extract_sdid_from_refish(source_ref)
            if sdid:
                attached.add(sdid)

    if attached:
        return attached

    try:
        # if the raw dict parse missed it, here the GEDCOM X objects will try once.
        gx = deserialize.Gedcomx()
        try:
            gx.deserialize_json(data)
        except Exception:
            deserialize.deserialize_json(gx, data)

        for person_obj in list(getattr(gx, "persons", []) or []):
            if getattr(person_obj, "id", None) != person_fsid:
                continue

            for source_ref in list(getattr(person_obj, "sources", []) or []):
                sdid = str(getattr(source_ref, "descriptionId", "") or "").strip()
                if sdid:
                    attached.add(sdid)
            break
    except Exception:
        pass

    return attached


def _head_source_description(session: Any, sdid: str) -> Tuple[str, Any]:
    """head a source description and follow forwarded ids."""
    sdid = (sdid or "").strip()
    if not sdid:
        return sdid, None

    head = getattr(session, "head_url", None)
    if not callable(head):
        return sdid, None

    path = f"/platform/sources/descriptions/{sdid}"
    try:
        resp = head(path)
    except Exception:
        return sdid, None

    while resp is not None and _response_status(resp) == 301:
        headers = _response_headers(resp)

        new_id = str(headers.get("X-Entity-Forwarded-Id") or "").strip()
        if not new_id:
            location = str(
                headers.get("Location") or headers.get("location") or ""
            ).strip()
            if location:
                match = re.search(r"/descriptions/([^/?#]+)", location)
                if match:
                    new_id = match.group(1).strip()

        if not new_id:
            break

        sdid = new_id
        path = f"/platform/sources/descriptions/{sdid}"
        try:
            resp = head(path)
        except Exception:
            break

    return sdid, resp


def _resolve_active_source_description(session: Any, sdid: str) -> Tuple[str, str]:
    """Return the usable source description id plus a rough status."""
    original = (sdid or "").strip()
    if not original:
        return "", "missing"

    resolved, resp = _head_source_description(session, original)
    status = _response_status(resp)

    if status == 410:
        return original, "deleted"
    if status == 404:
        return original, "missing"
    if status in (200, 204):
        if resolved and resolved != original:
            return resolved, "merged"
        return resolved or original, "ok"
    if status == 301 and resolved and resolved != original:
        return resolved, "merged"

    data = _session_get_json(session, f"/platform/sources/descriptions/{original}")
    if isinstance(data, dict) and data:
        return original, "ok"

    return resolved or original, "unknown"


def _request_url(session: Any, endpoint: str) -> str:
    endpoint = endpoint if endpoint.startswith("/") else ("/" + endpoint)
    using_foundation = False
    using_foundation_fn = getattr(session, "_using_foundation_middleware", None)
    if callable(using_foundation_fn):
        try:
            using_foundation = bool(using_foundation_fn())
        except Exception:
            using_foundation = False

    if using_foundation:
        foundation_proxy_fn = getattr(session, "_foundation_proxy_url", None)
        if callable(foundation_proxy_fn):
            try:
                return str(foundation_proxy_fn(endpoint))
            except Exception:
                pass
        foundation_base = str(
            getattr(session, "foundation_base_url", "")
            or getattr(session, "FOUNDATION_BASE_URL", "")
            or ""
        ).rstrip("/")
        if foundation_base:
            return foundation_base + "/v1/fs/proxy" + endpoint

    base = (
        getattr(session, "api_url", "")
        or getattr(session, "API_URL", "")
        or "https://api.familysearch.org"
    )
    return str(base).rstrip("/") + endpoint


def _request_bearer_token(session: Any) -> str:
    using_foundation = False
    using_foundation_fn = getattr(session, "_using_foundation_middleware", None)
    if callable(using_foundation_fn):
        try:
            using_foundation = bool(using_foundation_fn())
        except Exception:
            using_foundation = False
    if using_foundation:
        return str(
            getattr(session, "foundation_session_token", "")
            or getattr(session, "access_token", "")
            or ""
        ).strip()
    return str(getattr(session, "access_token", "") or "").strip()


def _session_post_binary(
    session: Any, endpoint: str, data: bytes, headers: Dict[str, str]
) -> Any:
    """post raw bytes to FamilySearch and hand the response back."""
    endpoint = endpoint if endpoint.startswith("/") else ("/" + endpoint)

    # try the session wrappers first.
    post = getattr(session, "post", None)
    if callable(post):
        try:
            return post(endpoint, data=data, headers=headers)
        except TypeError:
            try:
                return post(endpoint, data, headers)
            except Exception:
                pass
        except Exception:
            pass

    post_url = getattr(session, "post_url", None)
    if callable(post_url):
        try:
            return post_url(endpoint, data=data, headers=headers)
        except TypeError:
            try:
                return post_url(endpoint, data, headers)
            except Exception:
                pass
        except Exception:
            pass

    # plain requests
    url = _request_url(session, endpoint)
    token = _request_bearer_token(session)

    final_headers = dict(headers)
    if (
        token
        and "Authorization" not in final_headers
        and "authorization" not in final_headers
    ):
        final_headers["Authorization"] = f"Bearer {token}"

    try:
        return requests.post(url, data=data, headers=final_headers, timeout=90)
    except Exception:
        return None


def _extract_memory_ids_from_upload_response(resp: Any) -> Tuple[str, str]:
    """pull memory ids out of upload response headers."""
    mem_id = ""
    mem_ref_id = ""

    headers = _response_headers(resp)
    mem_id = str(headers.get("X-Entity-Id") or headers.get("X-entity-id") or "").strip()

    location = str(headers.get("Location") or headers.get("location") or "").strip()
    if location:
        match = re.search(r"/memory-references/([^/?#]+)", location)
        if match:
            mem_ref_id = match.group(1).strip()
        else:
            tail = re.search(r"/([^/?#]+)$", location)
            if tail:
                mem_ref_id = tail.group(1).strip()

    return mem_id, mem_ref_id


def _resolve_media_path(db: Any, media_obj: Any) -> Optional[str]:
    """Figure out the local file path for a Gramps media object."""
    path = ""

    for method_name in ("get_path", "get_file_path", "get_filename", "get_file_name"):
        method = getattr(media_obj, method_name, None)
        if not callable(method):
            continue

        try:
            path = str(method() or "").strip()
        except Exception:
            path = ""

        if path:
            break

    if not path:
        path = str(
            getattr(media_obj, "path", "") or getattr(media_obj, "filename", "") or ""
        ).strip()

    if not path:
        return None

    if path.startswith("http://") or path.startswith("https://"):
        return None

    path = os.path.expanduser(path)

    if os.path.isabs(path) and os.path.exists(path):
        return path

    media_base = ""
    for method_name in ("get_mediapath", "get_media_path"):
        method = getattr(db, method_name, None)
        if not callable(method):
            continue

        try:
            media_base = str(method() or "").strip()
        except Exception:
            media_base = ""

        if media_base:
            break

    if media_base:
        candidate = os.path.join(media_base, path)
        if os.path.exists(candidate):
            return candidate

    if os.path.exists(path):
        return os.path.abspath(path)

    return None


def _collect_memory_push_items(dbstate: Any, person: Any) -> List[Dict[str, Any]]:
    """build the list of media items that can be pushed as memories."""
    items: List[Dict[str, Any]] = []
    db = dbstate.db

    media_refs = list(person.get_media_list() or [])

    for media_ref in media_refs:
        handle = str(getattr(media_ref, "ref", "") or "").strip()
        if not handle:
            ref_getter = getattr(media_ref, "get_reference_handle", None)
            if callable(ref_getter):
                value = ref_getter()
                handle = str(value or "").strip()

        if not handle:
            continue

        media_obj = None
        for getter_name in ("get_media_from_handle", "get_media_object_from_handle"):
            getter = getattr(db, getter_name, None)
            if not callable(getter):
                continue
            media_obj = getter(handle)
            if media_obj:
                break

        if not media_obj:
            continue

        existing_fsid = (fs_utilities.get_fsftid(media_obj) or "").strip()
        if existing_fsid:
            continue

        file_path = _resolve_media_path(db, media_obj)
        if not file_path:
            continue

        description = ""
        for method_name in ("get_description", "get_desc"):
            method = getattr(media_obj, method_name, None)
            if not callable(method):
                continue

            try:
                description = str(method() or "").strip()
            except Exception:
                description = ""

            if description:
                break

        if not description:
            description = os.path.basename(file_path)

        mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        artifact_type = "Photo" if mime.startswith("image/") else "Document"

        items.append(
            {
                "kind": "memory_create",
                "label": _("Memory: {t}").format(t=description),
                "fs_val": _("(missing)"),
                "gr_val": file_path,
                "media_handle": handle,
                "file_path": file_path,
                "mime": mime,
                "artifact_type": artifact_type,
                "title": description,
                "description": description,
                "filename": os.path.basename(file_path),
            }
        )

    return items


def _upload_person_memory(
    session: Any,
    person_fsid: str,
    file_path: str,
    *,
    title: str,
    description: str,
    filename: str,
    person_name: str,
    artifact_type: str,
) -> Tuple[Optional[str], Optional[str], str]:
    """upload one local media file as a FamilySearch memory."""
    person_fsid = (person_fsid or "").strip()
    if not person_fsid:
        return None, None, "Missing person FSID"

    if not file_path or not os.path.exists(file_path):
        return None, None, "File not found"

    mime = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    final_filename = filename or os.path.basename(file_path)

    params: Dict[str, str] = {}
    if title:
        params["title"] = title
    if description:
        params["description"] = description
    if person_name:
        params["personName"] = person_name
    if final_filename:
        params["filename"] = final_filename
    if artifact_type:
        params["type"] = artifact_type

    endpoint = f"/platform/tree/persons/{person_fsid}/memories"
    if params:
        endpoint = f"{endpoint}?{urllib.parse.urlencode(params)}"

    try:
        with open(file_path, "rb") as handle:
            data = handle.read()
    except OSError as err:
        return None, None, f"Failed to read file: {err}"

    headers = {
        "accept": "application/x-fs-v1+json",
        "content-type": mime,
        "content-disposition": f'attachment; filename="{final_filename}"',
    }

    resp = _session_post_binary(session, endpoint, data, headers=headers)
    if resp is None:
        return None, None, "No response from FamilySearch"

    status = _response_status(resp)
    if status not in (200, 201):
        return None, None, f"HTTP {status}: {_err_text(resp)}"

    mem_id, mem_ref_id = _extract_memory_ids_from_upload_response(resp)
    if not mem_id:
        return None, None, "Upload succeeded but no memory id returned"

    return mem_id, (mem_ref_id or None), ""


def _session_get_json(session: Any, endpoint: str) -> Optional[dict]:
    """fetch GEDCOM X-ish JSON from a session endpoint."""
    endpoint = endpoint if endpoint.startswith("/") else ("/" + endpoint)

    # session helpers first
    for method_name in ("get_jsonurl", "get_json", "get_gedcomx"):
        method = getattr(session, method_name, None)
        if not callable(method):
            continue

        try:
            data = method(endpoint)
        except Exception:
            continue

        if isinstance(data, dict):
            return data

        if hasattr(data, "json"):
            try:
                return data.json() or {}
            except Exception:
                pass

    # then try the raw response path
    get_url = getattr(session, "get_url", None)
    if callable(get_url):
        try:
            resp = get_url(endpoint, {"Accept": "application/x-gedcomx-v1+json"})
            if resp and hasattr(resp, "json"):
                return resp.json() or {}
        except TypeError:
            try:
                resp = get_url(
                    endpoint, headers={"Accept": "application/x-gedcomx-v1+json"}
                )
                if resp and hasattr(resp, "json"):
                    return resp.json() or {}
            except Exception:
                pass
        except Exception:
            pass

    # build the request directly if all else fails
    token = _request_bearer_token(session)
    url = _request_url(session, endpoint)

    headers = {"Accept": "application/x-gedcomx-v1+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json() or {}
    except Exception:
        return None


def _session_post_json(
    session: Any, endpoint: str, payload: dict, *, headers: Optional[dict] = None
) -> Any:
    """POST JSON to an endpoint and return the raw response."""
    endpoint = endpoint if endpoint.startswith("/") else ("/" + endpoint)

    final_headers = {
        "accept": "application/x-gedcomx-v1+json",
        "content-type": "application/x-gedcomx-v1+json",
    }
    if headers:
        final_headers.update(headers)

    # session wrappers first
    post = getattr(session, "post", None)
    if callable(post):
        try:
            return post(endpoint, json=payload, headers=final_headers)
        except TypeError:
            try:
                return post(endpoint, payload, final_headers)
            except Exception:
                pass
        except Exception:
            pass

    post_url = getattr(session, "post_url", None)
    if callable(post_url):
        try:
            return post_url(endpoint, json=payload, headers=final_headers)
        except Exception:
            pass

    # regular requests
    token = _request_bearer_token(session)
    url = _request_url(session, endpoint)

    if token and "Authorization" not in final_headers:
        final_headers["Authorization"] = f"Bearer {token}"

    try:
        return requests.post(url, json=payload, headers=final_headers, timeout=30)
    except Exception:
        return None


def _head_person(session: Any, fsid: str) -> Tuple[str, Any]:
    """head a person endpoint and follow forwarded ids."""
    fsid = (fsid or "").strip()
    if not fsid:
        return fsid, None

    head = getattr(session, "head_url", None)
    if not callable(head):
        return fsid, None

    path = f"/platform/tree/persons/{fsid}"
    try:
        resp = head(path)
    except Exception:
        return fsid, None

    while (
        resp is not None
        and _response_status(resp) == 301
        and "X-Entity-Forwarded-Id" in _response_headers(resp)
    ):
        new_id = str(_response_headers(resp).get("X-Entity-Forwarded-Id") or "").strip()
        if not new_id:
            break

        fsid = new_id
        path = f"/platform/tree/persons/{fsid}"
        try:
            resp = head(path)
        except Exception:
            break

    return fsid, resp


def _err_text(resp: Any) -> str:
    if resp is None:
        return ""

    try:
        data = resp.json()
        if (
            isinstance(data, dict)
            and isinstance(data.get("errors"), list)
            and data["errors"]
        ):
            first = data["errors"][0]
            message = (first.get("message") or "").strip()
            code = (first.get("code") or "").strip()
            if code and message:
                return f"{code}: {message}"
            return message or code
    except Exception:
        pass

    text = str(getattr(resp, "text", "") or "").strip()
    if not text:
        return ""
    return text[:600] + ("..." if len(text) > 600 else "")


def _resolve_active_person(session: Any, fsid: str) -> Tuple[str, str]:
    """return the active person id plus a rough status."""
    original = (fsid or "").strip()
    if not original:
        return "", "missing"

    resolved, resp = _head_person(session, original)
    status = _response_status(resp)

    if status == 410:
        return original, "deleted"
    if status == 404:
        return original, "missing"
    if status in (200, 204):
        if resolved and resolved != original:
            return resolved, "merged"
        return resolved or original, "ok"
    if status == 301 and resolved and resolved != original:
        return resolved, "merged"

    data = _session_get_json(session, f"/platform/tree/persons/{original}")
    if isinstance(data, dict) and data:
        return original, "ok"

    return resolved or original, "unknown"


def _fact_type_from_label(label: str) -> str:
    """Map Gramps labels to GEDCOM X fact URIs."""
    key = re.sub(r"\s+", " ", (label or "").strip().lower())

    mapping = {
        "birth": "http://gedcomx.org/Birth",
        "death": "http://gedcomx.org/Death",
        "burial": "http://gedcomx.org/Burial",
        "cremation": "http://gedcomx.org/Cremation",
        "baptism": "http://gedcomx.org/Baptism",
        "christening": "http://gedcomx.org/Christening",
        "residence": "http://gedcomx.org/Residence",
        "occupation": "http://gedcomx.org/Occupation",
        "marriage": "http://gedcomx.org/Marriage",
        "divorce": "http://gedcomx.org/Divorce",
        "annulment": "http://gedcomx.org/Annulment",
        "immigration": "http://gedcomx.org/Immigration",
        "emigration": "http://gedcomx.org/Emigration",
        "naturalization": "http://gedcomx.org/Naturalization",
        "stillbirth": "http://gedcomx.org/Stillbirth",
    }

    if key in mapping:
        return mapping[key]

    for prefix, uri in mapping.items():
        if key.startswith(prefix):
            return uri

    return ""


def _extract_gramps_note_fsid(gr_note_obj: Any) -> str:
    """Read the linked FS note id from a tagged Gramps note."""
    text_obj = getattr(gr_note_obj, "text", None)
    if text_obj is None or not hasattr(text_obj, "get_tags"):
        return ""

    tags = text_obj.get_tags()
    if not tags:
        return ""

    for tag in tags:
        try:
            name = getattr(getattr(tag, "name", None), "name", None)
            value = getattr(tag, "value", "") or ""
        except Exception:
            continue

        if name == "LINK" and isinstance(value, str) and value.startswith("_fsftid="):
            return value[8:].strip()

    return ""


def _gramps_note_title(gr_note_obj: Any) -> str:
    """Return display title for Gramps note."""
    note_type = getattr(gr_note_obj, "type", None)
    if note_type is not None and hasattr(note_type, "xml_str"):
        try:
            return _(note_type.xml_str())
        except Exception:
            pass

    value = getattr(gr_note_obj, "type", "Note")
    return str(value) if value is not None else _("Note")


def _normalize_note_text(text: str) -> str:
    cleaned = text or ""
    if cleaned.startswith("\ufeff"):
        cleaned = cleaned[1:]
    return cleaned.strip()


def _load_fs_person_notes(session: Any, fsid: str) -> List[Any]:
    """Load notes for a person and deserialize them into Gedcomx objects."""
    data = _session_get_json(session, f"/platform/tree/persons/{fsid}/notes")
    if not data:
        return []

    gx = deserialize.Gedcomx()
    try:
        gx.deserialize_json(data)
    except Exception:
        try:
            # some payloads only behave through the other deserialize helper.
            deserialize.deserialize_json(gx, data)
        except Exception:
            return []

    for person_obj in list(getattr(gx, "persons", []) or []):
        if getattr(person_obj, "id", None) == fsid:
            return list(getattr(person_obj, "notes", []) or [])

    notes = getattr(gx, "notes", None)
    if notes:
        return list(notes) if isinstance(notes, (list, set, tuple)) else [notes]

    return []


def _build_person_payload(
    fsid: str, chosen: List[Dict[str, Any]], change_message: str
) -> Dict[str, Any]:
    """Build the person update payload from the chosen sync items."""
    message = (change_message or "").strip() or _("Updated from Gramps")

    person_obj: Dict[str, Any] = {"id": fsid}
    names: List[Dict[str, Any]] = []
    facts: List[Dict[str, Any]] = []

    for item in chosen:
        kind = item.get("kind")

        # name updates are built as preferred names
        if kind == "primary_name":
            full = str(item.get("gr_val") or "").strip()
            given = str(item.get("gr_given") or "").strip()
            surname = str(item.get("gr_surname") or "").strip()

            if not full and not (given or surname):
                continue

            name_form: Dict[str, Any] = {
                "fullText": full or f"{given} {surname}".strip()
            }

            parts: List[Dict[str, str]] = []
            if given:
                parts.append({"type": "http://gedcomx.org/Given", "value": given})
            if surname:
                parts.append({"type": "http://gedcomx.org/Surname", "value": surname})
            if parts:
                name_form["parts"] = parts

            name_obj: Dict[str, Any] = {
                "preferred": True,
                "nameForms": [name_form],
                "attribution": {"changeMessage": message},
            }

            name_id = str(item.get("fs_id") or "").strip()
            if name_id:
                name_obj["id"] = name_id

            names.append(name_obj)
            continue

        # fact updates can carry date, place, or both
        if kind == "fact":
            fact_id = str(item.get("fs_id") or "").strip()
            fact_type = ""

            if fact_id:
                fs_person = deserialize.Person.index.get(fsid)
                if fs_person and getattr(fs_person, "facts", None):
                    for fact_obj in fs_person.facts:
                        if getattr(fact_obj, "id", None) == fact_id and getattr(
                            fact_obj, "type", None
                        ):
                            fact_type = str(fact_obj.type)
                            break

            if not fact_type:
                fact_type = str(item.get("fact_type") or "").strip()

            if not fact_type:
                continue

            fact: Dict[str, Any] = {
                "type": fact_type,
                "attribution": {"changeMessage": message},
            }

            if fact_id:
                fact["id"] = fact_id

            gr_date = str(item.get("gr_date") or "").strip()
            gr_place = str(item.get("gr_val") or "").strip()

            if gr_date:
                fact["date"] = {"formal": gr_date, "original": gr_date}
            if gr_place:
                fact["place"] = {"original": gr_place}

            if "date" not in fact and "place" not in fact:
                continue

            facts.append(fact)

    if names:
        person_obj["names"] = names
    if facts:
        person_obj["facts"] = facts

    return {"persons": [person_obj]}


def _build_notes_payload(
    fsid: str, chosen: List[Dict[str, Any]], change_message: str
) -> Optional[Dict[str, Any]]:
    """build the notes payload for note creates/updates"""
    message = (change_message or "").strip() or _("Updated from Gramps")
    notes: List[Dict[str, Any]] = []

    for item in chosen:
        if item.get("kind") not in ("note_create", "note_update"):
            continue

        subject = str(item.get("gr_subject") or "").strip()
        text = str(item.get("gr_text") or "").strip()

        note: Dict[str, Any] = {
            "subject": subject,
            "text": text,
            "attribution": {"changeMessage": message},
        }

        fs_note_id = str(item.get("fs_id") or "").strip()
        if item.get("kind") == "note_update" and fs_note_id:
            note["id"] = fs_note_id

        notes.append(note)

    if not notes:
        return None

    return {"persons": [{"id": fsid, "notes": notes}]}


def _build_source_description_payload(
    title: str, citation_text: str, about: str, change_message: str
) -> Dict[str, Any]:
    message = (change_message or "").strip() or _("Updated from Gramps")

    sd: Dict[str, Any] = {
        "titles": [{"value": title}],
        "citations": [{"value": citation_text}],
        "attribution": {"changeMessage": message},
    }

    if about:
        sd["about"] = about

    return {"sourceDescriptions": [sd]}


def _extract_id_from_location(location: str) -> str:
    """Pull a source description id out of a Location"""
    if not location:
        return ""

    match = re.search(r"/descriptions/([^/?#]+)", location)
    if match:
        return match.group(1).strip()

    tail = re.search(r"/([^/?#]+)$", location)
    return tail.group(1).strip() if tail else ""


def _create_source_description(
    session: Any, title: str, citation_text: str, about: str, change_message: str
) -> Optional[str]:
    """create a source description and return its id if we can find it"""
    resp = _session_post_json(
        session,
        "/platform/sources/descriptions",
        _build_source_description_payload(title, citation_text, about, change_message),
    )
    if resp is None or _response_status(resp) not in (200, 201):
        return None

    # headers first, -> location, then the JSON body
    headers = _response_headers(resp)
    sdid = str(headers.get("X-Entity-Id") or headers.get("X-entity-id") or "").strip()
    if sdid:
        return sdid

    location = str(headers.get("Location") or headers.get("location") or "").strip()
    if location:
        return _extract_id_from_location(location)

    try:
        data = resp.json() if hasattr(resp, "json") else None
    except Exception:
        data = None

    if isinstance(data, dict):
        source_descriptions = (
            data.get("sourceDescriptions") or data.get("sourceDescription") or []
        )
        if isinstance(source_descriptions, list) and source_descriptions:
            sdid = (source_descriptions[0].get("id") or "").strip()
            if sdid:
                return sdid

    return None


def _build_person_sources_payload(
    session: Any, fsid: str, source_refs: List[Dict[str, Any]], change_message: str
) -> Dict[str, Any]:
    """wrap source refs into the person payload shape FS expects"""
    message = (change_message or "").strip() or _("Updated from Gramps")
    for source_ref in source_refs:
        source_ref.setdefault("attribution", {"changeMessage": message})
    return {"persons": [{"id": fsid, "sources": source_refs}]}


def _api_base(session: Any) -> str:
    base = (
        getattr(session, "api_url", "")
        or getattr(session, "API_URL", "")
        or "https://api.familysearch.org"
    )
    return str(base).rstrip("/")


def _build_source_ref(
    session: Any, sdid: str, tags: List[str], change_message: str
) -> Dict[str, Any]:
    """Build one person source ref pointed at a source description id."""
    desc_url = f"{_api_base(session)}/platform/sources/descriptions/{sdid}"
    out: Dict[str, Any] = {
        "description": desc_url,
        "tags": [{"resource": tag} for tag in tags if tag],
        "attribution": {
            "changeMessage": (change_message or "").strip() or _("Updated from Gramps")
        },
    }

    if not out["tags"]:
        out.pop("tags", None)

    return out


def _get_or_set_person_fsid(db: Any, txn: Any, gr_person: Person, fsid: str) -> None:
    """ensure the Gramps person carries this FS id."""
    fsid = (fsid or "").strip()
    if not fsid:
        return

    link_fn = getattr(fs_utilities, "link_gramps_fs_id", None)
    if callable(link_fn):
        try:
            link_fn(db, gr_person, fsid)
            return
        except Exception:
            pass

    attrs = list(gr_person.get_attribute_list() or [])

    kept: List[Any] = []
    for attr in attrs:
        try:
            attr_type = str(attr.get_type())
        except Exception:
            attr_type = ""

        if attr_type in ("_FSFTID", "_FSTID", "FamilySearch ID"):
            continue
        kept.append(attr)

    fs_attr = Attribute()
    fs_attr.set_type(AttributeType("_FSFTID"))
    fs_attr.set_value(fsid)
    kept.append(fs_attr)

    gr_person.set_attribute_list(kept)
    db.commit_person(gr_person, txn)


def _gramps_name_parts(gr_person: Person) -> Tuple[str, str]:
    """Return the primary given/surname pair from a Gramps person."""
    name = gr_person.primary_name
    if name is None:
        return "", ""

    given = (getattr(name, "first_name", "") or "").strip()

    try:
        surname = (name.get_surname() or "").strip()
    except Exception:
        surname = (getattr(name, "surname", "") or "").strip()

    return given, surname


def _gender_uri(gr_person: Person) -> str:
    """Map Gramps gender to a GEDCOM X gender URI."""
    gender = gr_person.get_gender()
    if gender == Person.MALE:
        return "http://gedcomx.org/Male"
    if gender == Person.FEMALE:
        return "http://gedcomx.org/Female"
    return "http://gedcomx.org/Unknown"


def _event_to_fact(db: Any, event: Any, fact_type_uri: str) -> Optional[Dict[str, Any]]:
    """Turn a Gramps event into a simple GEDCOM X fact payload."""
    if event is None:
        return None

    try:
        date_formal = fs_utilities.gramps_date_to_formal(event.date) or ""
    except Exception:
        date_formal = ""

    place_text = ""
    if getattr(event, "place", None):
        try:
            place = db.get_place_from_handle(event.place)
            place_text = (place_displayer.display(db, place) or "").strip()
        except Exception:
            place_text = ""

    if not date_formal and not place_text:
        return None

    fact: Dict[str, Any] = {"type": fact_type_uri}
    if date_formal:
        fact["date"] = {"formal": date_formal, "original": date_formal}
    if place_text:
        fact["place"] = {"original": place_text}
    return fact


def _birth_death_facts(db: Any, gr_person: Person) -> List[Dict[str, Any]]:
    """Collect birth/death facts we can safely send to FS."""
    facts: List[Dict[str, Any]] = []

    birth_event = get_birth_or_fallback(db, gr_person)
    death_event = get_death_or_fallback(db, gr_person)

    birth_fact = _event_to_fact(db, birth_event, "http://gedcomx.org/Birth")
    if birth_fact:
        facts.append(birth_fact)

    death_fact = _event_to_fact(db, death_event, "http://gedcomx.org/Death")
    if death_fact:
        facts.append(death_fact)

    return facts


def _extract_created_person_id(resp: Any) -> str:
    """Pull the new person id from headers or the JSON body."""
    headers = _response_headers(resp)

    person_id = str(
        headers.get("X-Entity-Id") or headers.get("X-entity-id") or ""
    ).strip()
    if person_id:
        return person_id

    location = str(headers.get("Location") or headers.get("location") or "").strip()
    if location:
        match = re.search(r"/persons/([^/?#]+)", location)
        if match:
            return match.group(1).strip()

        tail = re.search(r"/([^/?#]+)$", location)
        if tail:
            return tail.group(1).strip()

    try:
        data = resp.json() if hasattr(resp, "json") else None
    except Exception:
        data = None

    if isinstance(data, dict):
        persons = data.get("persons") or []
        if isinstance(persons, list) and persons:
            person_id = (persons[0].get("id") or "").strip()
            if person_id:
                return person_id

    return ""


def _fs_create_person_basic(
    session: Any, db: Any, gr_person: Person, change_message: str
) -> Optional[str]:
    """create a basic FS person from Gramps name/gender/facts data."""
    given, surname = _gramps_name_parts(gr_person)
    full = f"{given} {surname}".strip() if (given or surname) else ""

    if not full:
        return None

    message = (change_message or "").strip() or _("Created from Gramps")

    parts: List[Dict[str, str]] = []
    if given:
        parts.append({"type": "http://gedcomx.org/Given", "value": given})
    if surname:
        parts.append({"type": "http://gedcomx.org/Surname", "value": surname})

    name_form: Dict[str, Any] = {"fullText": full}
    if parts:
        name_form["parts"] = parts

    person_payload: Dict[str, Any] = {
        "names": [
            {
                "preferred": True,
                "nameForms": [name_form],
                "attribution": {"changeMessage": message},
            }
        ],
        "gender": {
            "type": _gender_uri(gr_person),
            "attribution": {"changeMessage": message},
        },
        "attribution": {"changeMessage": message},
    }

    facts = _birth_death_facts(db, gr_person)
    if facts:
        person_payload["facts"] = facts

    payload = {"persons": [person_payload]}

    resp = None
    for endpoint in ("/platform/tree/persons", "/platform/tree/persons/"):
        resp = _session_post_json(session, endpoint, payload)
        if resp is None:
            continue
        if _response_status(resp) in (200, 201):
            break

    if resp is None or _response_status(resp) not in (200, 201):
        return None

    fsid = _extract_created_person_id(resp)
    return fsid.strip() or None


def _ok_or_duplicate(resp: Any) -> bool:
    if resp is None:
        return False

    status = _response_status(resp)
    if status in (200, 201, 204):
        return True

    if status in (400, 409):
        message = _err_text(resp).lower()
        if "already" in message or "exists" in message or "duplicate" in message:
            return True

    return False


def _post_couple_relationship(
    session: Any, fsid1: str, fsid2: str, change_message: str
) -> Tuple[bool, str]:
    """Create the couple relationship between two linked FS people."""
    fsid1 = (fsid1 or "").strip()
    fsid2 = (fsid2 or "").strip()
    if not fsid1 or not fsid2:
        return False, "Missing spouse FSID(s)"

    message = (change_message or "").strip() or "Created from Gramps"
    base = _api_base(session)

    rel = {
        "type": "http://gedcomx.org/Couple",
        "person1": {
            "resource": f"{base}/platform/tree/persons/{fsid1}",
            "resourceId": fsid1,
        },
        "person2": {
            "resource": f"{base}/platform/tree/persons/{fsid2}",
            "resourceId": fsid2,
        },
        "attribution": {"changeMessage": message},
    }

    payload = {"relationships": [rel]}
    headers = {
        "accept": "application/x-fs-v1+json",
        "content-type": "application/x-fs-v1+json",
    }

    last_resp = None
    for endpoint in ("/platform/tree/relationships", "/platform/tree/relationships/"):
        last_resp = _session_post_json(session, endpoint, payload, headers=headers)
        if _ok_or_duplicate(last_resp):
            return True, ""

    if last_resp is None:
        return False, "No response from FamilySearch"

    return False, f"HTTP {_response_status(last_resp)}: {_err_text(last_resp)}"


def _post_child_and_parents(
    session: Any,
    child_fsid: str,
    parent1_fsid: str,
    parent2_fsid: str,
    change_message: str,
) -> Tuple[bool, str]:
    """Create the child-and-parents relationship and post it."""
    child_fsid = (child_fsid or "").strip()
    parent1_fsid = (parent1_fsid or "").strip()
    parent2_fsid = (parent2_fsid or "").strip()

    if not child_fsid:
        return False, "Missing child FSID"
    if not parent1_fsid and not parent2_fsid:
        return False, "Missing parent FSID(s)"

    message = (change_message or "").strip() or "Created from Gramps"
    base = _api_base(session)

    capr: Dict[str, Any] = {
        "child": {
            "resource": f"{base}/platform/tree/persons/{child_fsid}",
            "resourceId": child_fsid,
        },
        "attribution": {"changeMessage": message},
    }

    if parent1_fsid:
        capr["parent1"] = {
            "resource": f"{base}/platform/tree/persons/{parent1_fsid}",
            "resourceId": parent1_fsid,
        }
        capr["parent1Facts"] = [
            {
                "id": "C.1",
                "type": "http://gedcomx.org/BiologicalParent",
                "attribution": {"changeMessage": message},
            }
        ]

    if parent2_fsid:
        capr["parent2"] = {
            "resource": f"{base}/platform/tree/persons/{parent2_fsid}",
            "resourceId": parent2_fsid,
        }
        capr["parent2Facts"] = [
            {
                "id": "C.2",
                "type": "http://gedcomx.org/BiologicalParent",
                "attribution": {"changeMessage": message},
            }
        ]

    payload: Dict[str, Any] = {"childAndParentsRelationships": [capr]}
    headers: Dict[str, str] = {
        "accept": "application/x-fs-v1+json",
        "content-type": "application/x-fs-v1+json",
    }

    last_resp = None
    for endpoint in ("/platform/tree/relationships", "/platform/tree/relationships/"):
        last_resp = _session_post_json(session, endpoint, payload, headers=headers)
        if _ok_or_duplicate(last_resp):
            return True, ""

    if last_resp is None:
        return False, "No response from FamilySearch"

    return False, f"HTTP {_response_status(last_resp)}: {_err_text(last_resp)}"


def _family_other_parent_handle(family: Family, me_handle: str) -> Optional[str]:
    """Given one family member handle, return the other parent."""
    father = family.get_father_handle()
    mother = family.get_mother_handle()

    if father == me_handle:
        return mother
    if mother == me_handle:
        return father
    return None


def _collect_relatives(
    db: Any, me: Person
) -> Tuple[List[str], List[str], List[str], List[str]]:
    """collect parent, spouse, child, and family handles for a person."""
    parent_handles: List[str] = []
    spouse_handles: List[str] = []
    child_handles: List[str] = []
    family_handles: List[str] = []

    parents_family_handle = me.get_main_parents_family_handle()
    if not parents_family_handle:
        parent_families = list(me.get_parent_family_handle_list() or [])
        parents_family_handle = parent_families[0] if parent_families else None

    if parents_family_handle:
        family = db.get_family_from_handle(parents_family_handle)
        if family:
            father = family.get_father_handle()
            mother = family.get_mother_handle()

            if father:
                parent_handles.append(father)
            if mother:
                parent_handles.append(mother)

    family_handles = list(me.get_family_handle_list() or [])

    for family_handle in family_handles:
        family = db.get_family_from_handle(family_handle)
        if not family:
            continue

        spouse_handle = _family_other_parent_handle(family, me.handle)
        if spouse_handle and spouse_handle not in spouse_handles:
            spouse_handles.append(spouse_handle)

        child_refs = list(family.get_child_ref_list() or [])
        for child_ref in child_refs:
            child_handle = getattr(child_ref, "ref", None)
            if child_handle and child_handle not in child_handles:
                child_handles.append(child_handle)

    return parent_handles, spouse_handles, child_handles, family_handles
