#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010,2017,2024  Nick Hall
# Copyright (C) 2013            Doug Blank <doug.blank@gmail.com>
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
Tag object for Gramps.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ..const import GRAMPS_LOCALE as glocale
from .tableobj import TableObject

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# Default Tag Color Palette
#
# -------------------------------------------------------------------------
# Color palette designed to work well on both light and dark GTK themes.
# These are medium-saturation colors that provide good contrast and are
# visually distinct from each other.
DEFAULT_TAG_COLORS = [
    "#3584e4",  # Blue - GTK Adwaita blue
    "#c64600",  # Orange/Red
    "#26a269",  # Green - GTK Adwaita green
    "#986803",  # Brown/Yellow
    "#813d9c",  # Purple
    "#1c71d8",  # Bright Blue
    "#e66100",  # Orange
    "#2ec27e",  # Teal/Green
    "#a51d2d",  # Red
    "#1a5fb4",  # Dark Blue
    "#c2185b",  # Pink/Magenta
    "#0d52bf",  # Deep Blue
    "#ff7800",  # Bright Orange
    "#33d17a",  # Light Green
    "#9141ac",  # Purple
]


def get_default_tag_color(db=None):
    """
    Get a default color for a new tag that minimizes collisions.

    This function provides colors that work well on both light and dark
    GTK themes. Colors are selected from a predefined palette, rotating
    by the number of existing tags and skipping colors already in use.

    Colors are stored as #RRGGBB (6-digit hex). Note: older Gramps data
    and XML imports may use the legacy #RRRRGGGGBBBB (12-digit) format.

    :param db: Optional database to check existing tag colors
    :type db: DbBase
    :returns: A hex color string in format #RRGGBB
    :rtype: str
    """
    if db:
        index = db.get_number_of_tags()
    else:
        index = 0

    # Rotate through the color palette
    color = DEFAULT_TAG_COLORS[index % len(DEFAULT_TAG_COLORS)]

    # If database is provided, try to find a color that's not already used
    if db:
        existing_colors = set()
        for tag_handle in db.get_tag_handles():
            tag = db.get_tag_from_handle(tag_handle)
            if tag:
                existing_colors.add(tag.get_color())

        # If the selected color is already used, try the next available one
        if color in existing_colors:
            for i in range(len(DEFAULT_TAG_COLORS)):
                candidate = DEFAULT_TAG_COLORS[(index + i) % len(DEFAULT_TAG_COLORS)]
                if candidate not in existing_colors:
                    color = candidate
                    break

    return color


# -------------------------------------------------------------------------
#
# Tag
#
# -------------------------------------------------------------------------
class Tag(TableObject):
    """
    The Tag record is used to store information about a tag that can be
    attached to a primary object.
    """

    def __init__(self, source=None, db=None):
        """
        Create a new Tag instance, copying from the source if present.

        :param source: A tag used to initialize the new tag
        :type source: Tag
        :param db: Optional database to get default color based on existing tags
        :type db: DbBase
        """

        TableObject.__init__(self, source)

        if source:
            self.__name = source.name
            self.__color = source.color
            self.__priority = source.priority
        else:
            self.__name = ""
            # Use a default color from the palette instead of black
            self.__color = get_default_tag_color(db)
            self.__priority = 0

    def serialize(self):
        """
        Convert the data held in the event to a Python tuple that
        represents all the data elements.

        This method is used to convert the object into a form that can easily
        be saved to a database.

        These elements may be primitive Python types (string, integers),
        complex Python types (lists or tuples, or Python objects. If the
        target database cannot handle complex types (such as objects or
        lists), the database is responsible for converting the data into
        a form that it can use.

        :returns: Returns a python tuple containing the data that should
                  be considered persistent.
        :rtype: tuple
        """
        return (
            self.handle,
            self.__name,
            self.__color,
            self.__priority,
            self.change,
        )

    def unserialize(self, data):
        """
        Convert the data held in a tuple created by the serialize method
        back into the data in a Tag structure.

        :param data: tuple containing the persistent data associated with the
                     object
        :type data: tuple
        """
        (
            self.handle,
            self.__name,
            self.__color,
            self.__priority,
            self.change,
        ) = data
        return self

    def get_object_state(self):
        """
        Get the current object state as a dictionary.

        We override this method to handle the `name`, `color` and `priority`
        properties.
        """
        attr_dict = super().get_object_state()
        attr_dict["name"] = self.__name
        attr_dict["color"] = self.__color
        attr_dict["priority"] = self.__priority
        return attr_dict

    def set_object_state(self, attr_dict):
        """
        Set the current object state using information provided in the given
        dictionary.

        We override this method to handle the `name`, `color` and `priority`
        properties.
        """
        self.__name = attr_dict.pop("name")
        self.__color = attr_dict.pop("color")
        self.__priority = attr_dict.pop("priority")
        super().set_object_state(attr_dict)

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
                "handle": {
                    "type": "string",
                    "maxLength": 50,
                    "title": _("Handle"),
                },
                "name": {"type": "string", "title": _("Name")},
                "color": {
                    "type": "string",
                    "maxLength": 13,
                    "title": _("Color"),
                },
                "priority": {
                    "type": "integer",
                    "minimum": 0,
                    "title": _("Priority"),
                },
                "change": {"type": "integer", "title": _("Last changed")},
            },
        }

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.__name]

    def is_empty(self):
        """
        Return True if the Tag is an empty object (no values set).

        :returns: True if the Tag is empty
        :rtype: bool
        """
        return not self.__name

    def are_equal(self, other):
        """
        Return True if the passed Tag is equivalent to the current Tag.

        :param other: Tag to compare against
        :type other: Tag
        :returns: True if the Tags are equal
        :rtype: bool
        """
        if other is None:
            other = Tag()

        if (
            self.__name != other.name
            or self.__color != other.color
            or self.__priority != other.priority
        ):
            return False
        return True

    def set_name(self, name):
        """
        Set the name of the Tag to the passed string.

        :param name: Name to assign to the Tag
        :type name: str
        """
        self.__name = name

    def get_name(self):
        """
        Return the name of the Tag.

        :returns: Name of the Tag
        :rtype: str
        """
        return self.__name

    name = property(get_name, set_name, None, "Returns or sets name of the tag")

    def set_color(self, color):
        """
        Set the color of the Tag to the passed string.

        The string is of the format #rrrrggggbbbb.

        :param color: Color to assign to the Tag
        :type color: str
        """
        self.__color = color

    def get_color(self):
        """
        Return the color of the Tag.

        :returns: Returns the color of the Tag
        :rtype: str
        """
        return self.__color

    color = property(get_color, set_color, None, "Returns or sets color of the tag")

    def set_priority(self, priority):
        """
        Set the priority of the Tag to the passed integer.

        The lower the value the higher the priority.

        :param priority: Priority to assign to the Tag
        :type priority: int
        """
        self.__priority = priority

    def get_priority(self):
        """
        Return the priority of the Tag.

        :returns: Returns the priority of the Tag
        :rtype: int
        """
        return self.__priority

    priority = property(
        get_priority, set_priority, None, "Returns or sets priority of the tag"
    )
