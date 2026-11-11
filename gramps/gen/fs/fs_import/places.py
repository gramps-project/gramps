#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2025-2026  Gabriel Rios
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

# ------------------------
# Python modules
# ------------------------
import logging
from typing import Any

# ------------------------
# Gramps modules
# ------------------------
from gramps.gen.db import DbTxn
from gramps.gen.db.base import DbWriteBase

from gramps.gen.lib import Place, PlaceName, PlaceType, Url, UrlType, PlaceRef

from gramps.gen.fs import utils as fs_utilities
from gramps.gen.fs import tree
from gramps.gen.fs.constants import GEDCOMX_TO_GRAMPS_PLACES
from gramps.gen.fs.fs_import import deserializer as deserialize

# ------------------------
# Gramps specific
# ------------------------
from . import _

logger = logging.getLogger(__name__)


def _pt(symbol_name: str, fallback_value: int) -> PlaceType:
    """
    Resolve a place type constant with a fallback for older installations.

    :param symbol_name: The place type constant name.
    :param fallback_value: The fallback numeric value.
    :returns: The supported place type.
    """
    return getattr(PlaceType, symbol_name, PlaceType(fallback_value))


PT_COUNTRY = _pt("COUNTRY", 1)
PT_STATE = _pt("STATE", 9)
PT_COUNTY = _pt("COUNTY", 10)
PT_CITY = _pt("CITY", 14)
PT_PARISH = _pt("PARISH", 20)


def create_place(
    db: DbWriteBase, txn: DbTxn, fs_place: Any, parent: Place | None
) -> Place:
    """
    Create a place from a downloaded FamilySearch description.

    :param db: The destination database.
    :param txn: The import transaction.
    :param fs_place: The FamilySearch place description.
    :param parent: The resolved enclosing place, if available.
    :returns: The imported place.
    """
    place = Place()

    # Two URLs: FS description API and human page
    u1 = Url()
    u1.path = f"https://api.familysearch.org/platform/places/description/{fs_place.id}"
    u1.type = UrlType("FamilySearch")

    u2 = Url()
    u2.path = fs_place.links["place"].href.removesuffix("?flag=fsh")
    u2.type = UrlType("FamilySearch")

    tmp = Place()
    tmp.add_url(u1)
    tmp.add_url(u2)
    place._merge_url_list(tmp)

    name = PlaceName()
    name.set_value(fs_place.display.name)
    place.set_name(name)
    place.set_title(fs_place.display.name)

    if hasattr(fs_place, "type"):
        mapped = GEDCOMX_TO_GRAMPS_PLACES.get(fs_place.type)
        ptype = PlaceType(mapped) if mapped else None
    else:
        ptype = None

    # Coordinates (stored as strings in Gramps)
    place.lat = str(fs_place.latitude)
    place.long = str(fs_place.longitude)

    # Fallback type inference by hierarchy if not mapped
    if not ptype:
        if not parent:
            ptype = PT_COUNTRY
        else:
            if parent.place_type == PT_COUNTRY:
                ptype = PT_STATE
            elif parent.place_type == PT_STATE:
                ptype = PT_COUNTY
            elif parent.place_type == PT_COUNTY:
                ptype = PT_CITY
            elif parent.place_type == PT_CITY:
                ptype = PT_PARISH

    if parent:
        pref = PlaceRef()
        pref.ref = parent.handle
        place.add_placeref(pref)

    place.set_type(ptype)
    db.add_place(place, txn)
    db.commit_place(place, txn)

    fs_place._handle = place.handle
    if fs_utilities.FS_INDEX_PLACES is not None:
        fs_utilities.FS_INDEX_PLACES[u1.path] = place.handle
        fs_utilities.FS_INDEX_PLACES[u2.path] = place.handle

    return place


def get_place_by_id(db: DbWriteBase, fs_place: Any) -> Place | None:
    """
    Find an imported place by its FamilySearch ID or cached URLs.

    :param db: The destination database.
    :param fs_place: The FamilySearch place reference or description.
    :returns: The existing place, or ``None`` if not linked.
    """
    if (
        not getattr(fs_place, "id", None)
        and getattr(fs_place, "description", None)
        and fs_place.description[:1] == "#"
    ):
        fs_place.id = fs_place.description[1:]

    if not getattr(fs_place, "id", None):
        return None

    api_url = f"https://api.familysearch.org/platform/places/description/{fs_place.id}"
    if hasattr(fs_place, "links") and fs_place.links and fs_place.links.get("place"):
        human_url = fs_place.links["place"].href.removesuffix("?flag=fsh")
    else:
        human_url = None

    # fast path via global cache
    if fs_utilities.FS_INDEX_PLACES:
        handle = fs_utilities.FS_INDEX_PLACES.get(api_url) or (
            human_url and fs_utilities.FS_INDEX_PLACES.get(human_url)
        )
        if handle:
            try:
                return db.get_place_from_handle(handle)
            except Exception:
                pass
        else:
            return None

    # build FSID map on first use
    if not fs_utilities.FS_INDEX_PLACES:
        logger.debug("%s", _("Building FSID list for places"))
        fs_utilities.FS_INDEX_PLACES = {}
        for handle in db.get_place_handles():
            place = db.get_place_from_handle(handle)
            for url in place.urls:
                if str(url.type) == "FamilySearch":
                    fs_utilities.FS_INDEX_PLACES[url.path] = handle

    handle = fs_utilities.FS_INDEX_PLACES.get(api_url)
    return db.get_place_from_handle(handle) if handle else None


def add_place(
    db: DbWriteBase,
    txn: DbTxn,
    fs_place: Any,
    *,
    _resolving: set[str] | None = None,
) -> Place | None:
    """
    Resolve a place using its canonical description and enclosing places.

    :param db: The destination database.
    :param txn: The import transaction.
    :param fs_place: The FamilySearch place reference or description.
    :param _resolving: IDs in the current hierarchy resolution path.
    :returns: The imported place, or ``None`` if unavailable.
    """
    if fs_place is None:
        return None
    if not hasattr(fs_place, "_handle"):
        fs_place._handle = None

    if fs_place._handle:
        try:
            cached = db.get_place_from_handle(fs_place._handle)
            if cached is not None:
                return cached
        except Exception:
            pass

    gr_place = get_place_by_id(db, fs_place)
    if gr_place:
        fs_place._handle = gr_place.handle
        return gr_place

    if not getattr(fs_place, "id", None):
        return None

    resolving = set(_resolving or ())
    if fs_place.id in resolving:
        logger.warning("Circular FamilySearch place hierarchy at %s", fs_place.id)
        return None
    resolving.add(fs_place.id)

    logger.debug("add_place: %s", fs_place.id)
    endpoint = f"/platform/places/description/{fs_place.id}"
    if tree._fs_session is None:
        return None
    try:
        r = tree._fs_session.get_url(endpoint, {"Accept": "application/json,*/*"})
    except Exception:
        logger.warning(
            "Unable to download FamilySearch place %s", fs_place.id, exc_info=True
        )
        return None

    if not (r and r.status_code == 200):
        if r:
            logger.warning("WARNING: Status code: %s", r.status_code)
        return None

    try:
        data = r.json()
    except Exception as e:
        logger.warning("WARNING: corrupted file from %s, error: %s", endpoint, e)
        try:
            logger.debug("Response content: %r", r.content)
        except Exception:
            pass
        return None

    if not isinstance(data, dict):
        return None
    descriptions = data.get("places")
    if not isinstance(descriptions, list) or not descriptions:
        return None
    if not isinstance(descriptions[0], dict) or not descriptions[0].get("id"):
        return None

    g = deserialize.Gedcomx()
    deserialize.deserialize_json(g, data)

    fs_place_id = data["places"][0]["id"]
    fs_desc = deserialize.PlaceDescription._index.get(fs_place_id)
    if fs_desc is None:
        return None
    if fs_place_id != fs_place.id and fs_place_id in resolving:
        logger.warning("Circular FamilySearch place redirect at %s", fs_place_id)
        return None
    resolving.add(fs_place_id)

    if fs_desc.jurisdiction:
        parent_id = fs_desc.jurisdiction.resourceId
        fs_parent = deserialize.PlaceDescription._index.get(parent_id)
        if fs_parent is None:
            fs_parent = deserialize.PlaceDescription()
            fs_parent.id = parent_id
        gr_parent = add_place(db, txn, fs_parent, _resolving=resolving)
    else:
        gr_parent = None

    if fs_place_id != fs_place.id:
        existing = get_place_by_id(db, fs_desc)
        if not existing:
            # The response already supplies the canonical description. A
            # second download can fail despite this description being usable.
            existing = create_place(db, txn, fs_desc, gr_parent)

        u1 = Url()
        u1.path = (
            f"https://api.familysearch.org/platform/places/description/{fs_place.id}"
        )
        u1.type = UrlType("FamilySearch")

        u2 = Url()
        u2.path = fs_desc.links["place"].href.removesuffix("?flag=fsh")
        u2.type = UrlType("FamilySearch")

        tmp = Place()
        tmp.add_url(u1)
        tmp.add_url(u2)
        existing._merge_url_list(tmp)

        if fs_utilities.FS_INDEX_PLACES is not None:
            fs_utilities.FS_INDEX_PLACES[u1.path] = existing.handle
            fs_utilities.FS_INDEX_PLACES[u2.path] = existing.handle

        db.commit_place(existing, txn)
        fs_place._handle = existing.handle
        return existing

    return create_place(db, txn, fs_desc, gr_parent)
