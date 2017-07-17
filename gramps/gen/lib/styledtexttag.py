#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Zsolt Foldvari
# Copyright (C) 2013  Doug Blank <doug.blank@gmail.com>
# Copyright (C) 2017  Nick Hall
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

"Provide formatting tag definition for StyledText."

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .styledtexttagtype import StyledTextTagType
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# StyledTextTag class
#
#-------------------------------------------------------------------------
class StyledTextTag:
    """Hold formatting information for :py:class:`.StyledText`.

    :py:class:`StyledTextTag` is a container class, it's attributes are
    directly accessed.

    :ivar name: Type (or name) of the tag instance. E.g. 'bold', etc.
    :type name: :py:class:`.StyledTextTagType` instace
    :ivar value: Value of the tag. E.g. color hex string for font color, etc.
    :type value: str or None
    :ivar ranges: Pointer pairs into the string, where the tag applies.
    :type ranges: list of (int(start), int(end)) tuples.

    """
    def __init__(self, name=None, value=None, ranges=None):
        """Setup initial instance variable values.

        .. note:: Since :py:class:`.GrampsType` supports the instance
                  initialization with several different base types, please note
                  that ``name`` parameter can be int, str, unicode, tuple,
                  or even another :py:class:`.StyledTextTagType` instance.
        """
        self.name = StyledTextTagType(name)
        self.value = value
        if ranges is None:
            self.ranges = []
        else:
            # Current use of StyledTextTag is such that a shallow copy suffices.
            self.ranges = ranges

    def serialize(self):
        """Convert the object to a serialized tuple of data.

        :return: Serialized format of the instance.
        :rtype: tuple

        """
        return (self.name.serialize(), self.value, self.ranges)

    def unserialize(self, data):
        """Convert a serialized tuple of data to an object.

        :param data: Serialized format of instance variables.
        :type data: tuple

        """
        (the_name, self.value, self.ranges) = data

        self.name = StyledTextTagType()
        self.name.unserialize(the_name)
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
            "title": _("Tag"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "name": StyledTextTagType.get_schema(),
                "value": {"type": ["null", "string", "integer"],
                          "title": _("Value")},
                "ranges": {"type": "array",
                           "items": {"type": "array",
                                     "items": {"type": "integer"},
                                     "minItems": 2,
                                     "maxItems": 2},
                           "title": _("Ranges")}
            }
        }
