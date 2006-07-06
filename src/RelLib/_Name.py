#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2006  Donald N. Allingham
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
Name class for GRAMPS
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
from _SecondaryObject import SecondaryObject
from _PrivacyBase import PrivacyBase
from _SourceBase import SourceBase
from _NoteBase import NoteBase
from _DateBase import DateBase
from _NameType import NameType

#-------------------------------------------------------------------------
#
# Personal Name
#
#-------------------------------------------------------------------------
class Name(SecondaryObject,PrivacyBase,SourceBase,NoteBase,DateBase):
    """
    Provides name information about a person.

    A person may have more that one name throughout his or her life.
    """

    DEF  = 0  # Default format (determined by gramps-wide prefs)
    LNFN = 1  # last name first name [patronymic]
    FNLN = 2  # first name last name
    PTFN = 3  # patronymic first name
    FN   = 4  # first name

    DEFAULT_FORMAT = \
        (DEF,_("Default format (defined by GRAMPS preferences)"),'')

    STANDARD_FORMATS = [
        (LNFN, _("Family name, Given name Patronymic"),''),
        (FNLN, _("Given name Family name"),''),
        (PTFN, _("Patronymic, Given name"),''),
        (FN,   _("Given name"),'')
    ]
    
    def __init__(self,source=None,data=None):
        """creates a new Name instance, copying from the source if provided"""
        SecondaryObject.__init__(self)
        if data:
            (privacy,source_list,note,date,
             self.first_name,self.surname,self.suffix,self.title,
             name_type,self.prefix,self.patronymic,self.sname,
             self.group_as,self.sort_as,self.display_as,self.call) = data
            self.type = NameType(name_type)
            PrivacyBase.unserialize(self,privacy)
            SourceBase.unserialize(self,source_list)
            NoteBase.unserialize(self,note)
            DateBase.unserialize(self,date)
        elif source:
            PrivacyBase.__init__(self,source)
            SourceBase.__init__(self,source)
            NoteBase.__init__(self,source)
            DateBase.__init__(self,source)
            self.first_name = source.first_name
            self.surname = source.surname
            self.suffix = source.suffix
            self.title = source.title
            self.type = source.type
            self.prefix = source.prefix
            self.patronymic = source.patronymic
            self.sname = source.sname
            self.group_as = source.group_as
            self.sort_as = source.sort_as
            self.display_as = source.display_as
            self.call = source.call
        else:
            PrivacyBase.__init__(self,source)
            SourceBase.__init__(self,source)
            NoteBase.__init__(self,source)
            DateBase.__init__(self,source)
            self.first_name = ""
            self.surname = ""
            self.suffix = ""
            self.title = ""
            self.type = NameType()
            self.prefix = ""
            self.patronymic = ""
            self.sname = '@'
            self.group_as = ""
            self.sort_as = self.DEF
            self.display_as = self.DEF
            self.call = ''

    def serialize(self):
        return (PrivacyBase.serialize(self),
                SourceBase.serialize(self),
                NoteBase.serialize(self),
                DateBase.serialize(self),
                self.first_name,self.surname,self.suffix,self.title,
                self.type.serialize(),self.prefix,self.patronymic,self.sname,
                self.group_as,self.sort_as,self.display_as,self.call)

    def unserialize(self,data):
        (privacy,source_list,note,date,
         self.first_name,self.surname,self.suffix,self.title,
         name_type,self.prefix,self.patronymic,self.sname,
         self.group_as,self.sort_as,self.display_as,self.call) = data
        self.type.unserialize(name_type)
        PrivacyBase.unserialize(self,privacy)
        SourceBase.unserialize(self,source_list)
        NoteBase.unserialize(self,note)
        DateBase.unserialize(self,date)
        return self

    def get_text_data_list(self):
        """
        Returns the list of all textual attributes of the object.

        @return: Returns the list of all textual attributes of the object.
        @rtype: list
        """
        return [self.first_name,self.surname,self.suffix,self.title,
                str(self.type),self.prefix,self.patronymic, self.call]

    def get_text_data_child_list(self):
        """
        Returns the list of child objects that may carry textual data.

        @return: Returns the list of child objects that may carry textual data.
        @rtype: list
        """
        check_list = self.source_list
        if self.note:
            check_list.append(self.note)
        return check_list

    def get_handle_referents(self):
        """
        Returns the list of child objects which may, directly or through
        their children, reference primary objects..
        
        @return: Returns the list of objects refereincing primary objects.
        @rtype: list
        """
        return self.source_list

    def set_group_as(self,name):
        """
        Sets the grouping name for a person. Normally, this is the person's
        surname. However, some locales group equivalent names (e.g. Ivanova
        and Ivanov in Russian are usually considered equivalent.
        """
        if name == self.surname:
            self.group_as = ""
        else:
            self.group_as = name

    def get_group_as(self):
        """
        Returns the grouping name, which is used to group equivalent surnames.
        """
        return self.group_as

    def get_group_name(self):
        """
        Returns the grouping name, which is used to group equivalent surnames.
        """
        if self.group_as:
            return self.group_as
        else:
            return self.surname

    def set_sort_as(self,value):
        """
        Specifies the sorting method for the specified name. Typically the
        locale's default should be used. However, there may be names where
        a specific sorting structure is desired for a name. 
        """
        self.sort_as = value

    def get_sort_as(self):
        """
        Returns the selected sorting method for the name. The options are
        LNFN (last name, first name), FNLN (first name, last name), etc.
        """
        return self.sort_as 

    def set_display_as(self,value):
        """
        Specifies the display format for the specified name. Typically the
        locale's default should be used. However, there may be names where
        a specific display format is desired for a name. 
        """
        self.display_as = value

    def get_display_as(self):
        """
        Returns the selected display format for the name. The options are
        LNFN (last name, first name), FNLN (first name, last name), etc.
        """
        return self.display_as

    def get_call_name(self):
        """
        Returns the call name. The call name's exact definition is not predetermined,
        and may be locale specific.
        """
        return self.call

    def set_call_name(self,val):
        """
        Returns the call name. The call name's exact definition is not predetermined,
        and may be locale specific.
        """
        self.call = val

    def get_surname_prefix(self):
        """
        Returns the prefix (or article) of a surname. The prefix is not
        used for sorting or grouping.
        """
        return self.prefix

    def set_surname_prefix(self,val):
        """
        Sets the prefix (or article) of a surname. Examples of articles
        would be 'de' or 'van'.
        """
        self.prefix = val

    def set_type(self,the_type):
        """sets the type of the Name instance"""
        self.type.set(the_type)

    def get_type(self):
        """returns the type of the Name instance"""
        return self.type

    def set_first_name(self,name):
        """sets the given name for the Name instance"""
        self.first_name = name

    def set_patronymic(self,name):
        """sets the patronymic name for the Name instance"""
        self.patronymic = name

    def set_surname(self,name):
        """sets the surname (or last name) for the Name instance"""
        self.surname = name

    def set_suffix(self,name):
        """sets the suffix (such as Jr., III, etc.) for the Name instance"""
        self.suffix = name

    def get_first_name(self):
        """returns the given name for the Name instance"""
        return self.first_name

    def get_patronymic(self):
        """returns the patronymic name for the Name instance"""
        return self.patronymic

    def get_surname(self):
        """returns the surname (or last name) for the Name instance"""
        return self.surname

    def get_upper_surname(self):
        """returns the surname (or last name) for the Name instance"""
        return self.surname.upper()

    def get_suffix(self):
        """returns the suffix for the Name instance"""
        return self.suffix

    def set_title(self,title):
        """sets the title (Dr., Reverand, Captain) for the Name instance"""
        self.title = title

    def get_title(self):
        """returns the title for the Name instance"""
        return self.title

    def get_name(self):
        """returns a name string built from the components of the Name
        instance, in the form of surname, Firstname"""

        if self.patronymic:
            first = "%s %s" % (self.first_name, self.patronymic)
        else:
            first = self.first_name
        if self.suffix:
            if self.prefix:
                return "%s %s, %s %s" % (self.prefix, self.surname, first, self.suffix)
            else:
                return "%s, %s %s" % (self.surname, first, self.suffix)
        else:
            if self.prefix:
                return "%s %s, %s" % (self.prefix,self.surname, first)
            else:
                return "%s, %s" % (self.surname, first)

    def get_upper_name(self):
        """returns a name string built from the components of the Name
        instance, in the form of surname, Firstname"""
        
        if self.patronymic:
            first = "%s %s" % (self.first_name, self.patronymic)
        else:
            first = self.first_name
        if self.suffix:
            if self.prefix:
                return "%s %s, %s %s" % (self.prefix.upper(), self.surname.upper(), first, self.suffix)
            else:
                return "%s, %s %s" % (self.surname.upper(), first, self.suffix)
        else:
            if self.prefix:
                return "%s %s, %s" % (self.prefix.upper(), self.surname.upper(), first)
            else:
                return "%s, %s" % (self.surname.upper(), first)

    def get_regular_name(self):
        """returns a name string built from the components of the Name
        instance, in the form of Firstname surname"""
        if self.patronymic:
            first = "%s %s" % (self.first_name, self.patronymic)
        else:
            first = self.first_name
        if (self.suffix == ""):
            if self.prefix:
                return "%s %s %s" % (first, self.prefix, self.surname)
            else:
                return "%s %s" % (first, self.surname)
        else:
            if self.prefix:
                return "%s %s %s, %s" % (first, self.prefix, self.surname, self.suffix)
            else:
                return "%s %s, %s" % (first, self.surname, self.suffix)
