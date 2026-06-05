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


"""
FamilySearch sync secondary object for Gramps.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ...const import GRAMPS_LOCALE as glocale
from ..secondaryobj import SecondaryObject

_ = glocale.translation.gettext


class FamilySearchSync(SecondaryObject):
    """
    Secondary object storing FamilySearch sync state for a primary object.
    """

    def __init__(self, data=None):
        SecondaryObject.__init__(self)
        self.fsid = None
        self.is_root = False
        self.status_ts = None
        self.confirmed_ts = None
        self.gramps_modified_ts = None
        self.fs_modified_ts = None
        self.essential_conflict = False
        self.conflict = False

        if data:
            self.unserialize(data)

    def serialize(self):
        """
        Convert the object to persistent dict data.
        """
        return {
            "_class": self.__class__.__name__,
            "fsid": self.fsid,
            "is_root": self.is_root,
            "status_ts": self.status_ts,
            "confirmed_ts": self.confirmed_ts,
            "gramps_modified_ts": self.gramps_modified_ts,
            "fs_modified_ts": self.fs_modified_ts,
            "essential_conflict": self.essential_conflict,
            "conflict": self.conflict,
        }

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON schema for this class.
        """
        return {
            "type": "object",
            "title": _("FamilySearch sync"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "fsid": {"type": ["string", "null"], "title": _("FamilySearch ID")},
                "is_root": {"type": "boolean", "title": _("Is root")},
                "status_ts": {
                    "type": ["integer", "null"],
                    "title": _("Status timestamp"),
                },
                "confirmed_ts": {
                    "type": ["integer", "null"],
                    "title": _("Confirmed timestamp"),
                },
                "gramps_modified_ts": {
                    "type": ["integer", "null"],
                    "title": _("Gramps modified timestamp"),
                },
                "fs_modified_ts": {
                    "type": ["integer", "null"],
                    "title": _("FamilySearch modified timestamp"),
                },
                "essential_conflict": {
                    "type": "boolean",
                    "title": _("Essential conflict"),
                },
                "conflict": {"type": "boolean", "title": _("Conflict")},
            },
        }

    def unserialize(self, data):
        """
        Convert persistent dict data into this object.
        """
        if not isinstance(data, dict):
            raise TypeError("FamilySearchSync data must be a dict")
        return self.from_status_dict(data)

    def get_text_data_list(self):
        """
        Return textual attributes for generic text searching.
        """
        return [self.fsid] if self.fsid else []

    def get_text_data_child_list(self):
        """
        Return child objects that may carry text.
        """
        return []

    def get_referenced_handles(self):
        """
        No direct primary-object references are stored here.
        """
        return []

    def get_handle_referents(self):
        """
        No child objects here reference primary objects.
        """
        return []

    def is_empty(self):
        """
        Return True when no meaningful FamilySearch state is stored.
        """
        return not self.to_status_dict()

    def to_status_dict(self):
        """
        Convert this object to the dict shape expected by FSStatusDB/db API.
        """
        data = {}

        if self.fsid:
            fsid = str(self.fsid).strip()
            if fsid:
                data["fsid"] = fsid

        if self.is_root is True:
            data["is_root"] = True

        for key, value in (
            ("status_ts", self.status_ts),
            ("confirmed_ts", self.confirmed_ts),
            ("gramps_modified_ts", self.gramps_modified_ts),
            ("fs_modified_ts", self.fs_modified_ts),
        ):
            if isinstance(value, int) and not isinstance(value, bool) and value > 0:
                data[key] = value

        if self.essential_conflict is True:
            data["essential_conflict"] = True

        if self.conflict is True:
            data["conflict"] = True

        return data

    def from_status_dict(self, data):
        """
        Populate this object from the dict shape used by FSStatusDB/db API.
        """
        self.fsid = None
        self.is_root = False
        self.status_ts = None
        self.confirmed_ts = None
        self.gramps_modified_ts = None
        self.fs_modified_ts = None
        self.essential_conflict = False
        self.conflict = False

        if not data:
            return self

        fsid = data.get("fsid")
        self.fsid = fsid.strip() if isinstance(fsid, str) else None
        self.fsid = self.fsid or None
        self.is_root = data.get("is_root") or False
        self.status_ts = data.get("status_ts")
        self.confirmed_ts = data.get("confirmed_ts")
        self.gramps_modified_ts = data.get("gramps_modified_ts")
        self.fs_modified_ts = data.get("fs_modified_ts")
        self.essential_conflict = data.get("essential_conflict") or False
        self.conflict = data.get("conflict") or False
        return self
