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
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

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
_GROUP     = 11
_SORT      = 12
_DISPLAY   = 13
_CALL      = 14

_ACT = True
_INA = False

_F_NAME = 0  # name of the format
_F_FMT = 1   # the format string
_F_ACT = 2   # if the format is active
_F_FN = 3    # name format function
_F_RAWFN = 4 # name format raw function

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

    STANDARD_FORMATS = [
        (Name.DEF,_("Default format (defined by GRAMPS preferences)"),'',_ACT),
        (Name.LNFN,_("Family name, Given name Patronymic"),'%p %l, %f %y %s',_ACT),
        (Name.FNLN,_("Given name Family name"),'%f %y %p %l %s',_ACT),
        (Name.PTFN,_("Patronymic, Given name"),'%p %y, %s %f',_ACT),
        (Name.FN,_("Given name"),'%f',_ACT)
    ]
    
    def __init__(self):
        self.name_formats = {}
        self.set_name_format(self.STANDARD_FORMATS)
        
        self.default_format = Config.get(Config.NAME_FORMAT)
        if self.default_format == 0:
            self.default_format = Name.LNFN
            Config.set(Config.NAME_FORMAT,self.default_format)
            
        self.set_default_format(self.default_format)

    def _format_fn(self,fmt_str):
        return lambda x: self.format_str(x,fmt_str)
    
    def _format_raw_fn(self,fmt_str):
        return lambda x: self.format_str_raw(x,fmt_str)
    
    def set_name_format(self,formats):
        for (num,name,fmt_str,act) in formats:
            self.name_formats[num] = (name,fmt_str,act,
                                      self._format_fn(fmt_str),
                                      self._format_raw_fn(fmt_str))

    def add_name_format(self,name,fmt_str):
        num = -1
        while num in self.name_formats:
            num -= 1
        self.set_name_format([(num,name,fmt_str,_ACT)])
        return num
    
    def edit_name_format(self,num,name,fmt_str):
        self.set_name_format([(num,name,fmt_str,_ACT)])
        if self.default_format == num:
            self.set_default_format(num)
        
    def del_name_format(self,num):
        try:
            del self.name_formats[num]
        except:
            pass
        
    def set_default_format(self,num):
        if num not in self.name_formats:
            num = Name.LNFN
            
        self.default_format = num
        
        self.name_formats[Name.DEF] = (self.name_formats[Name.DEF][_F_NAME],
                                       self.name_formats[Name.DEF][_F_FMT],
                                       self.name_formats[Name.DEF][_F_ACT],
                                       self.name_formats[num][_F_FN],
                                       self.name_formats[num][_F_RAWFN])
    
    def get_default_format(self):
        return self.default_format

    def set_format_inactive(self,num):
        try:
            self.name_formats[num] = (self.name_formats[num][_F_NAME],
                                      self.name_formats[num][_F_FMT],
                                      _INA,
                                      self.name_formats[num][_F_FN],
                                      self.name_formats[num][_F_RAWFN])
        except:
            pass
        
    def get_name_format(self,also_default=False,
                        only_custom=False,
                        only_active=True):
        """
        Get a list of tuples (num,name,fmt_str,act)
        """
        the_list = []

        keys = self.name_formats.keys()
        keys.sort(self._sort_name_format)
        
        for num in keys:
            if ((also_default or num) and
                (not only_custom or (num < 0)) and
                (not only_active or self.name_formats[num][_F_ACT])):
                the_list.append((num,) + self.name_formats[num][_F_NAME:_F_FN])

        return the_list

    def _sort_name_format(self,x,y):
        if x<0:
            if y<0: return x+y
            else: return -x+y
        else:
            if y<0: return -x+y
            else: return x-y
        
    def _is_format_valid(self,num):
        try:
            if not self.name_formats[num][_F_ACT]:
                num = 0
        except:
            num = 0    
        return num

    #-------------------------------------------------------------------------

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
    
    #-------------------------------------------------------------------------    

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
        num = self._is_format_valid(name.sort_as)
        return self.name_formats[num][_F_FN](name)

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
        num = self._is_format_valid(raw_data[_SORT])
        return self.name_formats[num][_F_RAWFN](raw_data)

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

        num = self._is_format_valid(name.display_as)
        return self.name_formats[num][_F_FN](name)

    def display_given(self,person):
        name = person.get_primary_name()
        return self.format_str(person.get_primary_name(),'%f %y')

    def name_grouping(self,db,person):
        return self.name_grouping_name(db,person.primary_name)

    def name_grouping_name(self,db,pn):
        if pn.group_as:
            return pn.group_as
        sv = pn.sort_as
        if sv == Name.LNFN or sv == Name.DEF:
            return db.get_name_group_mapping(pn.surname)
        elif sv == Name.PTFN:
            return db.get_name_group_mapping(pn.patronymic)
        else:
            return db.get_name_group_mapping(pn.first_name)

    def name_grouping_data(self, db, pn):
        if pn[_GROUP]:
            return pn[_GROUP]
        sv = pn[_SORT]
        if sv == Name.LNFN or sv == Name.DEF:
            return db.get_name_group_mapping(pn[_SURNAME])
        elif sv == Name.PTFN:
            return db.get_name_group_mapping(pn[_PATRONYM])
        else:
            return db.get_name_group_mapping(pn[_FIRSTNAME])

displayer = NameDisplay()
