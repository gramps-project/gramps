#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2010  Benny Malengier
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
SurnameBase class for Gramps.
"""

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from .surname import Surname
from .const import IDENTICAL, EQUAL
from ..const import GRAMPS_LOCALE as glocale

_ = glocale.translation.gettext


# -------------------------------------------------------------------------
#
# SurnameBase classes
#
# -------------------------------------------------------------------------
class SurnameBase:
    """
    Base class for surname-aware objects.
    """

    def __init__(self, source=None):
        """
        Initialize a SurnameBase.

        If the source is not None, then object is initialized from values of
        the source object.

        :param source: Object used to initialize the new object
        :type source: SurnameBase
        """
        self.surname_list = list(map(Surname, source.surname_list)) if source else []

    def serialize(self):
        """
        Convert the object to a serialized tuple of data.
        """
        return [surname.serialize() for surname in self.surname_list]

    def unserialize(self, data):
        """
        Convert a serialized tuple of data to an object.
        """
        self.surname_list = [Surname().unserialize(item) for item in data]

    def add_surname(self, surname):
        """
        Add the :class:`~.surname.Surname` instance to the object's
        list of surnames.

        :param surname: :class:`~.surname.Surname` instance to add to the
                        object's address list.
        :type address: list
        """
        self.surname_list.append(surname)

    def remove_surname(self, surname):
        """
        Remove the specified :class:`~.surname.Surname` instance from the
        surname list.

        If the instance does not exist in the list, the operation has
        no effect.

        :param surname: :class:`~.surname.Surname` instance to remove
                        from the list
        :type surname: :class:`~.surname.Surname`

        :returns: True if the surname was removed, False if it was not in the
                  list.
        :rtype: bool
        """
        if surname in self.surname_list:
            self.surname_list.remove(surname)
            return True
        else:
            return False

    def get_surname_list(self):
        """
        Return the list of :class:`~.surname.Surname` instances
        associated with the object.

        :returns: Returns the list of :class:`~.surname.Surname` instances
        :rtype: list
        """
        return self.surname_list

    def set_surname_list(self, surname_list):
        """
        Assign the passed list to the object's list of
        :class:`~.surname.Surname` instances.

        :param surname_list: List of :class:`~.surname.Surname` instances to be
                             associated with the object
        :type surname_list: list
        """
        self.surname_list = surname_list

    def get_primary_surname(self):
        """
        Return the surname that is the primary surname

        :returns: Returns the surname instance that is the primary surname. If
                  primary not set, and there is a surname, the first surname is
                  given, if no surnames, None is returned
        :rtype: :class:`~.surname.Surname` or None
        """
        for surname in self.surname_list:
            if surname.primary:
                return surname
        if self.surname_list:
            return self.surname_list[0]
        else:
            # self healing, add a surname to this object and return it
            self.set_surname_list([Surname()])
            return self.surname_list[0]

    def set_primary_surname(self, surnamenr=0):
        """
        Set the surname with surnamenr in the surname list as primary surname
        Counting starts at 0
        """
        assert isinstance(
            surnamenr, int
        ), "Surname.set_primary_surname requires integer"
        if surnamenr >= len(self.surname_list):
            return
        for surname in self.surname_list:
            surname.set_primary(False)
        self.surname_list[surnamenr].set_primary(True)

    def _merge_surname_list(self, acquisition):
        """
        Merge the list of surname from acquisition with our own.
        This method is normally only called when surnames are equal, if they
        are different, the merge code should fall back to storing an
        alternate name. For completeness, the code is present nevertheless.

        :param acquisition: the surname list of this object will be merged with
                            the current surname list.
        :type acquisition: SurnameBase
        """
        surname_list = self.surname_list[:]
        for addendum in acquisition.get_surname_list():
            for surname in surname_list:
                equi = surname.is_equivalent(addendum)
                if equi == IDENTICAL:
                    break
                elif equi == EQUAL:
                    # This should normally never happen, an alternate name
                    # should be added
                    surname.merge(addendum)
                    break
            else:
                self.surname_list.append(addendum)

    def get_surname(self):
        """
        Return a fully formatted surname utilizing the surname_list
        """
        totalsurn = ""
        for surn in self.surname_list:
            partsurn = surn.get_surname()
            if surn.get_prefix():
                fsurn = _("%(first)s %(second)s") % {
                    "first": surn.get_prefix(),
                    "second": partsurn,
                }
            else:
                fsurn = partsurn
            fsurn = fsurn.strip()
            if surn.get_connector():
                fsurn = _("%(first)s %(second)s") % {
                    "first": fsurn,
                    "second": surn.get_connector(),
                }
            fsurn = fsurn.strip()
            totalsurn = _("%(first)s %(second)s") % {
                "first": totalsurn,
                "second": fsurn,
            }
        return totalsurn.strip()

    def get_primary(self):
        """
        Return a fully formatted primary surname
        """
        primary = self.get_primary_surname()
        partsurn = primary.get_surname()
        if primary.get_prefix():
            fsurn = _("%(first)s %(second)s") % {
                "first": primary.get_prefix(),
                "second": partsurn,
            }
        else:
            fsurn = partsurn
        return fsurn.strip()

    def get_upper_surname(self):
        """Return a fully formatted surname capitalized"""
        return self.get_surname().upper()

    def get_surnames(self):
        """
        Return a list of surnames (no prefix or connectors)
        """
        surnl = []
        for surn in self.surname_list:
            realsurn = surn.get_surname()
            if realsurn:
                surnl.append(realsurn)
        return surnl

    def get_prefixes(self):
        """
        Return a list of prefixes
        """
        prefixl = []
        for surn in self.surname_list:
            prefix = surn.get_prefix()
            if prefix:
                prefixl.append(prefix)
        return prefixl

    def get_connectors(self):
        """
        Return a list of surnames (no prefix or connectors)
        """
        connl = []
        for surn in self.surname_list:
            conn = surn.get_connector()
            if conn:
                connl.append(conn)
        return connl
