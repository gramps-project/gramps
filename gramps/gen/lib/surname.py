#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010       Benny Malengier
# Copyright (C) 2013       Doug Blank <doug.blank@gmail.com>
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
Surname class for Gramps.
"""

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from .secondaryobj import SecondaryObject
from .nameorigintype import NameOriginType
from .const import IDENTICAL, EQUAL, DIFFERENT

#-------------------------------------------------------------------------
#
# Personal Name
#
#-------------------------------------------------------------------------
class Surname(SecondaryObject):
    """
    Provide surname information of a name.

    A person may have more that one surname in his name
    """

    def __init__(self, source=None, data=None):
        """
        Create a new Surname instance, copying from the source if provided.
        By default a surname is created as primary, use set_primary to change
        """
        if source:
            self.surname = source.surname
            self.prefix = source.prefix
            self.primary = source.primary
            self.origintype = NameOriginType(source.origintype)
            self.connector = source.connector
        else:
            self.surname = ""
            self.prefix = ""
            self.primary = True
            self.origintype = NameOriginType()
            self.connector = ""
        if data:
            self.unserialize(data)

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return (self.surname, self.prefix, self.primary,
                self.origintype.serialize(), self.connector)

    def to_struct(self):
        """
        Convert the data held in this object to a structure (eg,
        struct) that represents all the data elements.

        This method is used to recursively convert the object into a
        self-documenting form that can easily be used for various
        purposes, including diffs and queries.

        These structures may be primitive Python types (string,
        integer, boolean, etc.) or complex Python types (lists,
        tuples, or dicts). If the return type is a dict, then the keys
        of the dict match the fieldname of the object. If the return
        struct (or value of a dict key) is a list, then it is a list
        of structs. Otherwise, the struct is just the value of the
        attribute.

        :returns: Returns a struct containing the data of the object.
        :rtype: dict
        """
        return {"_class": "Surname",
                "surname": self.surname,
                "prefix": self.prefix,
                "primary": self.primary,
                "origintype": self.origintype.to_struct(),
                "connector": self.connector}

    @classmethod
    def get_schema(cls):
        return {
            "surname": str,
            "prefix": str,
            "primary": str,
            "origintype": NameOriginType,
            "connector": str
        }

    @classmethod
    def get_labels(cls, _):
        return {
            "_class": _("Surname"),
            "surname": _("Surname"),
            "prefix": _("Prefix"),
            "primary": _("Primary"),
            "origintype": _("Origin type"),
            "connector": _("Connector")
        }

    @classmethod
    def from_struct(cls, struct):
        """
        Given a struct data representation, return a serialized object.

        :returns: Returns a serialized object
        """
        default = Surname()
        return (struct.get("surname", default.surname),
                struct.get("prefix", default.prefix),
                struct.get("primary", default.primary),
                NameOriginType.from_struct(struct.get("origintype", {})),
                struct.get("connector", default.connector))

    def is_empty(self):
        """
        Indicate if the surname is empty.
        """
        return (self.surname == "" and self.prefix == "" and
                self.connector == "")

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        (self.surname, self.prefix, self.primary, origin_type,
         self.connector) = data
        self.origintype = NameOriginType(origin_type)
        return self

    def get_text_data_list(self):
        """
        Return the list of all textual attributes of the object.

        :returns: Returns the list of all textual attributes of the object.
        :rtype: list
        """
        return [self.surname, self.prefix, self.connector,
                str(self.origintype)]

    def is_equivalent(self, other):
        """
        Return if this surname is equivalent, that is agrees in type, surname,
        ..., to other.

        :param other: The surname to compare this name to.
        :type other: Surname
        :returns: Constant indicating degree of equivalence.
        :rtype: int
        """
        # TODO what to do with sort and display?
        if self.get_text_data_list() != other.get_text_data_list() or \
            self.primary != other.primary:
            return DIFFERENT
        else:
            if self.is_equal(other):
                return IDENTICAL
            else:
                return EQUAL

    def merge(self, acquisition):
        """
        Merge the content of acquisition into this surname.

        Lost: primary, surname, prefix, connector, origintype

        :param acquisition: The surname to merge with the present surname.
        :type acquisition: Surname
        """
        pass


    def get_surname(self):
        """
        Return the surname.

        The surname is one of the not given names coming from the parents
        """
        return self.surname

    def set_surname(self, val):
        """
        Set the surname.

        The surname is one of the not given names coming from the parents
        """
        self.surname = val

    def get_prefix(self):
        """
        Return the prefix (or article) of the surname.

        The prefix is not used for sorting or grouping.
        """
        return self.prefix

    def set_prefix(self, val):
        """
        Set the prefix (or article) of the surname.

        Examples of articles would be 'de' or 'van'.
        """
        self.prefix = val

    def set_origintype(self, the_type):
        """Set the origin type of the Surname instance."""
        self.origintype.set(the_type)

    def get_origintype(self):
        """Return the origin type of the Surname instance."""
        return self.origintype

    def set_connector(self, connector):
        """
        Set the connector for the Surname instance. This defines how a
        surname connects to the next surname (eg in Spanish names).
        """
        self.connector = connector

    def get_connector(self):
        """
        Get the connector for the Surname instance. This defines how a
        surname connects to the next surname (eg in Spanish names).
        """
        return self.connector

    def get_primary(self):
        """Return if this surname is the primary surname"""
        return self.primary

    def set_primary(self, primary=True):
        """
        Set if this surname is the primary surname.replace
        Use :class:`~.surnamebase.SurnameBase` to set the primary surname
        via :meth:`~.surnamebase.SurnameBase.set_primary_surname`

        :param primary: primay surname or not
        :type primary: bool
        """
        self.primary = primary
