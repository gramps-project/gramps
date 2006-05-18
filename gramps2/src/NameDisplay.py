#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2005  Donald N. Allingham
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

"""
Class handling language-specific displaying of names.
"""

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from RelLib import Name

#-------------------------------------------------------------------------
#
# Constants
#
#-------------------------------------------------------------------------
_FIRSTNAME = 4
_SURNAME   = 5
_SUFFIX    = 6
_TITLE     = 7
_TYPE      = 8
_PREFIX    = 9
_PATRONYM  = 10
_SNAME     = 11
_GROUP     = 12
_SORT      = 13
_DISPLAY   = 14

#-------------------------------------------------------------------------
#
# NameDisplay class
#
#-------------------------------------------------------------------------
class NameDisplay:
    """
    Base class for displaying of Name instances.
    """
    def __init__(self,use_upper=False):
        """
        Creates a new NameDisplay class.

        @param use_upper: True indicates that the surname should be
        displayed in upper case.
        @type use_upper: bool
        """
        self.force_upper = use_upper
        
        self.fn_array = [
            self._lnfn, self._lnfn, self._fnln,
            self._ptfn, self._empty ]
        
        self.raw_fn_array = (
            self._lnfn_raw, self._lnfn_raw, self._fnln_raw,
            self._ptfn_raw, self._empty_raw )

    def use_upper(self,upper):
        """
        Changes the NameDisplay class to enable or display the displaying
        of surnames in upper case.
        
        @param upper: True indicates that the surname should be
        displayed in upper case.
        @type upper: bool
        """
        self.force_upper = upper

    def sort_string(self,name):
        return u"%-25s%-30s%s" % (name.surname,name.first_name,name.suffix)

    def sorted(self,person):
        """
        Returns a text string representing the L{RelLib.Person} instance's
        L{Name} in a manner that should be used for displaying a sorted
        name.

        @param person: L{RelLib.Person} instance that contains the
        L{Name} that is to be displayed. The primary name is used for
        the display.
        @type person: L{RelLib.Person}
        @returns: Returns the L{RelLib.Person} instance's name
        @rtype: str
        """
        name = person.get_primary_name()
        if name.sort_as == Name.FNLN:
            return self._fnln(name)
        elif name.sort_as == Name.PTFN:
            return self._ptfn(name)
        elif name.sort_as == Name.FN:
            return name.first_name
        else:
            return self._lnfn(name)

    def _empty(self,name):
        return name.first_name

    def _empty_raw(self,raw_data):
        return raw_data[_FIRSTNAME]

    def _ptfn(self,name):
        """
        Prints the Western style first name, last name style.
        Typically this is::

           SurnamePrefix Patronymic SurnameSuffix, FirstName
        """

        first = name.first_name

        if self.force_upper:
            last = name.patronymic.upper()
        else:
            last = name.patronymic
            
        if name.suffix:
            if name.prefix:
                return "%s %s %s, %s" % (name.prefix, last, name.suffix, first)
            else:
                return "%s %s, %s" % (last, name.suffix, first)
        else:
            if name.prefix:
                return "%s %s, %s" % (name.prefix, last, first)
            else:
                return "%s, %s" % (last, first)

    def _ptfn_raw(self,raw_data):
        """
        Prints the Western style first name, last name style.
        Typically this is::

           SurnamePrefix Patronymic SurnameSuffix, FirstName
        """

        first = raw_data[_FIRSTNAME]
        suffix = raw_data[_SUFFIX]
        prefix = raw_data[_PREFIX]
        patronymic = raw_data[_PATRONYM]

        if self.force_upper:
            last = patronymic.upper()
        else:
            last = patronymic
            
        if suffix:
            if prefix:
                return "%s %s %s, %s" % (prefix, last, suffix, first)
            else:
                return "%s %s, %s" % (last, suffix, first)
        else:
            if prefix:
                return "%s %s, %s" % (prefix, last, first)
            else:
                return "%s, %s" % (last, first)
        
    def _fnln(self,name):
        """
        Prints the Western style first name, last name style.
        Typically this is::

           FirstName Patronymic SurnamePrefix Surname SurnameSuffix
        """
        first = name.first_name

        if name.patronymic:
            first = "%s %s" % (first, name.patronymic)

        if self.force_upper:
            last = name.surname.upper()
        else:
            last = name.surname
            
        if name.suffix:
            if name.prefix:
                return "%s %s %s, %s" % (first, name.prefix, last, name.suffix)
            else:
                return "%s %s, %s" % (first, last, name.suffix)
        else:
            if name.prefix:
                return "%s %s %s" % (first, name.prefix, last)
            else:
                return "%s %s" % (first, last)

    def _fnln_raw(self,raw_data):
        """
        Prints the Western style first name, last name style.
        Typically this is::

           FirstName Patronymic SurnamePrefix Surname SurnameSuffix
        """
        first = raw_data[_FIRSTNAME]
        surname = raw_data[_SURNAME]
        suffix = raw_data[_SUFFIX]
        prefix = raw_data[_PREFIX]
        patronymic = raw_data[_PATRONYM]

        if patronymic:
            first = "%s %s" % (first, patronymic)

        if self.force_upper:
            last = surname.upper()
        else:
            last = surname
            
        if suffix:
            if prefix:
                return "%s %s %s, %s" % (first, prefix, last, suffix)
            else:
                return "%s %s, %s" % (first, last, suffix)
        else:
            if prefix:
                return "%s %s %s" % (first, prefix, last)
            else:
                return "%s %s" % (first, last)

    def _lnfn(self,name):
        """
        Prints the Western style last name, first name style.
        Typically this is::

            SurnamePrefix Surname, FirstName Patronymic SurnameSuffix
        """
        if self.force_upper:
            last = name.surname.upper()
        else:
            last = name.surname

        if last:
            last += ","

        return " ".join([x for x in [name.prefix, last, name.first_name,
                                     name.patronymic, name.suffix]])

    def _lnfn_raw(self,raw_data):
        """
        Prints the Western style last name, first name style.
        Typically this is::

            SurnamePrefix Surname, FirstName Patronymic SurnameSuffix
        """
        if self.force_upper:
            last = raw_data[_SURNAME].upper()
        else:
            last = raw_data[_SURNAME]

        if last:
            last += ","

        return " ".join([x for x in
                         [raw_data[_PREFIX], last, raw_data[_FIRSTNAME],
                          raw_data[_PATRONYM], raw_data[_SUFFIX]]])
    
    def sorted_name(self,name):
        """
        Returns a text string representing the L{Name} instance
        in a manner that should be used for displaying a sorted
        name.

        @param name: L{Name} instance that is to be displayed.
        @type name: L{Name}
        @returns: Returns the L{Name} string representation
        @rtype: str
        """
        return self.fn_array[name.sort_as](name)
        #return self.fn_array.get(name.sort_as,self._lnfn)(name)

    def raw_sorted_name(self,raw_data):
        """
        Returns a text string representing the L{Name} instance
        in a manner that should be used for displaying a sorted
        name.

        @param name: L{Name} instance that is to be displayed.
        @type name: L{Name}
        @returns: Returns the L{Name} string representation
        @rtype: str
        """
        return self.raw_fn_array[raw_data[_SORT]](raw_data)

    def display_given(self,person):
        name = person.get_primary_name()
        if name.patronymic:
            return "%s %s" % (name.first_name, name.patronymic)
        else:
            return name.first_name

    def display(self,person):
        """
        Returns a text string representing the L{RelLib.Person} instance's
        L{Name} in a manner that should be used for normal displaying.

        @param person: L{RelLib.Person} instance that contains the
        L{Name} that is to be displayed. The primary name is used for
        the display.
        @type person: L{RelLib.Person}
        @returns: Returns the L{RelLib.Person} instance's name
        @rtype: str
        """
        name = person.get_primary_name()
        if name.display_as == Name.LNFN:
            return self._lnfn(name)
        else:
            return self._fnln(name)

    def display_formal(self,person):
        """
        Returns a text string representing the L{RelLib.Person} instance's
        L{Name} in a manner that should be used for normal displaying.

        @param person: L{RelLib.Person} instance that contains the
        L{Name} that is to be displayed. The primary name is used for
        the display.
        @type person: L{RelLib.Person}
        @returns: Returns the L{RelLib.Person} instance's name
        @rtype: str
        """
        name = person.get_primary_name()
        if name.display_as == Name.LNFN:
            return self._lnfn(name)
        else:
            return self._fnln(name)

    def display_name(self,name):
        """
        Returns a text string representing the L{Name} instance
        in a manner that should be used for normal displaying.

        @param name: L{Name} instance that is to be displayed.
        @type name: L{Name}
        @returns: Returns the L{Name} string representation
        @rtype: str
        """
        if name == None:
            return ""
        elif name.display_as == Name.LNFN:
            return self._lnfn(name)
        elif name.display_as == Name.PTFN:
            return self._ptfn(name)
        else:
            return self._fnln(name)

    def name_grouping(self,db,person):
        return self.name_grouping_name(db,person.primary_name)


    sort_field = (Name.get_surname, Name.get_surname,
                  Name.get_first_name, Name.get_patronymic,
                  Name.get_first_name)

    def name_grouping_name(self,db,pn):
        if pn.group_as:
            return pn.group_as
        sv = pn.sort_as
        if sv <= Name.LNFN:
            return db.get_name_group_mapping(pn.surname)
        elif sv == Name.PTFN:
            return db.get_name_group_mapping(pn.patronymic)
        else:
            return db.get_name_group_mapping(pn.first_name)

displayer = NameDisplay()
