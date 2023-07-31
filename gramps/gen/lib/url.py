#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
# Copyright (C) 2009-2013  Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2017       Nick Hall
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
Url class for Gramps.
"""

# -------------------------------------------------------------------------
#
# standard python modules
#
# -------------------------------------------------------------------------
from warnings import warn
from urllib.parse import urlparse

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .secondaryobj import SecondaryObject
from .privacybase import PrivacyBase
from .urltype import UrlType
from .const import IDENTICAL, EQUAL, DIFFERENT
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Url for Person/Place/Repository
#
# -------------------------------------------------------------------------
class Url(SecondaryObject, PrivacyBase):
    """
    Contains information related to internet Uniform Resource Locators,
    allowing gramps to store information about internet resources.
    """

    def __init__(self, source=None):
        """Create a new URL instance, copying from the source if present."""
        PrivacyBase.__init__(self, source)
        if source:
            self.path = source.path
            self.desc = source.desc
            self.type = UrlType(source.type)
        else:
            self.path = ""
            self.desc = ""
            self.type = UrlType()

    def serialize(self):
        return (self.private, self.path, self.desc, self.type.serialize())

    def unserialize(self, data):
        (self.private, self.path, self.desc, type_value) = data
        self.type.unserialize(type_value)
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
            "title": _("Url"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "private": {"type": "boolean", "title": _("Private")},
                "path": {"type": "string", "title": _("Path")},
                "desc": {"type": "string", "title": _("Description")},
                "type": UrlType.get_schema(),
            },
        }

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.path, self.desc]

    def is_equivalent(self, other):
        """
        Return if this url is equivalent, that is agrees in type, full path
        name and description, to other.

        :param other: The url to compare this one to.
        :type other: Url
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if (
            self.type != other.type
            or self.get_full_path() != other.get_full_path()
            or self.desc != other.desc
        ):
            return DIFFERENT
        else:
            if self.get_privacy() != other.get_privacy():
                return EQUAL
            else:
                return IDENTICAL

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this url.

        :param acquisition: The url to merge with the present url.
        :type acquisition: Url
        """
        self._merge_privacy(acquisition)

    def set_path(self, path):
        """Set the URL path."""
        self.path = path

    def get_path(self):
        """Return the URL path."""
        return self.path

    def set_description(self, description):
        """Set the description of the URL."""
        self.desc = description

    def get_description(self):
        """Return the description of the URL."""
        return self.desc

    def set_type(self, the_type):
        """
        :param the_type: descriptive type of the Url
        :type the_type: str
        """
        self.type.set(the_type)

    def get_type(self):
        """
        :returns: the descriptive type of the Url
        :rtype: str
        """
        return self.type

    def are_equal(self, other):
        """Deprecated - use :meth:`~.SecondaryObject.is_equal` instead."""

        warn("Use is_equal instead of are_equal", DeprecationWarning, 2)
        return self.is_equal(other)

    def parse_path(self):
        """
        Returns a 6 tuple-based object with the following items:

        ======== ===   =================================
        Property Pos   Meaning
        ======== ===   =================================
        scheme   0     URL scheme specifier
        netloc   1     Network location part
        path     2     Hierarchical path
        params   3     Parameters for last path element
        query    4     Query component
        fragment 5     Fragment identifier
        ======== ===   =================================
        """
        return urlparse(self.path)

    def get_full_path(self):
        """
        Returns a full url, complete with scheme, even if missing from path.
        """
        if self.type == UrlType.EMAIL and not self.path.startswith("mailto:"):
            return "mailto:" + self.path
        elif self.type == UrlType.WEB_FTP and not self.path.startswith("ftp://"):
            return "ftp://" + self.path
        elif self.parse_path().scheme == "":
            return "http://" + self.path
        else:
            return self.path
