#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2020       Paul Culley
# Copyright (C) 2020       Nick Hall
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
UID class for Gramps.
"""
import uuid
import os
#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext


#-------------------------------------------------------------------------
#
# UIDs for Person/Family
#
#-------------------------------------------------------------------------
class Uid(uuid.UUID):
    """
    UID class.

    Many programs GEDCOM support allows unique IDs to be added to Persons and
    Families via the '_UID' tag.  This class extends Gramps to support those
    UIDs.

    Since there is some variation on how UIDs are presented in GEDCOM files
    we support by parsing into a 16 byte integer if possible.  When not valid
    an exception is raised.

    When exporting to GEDCOM the value is always exported in the original
    Familysearch format.

    See also GEDCOM L group http://wiki-de.genealogy.net/GEDCOM/UID-Tag

    When creating our own UID, we follow the original FamilySearch format.

    The FamilySearch format consists of 36 uppercase hex characters, of which
    the first 32 characters are the unique ID encoded to hex.  The last four
    characters are a checksum, encoded to hex.

    The algorithm for creating the checksum comes from
      GEDCOM Unique Identifiers
      by Gordon Clarke — last modified 20070608 16:06

    (Example)      1 _UID 92FF8B766F327F48A256C3AE6DAE50D3A114

    Other formats that have been reported look like:
    (no checksum, ok)    1 _UID 92FF8B766F327F48A256C3AE6DAE50D3
    (formal UUID, ok)    1 _UID {A6247491-A693-4ca4-A764-DD1A752D8C36}
    (formal UUID, ok)    1 _UID A6247491-A693-4ca4-A764-DD1A752D8C36
    (bad checksum, fail) 1 _UID 92FF8B766F327F48A256C3AE6DAE50D30000
    (non-hex, fail)      1 _UID GWJ645C9-19X4-DF14-GQ3B-GQ3B594316C5
    """

    def __init__(self, source=None):
        if source:
            uid = source.strip('{ }').replace('-', '').upper()
            if len(uid) == 36:
                super().__init__(uid[:32])
                if uid[32:] != '{:04X}'.format(self.checksum()):
                    raise ValueError('Bad Checksum')
            elif len(uid) == 32:
                super().__init__(uid)
            else:
                raise ValueError('Bad UID')
        else:
            super().__init__(bytes=os.urandom(16))

    def gedcom_hex(self):
            return '{:032X}{:04X}'.format(self.int, self.checksum())

    def checksum(self):
        value = self.int
        check_a = check_b = 0
        for i in range(1, 17):
            check_a += value & 255
            check_b += (value & 255) * i
            value >>= 8
        return ((check_a % 256) << 8) + (check_b % 256)

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return self.__str__()

    def __setattr__(self, name, value):
        """
        This is needed to allow our json serialize/unserialize to work
        because the UUID class is normally set to be immutable
        """
        if name == 'int':
            object.__setattr__(self, 'int', value)

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        self.__init__(data)
        return self

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: Returns a dict containing the schema.
        :rtype: dict
        """
        return {
            "type": "object",
            "title": _("Uid"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "uid": {"type": "string",
                        "maxLength": 50,
                        "title": _("Uid")},
            }
        }
