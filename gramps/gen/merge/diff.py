#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2012       Doug Blank <doug.blank@gmail.com>
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

"""
This package implements an object difference engine.
"""

import json

from ..db.utils import import_as_dict
from ..lib.serialize import to_json
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


def to_struct(obj):
    """
    Convert an object into a struct.
    """
    return json.loads(to_json(obj))


def diff_dates(json1, json2):
    """
    Compare two json date objects. Returns True if different.
    """
    if json1 == json2:  # if same, then Not Different
        return False  # else, they still might be Not Different
    elif isinstance(json1, dict) and isinstance(json2, dict):
        if json1["dateval"] == json2["dateval"] and json2["dateval"] != 0:
            return False
        elif json1["text"] == json2["text"]:
            return False
        else:
            return True
    else:
        return True


def diff_items(path, json1, json2):
    """
    Compare two json objects. Returns True if different.
    """
    if json1 == json2:
        return False
    elif isinstance(json1, list) and isinstance(json2, list):
        if len(json1) != len(json2):
            return True
        else:
            pos = 0
            for v1, v2 in zip(json1, json2):
                result = diff_items(path + ("[%d]" % pos), v1, v2)
                if result:
                    return True
                pos += 1
            return False
    elif isinstance(json1, dict) and isinstance(json2, dict):
        for key in json1.keys():
            if key == "change":
                continue  # don't care about time differences, only data changes
            elif key == "date":
                result = diff_dates(json1["date"], json2["date"])
                if result:
                    # print("different dates", path)
                    # print("   old:", json1["date"])
                    # print("   new:", json2["date"])
                    return True
            else:
                result = diff_items(path + "." + key, json1[key], json2[key])
                if result:
                    return True
        return False
    else:
        # print("different values", path)
        # print("   old:", json1)
        # print("   new:", json2)
        return True


def diff_dbs(db1, db2, user):
    """
    1. new objects => mark for insert
    2. deleted objects, no change locally after delete date => mark
       for deletion
    3. deleted objects, change locally => mark for user confirm for
       deletion
    4. updated objects => do a diff on differences, mark origin
       values as new data
    """
    missing_from_old = []
    missing_from_new = []
    diffs = []
    with user.progress(_("Family Tree Differences"), _("Searching..."), 10) as step:
        for item in [
            "Person",
            "Family",
            "Source",
            "Citation",
            "Event",
            "Media",
            "Place",
            "Repository",
            "Note",
            "Tag",
        ]:
            step()

            handles_func1 = db1.method("get_%s_handles", item)
            handles_func2 = db2.method("get_%s_handles", item)
            handle_func1 = db1.method("get_%s_from_handle", item)
            handle_func2 = db2.method("get_%s_from_handle", item)

            handles1 = sorted([handle for handle in handles_func1()])
            handles2 = sorted([handle for handle in handles_func2()])
            p1 = 0
            p2 = 0
            while p1 < len(handles1) and p2 < len(handles2):
                if handles1[p1] == handles2[p2]:  # in both
                    item1 = handle_func1(handles1[p1])
                    item2 = handle_func2(handles2[p2])
                    diff = diff_items(item, to_struct(item1), to_struct(item2))
                    if diff:
                        diffs += [(item, item1, item2)]
                    # else same!
                    p1 += 1
                    p2 += 1
                elif handles1[p1] < handles2[p2]:  # p1 is mssing in p2
                    item1 = handle_func1(handles1[p1])
                    missing_from_new += [(item, item1)]
                    p1 += 1
                elif handles1[p1] > handles2[p2]:  # p2 is mssing in p1
                    item2 = handle_func2(handles2[p2])
                    missing_from_old += [(item, item2)]
                    p2 += 1
            while p1 < len(handles1):
                item1 = handle_func1(handles1[p1])
                missing_from_new += [(item, item1)]
                p1 += 1
            while p2 < len(handles2):
                item2 = handle_func2(handles2[p2])
                missing_from_old += [(item, item2)]
                p2 += 1
    return diffs, missing_from_old, missing_from_new


def diff_db_to_file(old_db, filename, user):
    # First, get data as a InMemoryDB
    new_db = import_as_dict(filename, user, user)
    if new_db is not None:
        # Next get differences:
        diffs, m_old, m_new = diff_dbs(old_db, new_db, user)
        return diffs, m_old, m_new
