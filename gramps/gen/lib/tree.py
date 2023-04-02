#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2013       Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2022       Christopher Horn
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
Tree information for Gramps.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Tree class
#
# -------------------------------------------------------------------------
class Tree:
    """
    Contains the tree related metadata.
    """

    def __init__(self, source=None):
        """
        Initialize the Tree object, copying from the source if provided.
        """
        self.name = ""
        self.description = ""
        self.copyright_used = ""
        self.license_used = ""
        self.contributors = ""
        if source:
            self.unserialize(source)

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (
            self.name,
            self.description,
            self.copyright_used,
            self.license_used,
            self.contributors,
        )

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: Returns a dict containing the schema.
        :rtype: dict
        """
        return {
            "type": "object",
            "title": _("Tree"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "name": {"type": "string", "title": _("Tree name")},
                "description": {"type": "string", "title": _("Description")},
                "copyright": {"type": "string", "title": _("Copyright")},
                "license": {"type": "string", "title": _("License")},
                "contributors": {"type": "string", "title": _("Contributors")},
            },
        }

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (
            self.name,
            self.description,
            self.copyright_used,
            self.license_used,
            self.contributors,
        ) = data
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [
            self.name,
            self.description,
            self.copyright_used,
            self.license_used,
            self.contributors,
        ]

    def get_name(self):
        """
        Return the tree name.
        """
        return self.name

    def set_name(self, data):
        """
        Set the tree name.
        """
        self.name = data

    def get_description(self):
        """
        Return the description.
        """
        return self.description

    def set_description(self, data):
        """
        Set the description.
        """
        self.description = data

    def get_copyright(self):
        """
        Return the copyright.
        """
        return self.copyright_used

    def set_copyright(self, data):
        """
        Set the copyright.
        """
        self.copyright_used = data

    def get_license(self):
        """
        Return the license.
        """
        return self.license_used

    def set_license(self, data):
        """
        Set the license.
        """
        self.license_used = data

    def get_contributors(self):
        """
        Return the contributors.
        """
        return self.contributors

    def set_contributors(self, data):
        """
        Set the contributors.
        """
        self.contributors = data
