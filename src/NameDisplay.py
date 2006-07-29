#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2006  Donald N. Allingham
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
import Config

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
_CALL      = 15

#-------------------------------------------------------------------------
#
# NameDisplay class
#
#-------------------------------------------------------------------------
class NameDisplay:
    """
    Base class for displaying of Name instances.
    """

    # FIXME: Is this used anywhere? I cannot see that it is.
    sort_field = (Name.get_surname, Name.get_surname,
                  Name.get_first_name, Name.get_patronymic,
                  Name.get_first_name)

    def __init__(self,use_upper=False):
        """
        Creates a new NameDisplay class.

        @param use_upper: True indicates that the surname should be
        displayed in upper case.
        @type use_upper: bool
        """

        ##self.force_upper = use_upper
        
        self.CUSTOM_FORMATS = []
        self.gramps_format = Name.LNFN
        self.fn_array = {}
        self.raw_fn_array = {}
        self.set_format_fn()
        
        default_idx = Config.get(Config.NAME_FORMAT)
        if default_idx == 0:
            default_idx = Name.LNFN        
        self.set_format_default(default_idx)

    def _format_fn(self,fmt_str):
        return lambda x: self.format_str(x,fmt_str)
    
    def _format_raw_fn(self,fmt_str):
        return lambda x: self.format_str_raw(x,fmt_str)
    
    def set_format_fn(self):
        self.fn_array.clear()
        self.raw_fn_array.clear()
        # Add standard formats to mappings
        for number,name,fmt_str in Name.STANDARD_FORMATS:
            self.fn_array[number] = self._format_fn(fmt_str)
            self.raw_fn_array[number] = self._format_raw_fn(fmt_str)
        # Add custom formats to the mappings
        for number,name,fmt_str,act in self.CUSTOM_FORMATS:
            if act:
                self.fn_array[number] = self._format_fn(fmt_str)
                self.raw_fn_array[number] = self._format_raw_fn(fmt_str)
                
        self.set_format_default(self.gramps_format)
        
    def set_format_default(self,idx):
        # Add mappings for the gramps-prefs format
        if not self.fn_array.has_key(idx):
            idx = Name.LNFN
            # this should not happen if the default is kept in the db
            
        self.gramps_format = idx
        self.fn_array[0] = self.fn_array[idx]
        self.raw_fn_array[0] = self.raw_fn_array[idx]

    def register_custom_formats(self,formats):
        self.CUSTOM_FORMATS = formats[:]
        self.set_format_fn()
        
    def update_custom_formats(self,num,name,str,act):
        i = 0
        while (i < len(self.CUSTOM_FORMATS) and 
               self.CUSTOM_FORMATS[i][0] != num):
            i += 1
        
        try:
            self.CUSTOM_FORMATS[i] = (num,name,str,act)
        except IndexError:
            self.CUSTOM_FORMATS.append((num,name,str,act))
            
        self.set_format_fn()

    ##def use_upper(self,upper):
        ##"""
        ##Changes the NameDisplay class to enable or display the displaying
        ##of surnames in upper case.
        
        ##@param upper: True indicates that the surname should be
        ##displayed in upper case.
        ##@type upper: bool
        ##"""
        ##self.force_upper = upper

    def sort_string(self,name):
        return u"%-25s%-30s%s" % (name.surname,name.first_name,name.suffix)

    ##def _fn(self,name):
        ##return self._fn_base(name.first_name)

    ##def _fn_raw(self,raw_data):
        ##first = raw_data[_FIRSTNAME]
        ##return self._fn_base(first)

    ##def _fn_base(self,first):
        ##return first

    ##def _ptfn(self,name):
        ##"""
        ##Prints the Western style first name, last name style.
        ##Typically this is::

           ##SurnamePrefix Patronymic SurnameSuffix, FirstName
        ##"""

        ##return self._ptfn_base(name.first_name,name.suffix,
                               ##name.prefix,name.patronymic)

    ##def _ptfn_raw(self,raw_data):
        ##"""
        ##Prints the Western style first name, last name style.
        ##Typically this is::

           ##SurnamePrefix Patronymic SurnameSuffix, FirstName
        ##"""

        ##first = raw_data[_FIRSTNAME]
        ##suffix = raw_data[_SUFFIX]
        ##prefix = raw_data[_PREFIX]
        ##patronymic = raw_data[_PATRONYM]

        ##return self._ptfn_base(first,suffix,prefix,patronymic)

    ##def _ptfn_base(self,first,suffix,prefix,patronymic):
        ##if self.force_upper:
            ##last = patronymic.upper()
        ##else:
            ##last = patronymic
            
        ##if suffix:
            ##if prefix:
                ##return "%s %s %s, %s" % (prefix, last, suffix, first)
            ##else:
                ##return "%s %s, %s" % (last, suffix, first)
        ##else:
            ##if prefix:
                ##return "%s %s, %s" % (prefix, last, first)
            ##else:
                ##return "%s, %s" % (last, first)
        
    ##def _fnln(self,name):
        ##"""
        ##Prints the Western style first name, last name style.
        ##Typically this is::

           ##FirstName Patronymic SurnamePrefix Surname SurnameSuffix
        ##"""
        ##return self._fnln_base(name.first_name,name.surname,name.suffix,
                          ##name.prefix,name.patronymic)

    ##def _fnln_raw(self,raw_data):
        ##"""
        ##Prints the Western style first name, last name style.
        ##Typically this is::

           ##FirstName Patronymic SurnamePrefix Surname SurnameSuffix
        ##"""
        ##first = raw_data[_FIRSTNAME]
        ##surname = raw_data[_SURNAME]
        ##suffix = raw_data[_SUFFIX]
        ##prefix = raw_data[_PREFIX]
        ##patronymic = raw_data[_PATRONYM]
        ##return self._fnln_base(first,surname,suffix,prefix,patronymic)

    ##def _fnln_base(self,first,surname,suffix,prefix,patronymic):
        ##if patronymic:
            ##first = "%s %s" % (first, patronymic)

        ##if self.force_upper:
            ##last = surname.upper()
        ##else:
            ##last = surname
            
        ##if suffix:
            ##if prefix:
                ##return "%s %s %s, %s" % (first, prefix, last, suffix)
            ##else:
                ##return "%s %s, %s" % (first, last, suffix)
        ##else:
            ##if prefix:
                ##return "%s %s %s" % (first, prefix, last)
            ##else:
                ##return "%s %s" % (first, last)

    ##def _lnfn(self,name):
        ##"""
        ##Prints the Western style last name, first name style.
        ##Typically this is::

            ##SurnamePrefix Surname, FirstName Patronymic SurnameSuffix
        ##"""
        ##return self._lnfn_base(name.first_name,name.surname,name.prefix,
                               ##name.suffix,name.patronymic)

    ##def _lnfn_raw(self,raw_data):
        ##"""
        ##Prints the Western style last name, first name style.
        ##Typically this is::

            ##SurnamePrefix Surname, FirstName Patronymic SurnameSuffix
        ##"""

        ##surname = raw_data[_SURNAME]
        ##prefix = raw_data[_PREFIX]
        ##first = raw_data[_FIRSTNAME]
        ##patronymic = raw_data[_PATRONYM]
        ##suffix = raw_data[_SUFFIX]

        ##return self._lnfn_base(first,surname,prefix,suffix,patronymic)

    ##def _lnfn_base(self,first,surname,prefix,suffix,patronymic):
        ##if self.force_upper:
            ##last = surname.upper()
        ##else:
            ##last = surname

        ##if last:
            ##last += ","

        ##return " ".join([prefix, last, first, patronymic, suffix])
    
    def format_str(self,name,format_str):
        return self._format_str_base(name.first_name,name.surname,name.prefix,
                                     name.suffix,name.patronymic,name.title,
                                     name.call,format_str)

    def format_str_raw(self,raw_data,format_str):
        surname = raw_data[_SURNAME]
        prefix = raw_data[_PREFIX]
        first = raw_data[_FIRSTNAME]
        patronymic = raw_data[_PATRONYM]
        suffix = raw_data[_SUFFIX]
        title = raw_data[_TITLE]
        call = raw_data[_CALL]
        return self._format_str_base(first,surname,prefix,suffix,patronymic,
                                     title,call,format_str)
        
    def _format_str_base(self,first,surname,prefix,suffix,patronymic,
                         title,call,format_str):
        """
        Generates name from a format string.

        The following substitutions are made:
            %t -> title
            %f -> given name (first name)
            %p -> prefix
            %s -> suffix
            %l -> family name (last name, surname)
            %y -> patronymic
            %c -> call name
        The capital letters are substituted for capitalized name components.
        The %% is substituted with the single % character.
        All the other characters in the fmt_str are unaffected.
        
        """

        output = format_str
        
        output = output.replace("%t",title)
        output = output.replace("%f",first)
        output = output.replace("%p",prefix)
        output = output.replace("%l",surname)
        output = output.replace("%s",suffix)
        output = output.replace("%y",patronymic)
        output = output.replace("%c",call)

        output = output.replace("%T",title.upper())
        output = output.replace("%F",first.upper())
        output = output.replace("%P",prefix.upper())
        output = output.replace("%L",surname.upper())
        output = output.replace("%S",suffix.upper())
        output = output.replace("%Y",patronymic.upper())
        output = output.replace("%C",call.upper())
        output = output.replace("%%",'%')

        # Suppress multiple spaces
        prev_space = -1
        namestr = ''
        for i in range(len(output)):
            if output[i] == ' ':
                dist = i - prev_space
                prev_space = i
                if dist == 1:
                    continue
            namestr += output[i]
                    
        return namestr.strip()

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
        return self.sorted_name(name)

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
        idx = name.sort_as
        if not self.fn_array.has_key(idx):
            idx = 0
        return self.fn_array[idx](name)

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
        idx = raw_data[_SORT]
        if not self.raw_fn_array.has_key(idx):
            idx = 0        
        return self.raw_fn_array[idx](raw_data)

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
        return self.display_name(name)

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
        # FIXME: At this time, this is just duplicating display() method
        name = person.get_primary_name()
        return self.display_name(name)

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

        idx = name.display_as
        if not self.fn_array.has_key(idx):
            idx = 0
        
        return self.fn_array[idx](name)

    def display_given(self,person):
        name = person.get_primary_name()
        return self.format_str(person.get_primary_name(),'%f %y')

    def name_grouping(self,db,person):
        return self.name_grouping_name(db,person.primary_name)

    def name_grouping_name(self,db,pn):
        if pn.group_as:
            return pn.group_as
        sv = pn.sort_as
        if sv == Name.LNFN:
            return db.get_name_group_mapping(pn.surname)
        elif sv == Name.PTFN:
            return db.get_name_group_mapping(pn.patronymic)
        else:
            return db.get_name_group_mapping(pn.first_name)

displayer = NameDisplay()
