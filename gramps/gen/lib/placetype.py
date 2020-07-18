#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
# Copyright (C) 2015,2017  Nick Hall
# Copyright (C) 2019       Paul Culley
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
Place Type class for Gramps
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .datebase import DateBase
from .citationbase import CitationBase
from .secondaryobj import SecondaryObject
from .placegrouptype import PlaceGroupType as p_g
from .const import IDENTICAL, EQUAL, DIFFERENT
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# _T_ is a gramps-defined keyword -- see po/update_po.py and po/genpot.sh
def _T_(value):  # enable deferred translations (see Python docs 22.1.3.4)
    return value


DM_NAME = 0  # index into DATAMAP tuple
DM_NATIVE = 1
DM_CTRY = 2
DM_COLOR = 3
DM_GRP = 4
DM_TRANS = 5


# -------------------------------------------------------------------------
#
# Place Type
#
# -------------------------------------------------------------------------
class PlaceType(CitationBase, DateBase, SecondaryObject):
    """
    Place Type class.

    This class is for keeping information about place types.
    Within the XML and db, the place type holds an ID and a default text string
    to be used if no other addon data is available.

    Place Types are mostly defined via addons/plugins.  During initialization,
    these are read in and cached in the DATAMAP structure in this class.

    The place type DATAMAP is referenced via the ID.
        The ID must be unique, but is not constructed in the usual way.
        * For original Gramps place types the ID is the XML string of the
          type.
        * For types created from an external system, (e.g. GOV types) the
          ID should be clearly identifiable as belonging to that system.
          For GOV we will use GOV_xxx where xxx is the number assigned to the
          GOV place type
        * For manually entered fully custom types, we will use the initially
          entered name string, preceded by 'CUS_' to make it unique.
    Because the type names can now be modified in the GUI as well as hidden
    from menus and have groups modified, the DATAMAP dict is now modified in
    place when changes are made and new types are added.

    As a consequence, the place type menus in the GUI combobox are built
    as needed at runtime.
    """

    CUSTOM = "CUSTOM"  # 0 original value
    UNKNOWN = "Unknown"  # -1 original value
    #     STREET = "Street"       # 7
    #     NUMBER = "Number"       # 20
    _DEFAULT = UNKNOWN
    _CUSTOM = CUSTOM

    # The data map (dict) contains a tuple with key as ID (str)
    #   name
    #   native name
    #   countries
    #   color
    #   probable group (used for legacy XML import)
    #   gettext method (or None if standard method)

    DATAMAP = {
        UNKNOWN: (
            _T_("Unknown"),
            "Unknown",
            "!!",
            "#0000FFFF0000",
            p_g(p_g.PLACE),
            None,
        ),
        CUSTOM: ("", "", "", "#0000FFFF0000", p_g(p_g.NONE), None),
    }

    str_to_pt_id: dict[str, str] = (
        {}
    )  # used for finding type from imported place type value

    def __init__(self, source=None, **kwargs):
        """
        Create a new PlaceType instance, copying from the source if present.

        :param source: source data to initialize the type
        :type source: PlaceType, or int or string or tuple
        """
        self.pt_id = PlaceType.UNKNOWN
        # pt_id is prefixed with nothing for legacy Gramps,
        # 'CUS_' for custom, 'GOV_' for GOV types, 'GB_' for Great Britain etc.
        # The rest is usually the translatable name, or the GOV number

        self.name = _T_("Unknown")
        # default name, for use when on plugin is available

        DateBase.__init__(self)
        CitationBase.__init__(self)
        if source:
            self.set(source)
        for key in kwargs:
            if key in ["pt_id", "name", "date", "citation_list"]:
                setattr(self, key, kwargs[key])
            else:
                raise AttributeError("PlaceType does not have property '%s'" % key)

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.

        :returns: Returns the serialized tuple of data.
        :rtype: tuple
        """
        return (
            self.pt_id,
            self.name,
            DateBase.serialize(self),
            CitationBase.serialize(self),
        )

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.

        :param data: serialized tuple of data from an object.
        :type data: tuple
        :returns: Returns the PlaceType containing the unserialized data.
        :rtype: PlaceType
        """
        (self.pt_id, self.name, date, citation_list) = data
        DateBase.unserialize(self, date)
        CitationBase.unserialize(self, citation_list)
        return self

    @classmethod
    def get_schema(cls):
        """
        Returns the JSON Schema for this class.

        :returns: Returns a dict containing the schema.
        :rtype: dict
        """
        from .date import Date

        return {
            "type": "object",
            "title": _("Place Type"),
            "properties": {
                "_class": {"enum": [cls.__name__]},
                "pt_id": {"type": "string", "maxLength": 50, "title": _("ID")},
                "name": {"type": "string", "maxLength": 50, "title": _("Name")},
                "date": {
                    "oneOf": [{"type": "null"}, Date.get_schema()],
                    "title": _("Date"),
                },
                "citation_list": {
                    "type": "array",
                    "title": _("Citations"),
                    "items": {"type": "string", "maxLength": 50},
                },
            },
        }

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.name, self.__str__()]

    @staticmethod
    def get_text_data_child_list():
        """
        Return the list of child objects that may carry textual data.

        :returns: list of child objects that may carry textual data.
        :rtype: list
        """
        return []

    def get_referenced_handles(self):
        """
        Return the list of (classname, handle) tuples for all directly
        referenced primary objects.

        :returns: Returns the list of (classname, handle) tuples for referenced
                  objects.
        :rtype: list
        """
        return self.get_referenced_citation_handles()

    @staticmethod
    def get_handle_referents():
        """
        Return the list of child objects which may, directly or through their
        children, reference primary objects.

        :returns: Returns the list of objects referencing primary objects.
        :rtype: list
        """
        return []

    def set(self, value):
        """Set the properties from the passed in value."""
        if isinstance(value, self.__class__):
            self.pt_id = value.pt_id
            self.name = value.name
            self.date = value.date
            self.citation_list = value.citation_list
        elif isinstance(value, tuple):
            self.pt_id, name = value
            tup = self.DATAMAP.get(self.pt_id, None)
            if tup and self.pt_id != self.CUSTOM:  # an already known type
                self.name = tup[DM_NAME]
            else:  # a new custom type
                self.name = name
        elif isinstance(value, str):
            # value is assumed to be the pt_id
            tup = self.DATAMAP.get(value, None)
            if tup:  # an already known type
                self.pt_id = value
                self.name = tup[DM_NAME]
                return
            # but value might be a poorly typed actual type
            id_ = value.capitalize()
            tup = self.DATAMAP.get(id_, None)
            if tup:  # an already known type
                self.pt_id = id_
                self.name = tup[DM_NAME]
            else:  # a new custom type
                self.pt_id = self.CUSTOM
                self.name = value

    def __eq__(self, other):
        """
        When comparing the objects, absolute equality.
        When comparing self to string, only checks type equality.
        """
        if isinstance(other, str):
            if self.pt_id == self.CUSTOM:
                return self.name == other
            else:
                return self.pt_id == other
        return self.is_equal(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_equivalent(self, other):
        """
        Return if this PlaceType is equivalent, that is agrees in type and
        date, to other.

        :param other: The PlaceType to compare this one to.
        :type other: PlaceType
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        if (
            self.pt_id != other.pt_id
            or self.name != other.name
            or self.date != other.date
        ):
            return DIFFERENT
        if self.is_equal(other):
            return IDENTICAL
        return EQUAL

    def is_same(self, other):
        """
        Compares only the type to other, date and citation are ignored.
        """
        if self.pt_id == self.CUSTOM == other.pt_id:
            return self.name == other.name
        return self.pt_id == other.pt_id

    def str(self, locale=glocale, expand=False):
        """
        return the name of the placetype appropriate to the defined locale.

        Note: locale is used to provide a language information, in reports
        only.  The actual language used is taken from the locale.
        If the translation is not found in the addon, the actual locale
        is used.  Example from typical report:

        loc = self.set_locale(menu.get_option_by_name('trans').get_value())
        ...
        printstr = placetype.str(locale=loc)

        :param locale: the backup locale
        :type locale: GrampsLocale instance
        :returns: display string of the place type
        :rtype: str
        """
        if self.pt_id in self.DATAMAP:
            native = self.DATAMAP[self.pt_id][DM_NATIVE]
            transfunc = self.DATAMAP[self.pt_id][DM_TRANS]
        else:
            native = transfunc = None
        if transfunc:
            name = transfunc(self.name, locale=locale, pt_id=self.pt_id)
        elif locale is None:  # use the standard GLOCALE sgettext
            name = _(self.name)
        else:  # use the defined locale
            name = locale.translation.sgettext(self.name)
        if expand and native and native not in name:  # and '(' not in name
            # translators: used to output place types
            name = _("{name}({native})").format(name=name, native=native)
        return name

    def __str__(self):
        """return the name of the placetype appropriate to the current
        language

        :returns: display string of the place type
        :rtype: str
        """
        return self.str()

    def is_empty(self):
        """Determine if this PlaceType is empty (not changed from initial
        value)
        """
        return (
            self.pt_id == PlaceType.UNKNOWN
            and self.date.is_empty()
            and not self.citation_list
        )

    def is_custom(self):
        """This type is a temporary value assigned to indicate that the type
        is stored as a string in self.name

        :returns: True if the temp value is in use.
        :rtype: bool
        """
        return self.pt_id == self.CUSTOM

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this PlaceType.

        Lost: type, date of acquisition.

        :param acquisition: the PlaceType to merge with.
        :type acquisition: PlaceType
        """
        self._merge_citation_list(acquisition)

    def get_color(self):
        """
        Gets the color

        :returns: the place type color (hex string).
        :rtype: str
        """
        if self.pt_id in self.DATAMAP:
            return self.DATAMAP[self.pt_id][DM_COLOR]
        return "#0000FFFF0000"

    def get_name(self):
        """
        Gets the name

        :returns: the place type name.
        :rtype: str
        """
        return self.name

    def get_native(self):
        """
        Gets the native name

        :returns: the place type native name.
        :rtype: str
        """
        if self.pt_id in self.DATAMAP:
            return self.DATAMAP[self.pt_id][DM_NATIVE]
        return ""

    def get_probable_group(self):
        """
        Gets the probable group for a given place type.
        Used for XML import of legacy Gramps and other imports

        :returns: the place group.
        :rtype: PlaceGroupType (GrampsType)
        """
        if self.pt_id in self.DATAMAP:
            return self.DATAMAP[self.pt_id][DM_GRP]
        name = self.name.lower()
        if name in self.str_to_pt_id:
            return self.DATAMAP[self.str_to_pt_id[name]][DM_GRP]
        return p_g(p_g.NONE)

    def get_countries(self):
        """
        Gets the countries string

        :returns: the place type countries.
        :rtype: str
        """
        if self.pt_id in self.DATAMAP:
            return self.DATAMAP[self.pt_id][DM_CTRY]
        return "##"  # Custom

    @classmethod
    def register_placetype(cls, pt_id, data, category):
        """
        This supports plugins/addons providing new placetypes.
        Store the new or updated entry in our datamap.

        The pt_id must be a unique identifier if the entry is to be
        completely new.  If the pt_id is NOT unique, the data must match
        already existing data.  This would be used to allow 'sharing' of
        common (legacy) types with additional categories.

        The pt_id should consist of a prefix (GOV_, CUS_, DE_, GB_ etc.)
        that suggests the source of the type with the remainder of the pt_id
        readable, probably the type name in English or the native
        language where English is not clear.  GOV types should use the number
        of the type (GOV_49).  The common (legacy) types have no prefix and
        consist of the original XML name, to allow easier db and XML upgrades.

        The 'data' field is a tuple with the following elements:
           translatable name (str)
           native name (str)
           color for map markers (hex color string)
           probable group (used for legacy XML import) (PlaceGroupType)
           gettext method (or None if standard method)

        The 'category' field is usually a country code but can also be
        The special '!!' code to specify Gramps legacy 'Common'
        The special '##' code to specify 'Custom'

        :param pt_id: the PlaceType pt_id
        :type pt_id: str
        :param data: a tuple of data as indicated above
        :type data: tuple
        :param category: the category to show this entry under in the menu
        :type category: str
        :returns: True if already found in datamap, False if not
        :rtype: bool
        """
        if pt_id in cls.DATAMAP:
            old_data = list(cls.DATAMAP[pt_id])
            if category not in old_data[DM_CTRY]:
                old_data[DM_CTRY] += " " + category
                cls.DATAMAP[pt_id] = tuple(old_data)
            return True
        (name, native, color, group, transfunc) = data
        new_data = (name, native, category, color, group, transfunc)
        cls.DATAMAP[pt_id] = new_data
        return False

    @classmethod
    def update_name_map(cls):
        """
        Create a name to pt_id dict from the DATAMAP
        the translated names SHOULD be unique, otherwise you might get an
        unexpected placetype pt_id.  Names are stored in lower case for
        case insensitive search.
        """
        cls.str_to_pt_id = {}
        # include untranslated names
        for pt_id, tup in cls.DATAMAP.items():
            name = tup[DM_NAME].lower()
            if name not in cls.str_to_pt_id:
                cls.str_to_pt_id[name] = pt_id
        # and translated names, if they are not already there.
        for pt_id, tup in cls.DATAMAP.items():
            transfunc = tup[DM_TRANS]
            if transfunc:
                name = transfunc(tup[DM_NAME], pt_id=pt_id).lower()
            else:
                name = _(tup[DM_NAME]).lower()
            if name not in cls.str_to_pt_id:
                cls.str_to_pt_id[name] = pt_id


PlaceType.update_name_map()
