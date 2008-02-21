#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2007-2008  Brian G. Matherly
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
Abstracted option handling.
"""
#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import gen.utils

#-------------------------------------------------------------------------
#
# Option class
#
#-------------------------------------------------------------------------
class Option(gen.utils.Callback):
    """
    This class serves as a base class for all options. All Options must 
    minimally provide the services provided by this class. Options are allowed 
    to add additional functionality.
    """
    
    __signals__ = { 'value-changed' : None,
                    'avail-changed' : None}
    
    def __init__(self, label, value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Exclude living people"
        @type label: string
        @param value: An initial value for this option.
            Example: True
        @type value: The type will depend on the type of option.
        @return: nothing
        """
        gen.utils.Callback.__init__(self)
        self.__value = value
        self.__label = label
        self.__help_str = ""
        self.__available = True
        
    def get_label(self):
        """
        Get the friendly label for this option.
        
        @return: string
        """
        return self.__label
    
    def set_label(self, label):
        """
        Set the friendly label for this option.
        
        @param label: A friendly label to be applied to this option.
            Example: "Exclude living people"
        @type label: string
        @return: nothing
        """
        self.__label = label
        
    def get_value(self):
        """
        Get the value of this option.
        
        @return: The option value.
        """
        return self.__value
    
    def set_value(self, value):
        """
        Set the value of this option.
        
        @param value: A value for this option.
            Example: True
        @type value: The type will depend on the type of option.
        @return: nothing
        """
        self.__value = value
        self.emit('value-changed')
        
    def get_help(self):
        """
        Get the help information for this option.
        
        @return: A string that provides additional help beyond the label.
        """
        return self.__help_str
        
    def set_help(self, help_text):
        """
        Set the help information for this option.
        
        @param help: A string that provides additional help beyond the label.
            Example: "Whether to include or exclude people who are calculated 
            to be alive at the time of the generation of this report"
        @type value: string
        @return: nothing
        """
        self.__help_str = help_text
        
    def set_available(self, avail):
        """
        Set the availability of this option.
        
        @param avail: An indicator of whether this option is currently 
        available. True indicates that the option is available. False indicates
        that the option is not available.
        @type avail: Bool
        @return: nothing
        """
        if avail != self.__available:
            self.__available = avail
            self.emit('avail-changed')
        
    def get_available(self):
        """
        Get the availability of this option.
        
        @return: A Bool indicating the availablity of this option. 
        True indicates that the option is available. 
        False indicates that the option is not available.
        """
        return self.__available

#-------------------------------------------------------------------------
#
# StringOption class
#
#-------------------------------------------------------------------------
class StringOption(Option):
    """
    This class describes an option that is a simple one-line string.
    """
    def __init__(self, label, value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Page header"
        @type label: string
        @param value: An initial value for this option.
            Example: "Generated by GRAMPS"
        @type value: string
        @return: nothing
        """
        Option.__init__(self, label, value)

#-------------------------------------------------------------------------
#
# ColourOption class
#
#-------------------------------------------------------------------------
class ColourOption(Option):
    """
    This class describes an option that allows the selection of a colour.
    """
    def __init__(self, label, value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Males"
        @type label: string
        @param value: An initial value for this option.
            Example: "#ff00a0"
        @type value: string
        @return: nothing
        """
        Option.__init__(self, label, value)

#-------------------------------------------------------------------------
#
# NumberOption class
#
#-------------------------------------------------------------------------
class NumberOption(Option):
    """
    This class describes an option that is a simple number with defined maximum 
    and minimum values.
    """
    def __init__(self, label, value, min_val, max_val, step = 1):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Number of generations to include"
        @type label: string
        @param value: An initial value for this option.
            Example: 5
        @type value: int
        @param min: The minimum value for this option.
            Example: 1
        @type min: int
        @param max: The maximum value for this option.
            Example: 10
        @type value: int
        @param step: The step size for this option.
            Example: 0.01
        @type value: int or float
        @return: nothing
        """
        Option.__init__(self, label, value)
        self.__min = min_val
        self.__max = max_val
        self.__step = step
    
    def get_min(self):
        """
        Get the minimum value for this option.
        
        @return: an int that represents the minimum value for this option.
        """
        return self.__min
    
    def get_max(self):
        """
        Get the maximum value for this option.
        
        @return: an int that represents the maximum value for this option.
        """
        return self.__max
    
    def get_step(self):
        """
        Get the step size for this option.
        
        @return: an int that represents the step size for this option.
        """
        return self.__step

#-------------------------------------------------------------------------
#
# TextOption class
#
#-------------------------------------------------------------------------
class TextOption(Option):
    """
    This class describes an option that is a multi-line string.
    """
    def __init__(self, label, value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Page header"
        @type label: string
        @param value: An initial value for this option.
            Example: "Generated by GRAMPS\nCopyright 2007"
        @type value: string
        @return: nothing
        """
        Option.__init__(self, label, value)
        
#-------------------------------------------------------------------------
#
# BooleanOption class
#
#-------------------------------------------------------------------------
class BooleanOption(Option):
    """
    This class describes an option that is a boolean (True or False).
    """
    def __init__(self, label, value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Exclude living people"
        @type label: string
        @param value: An initial value for this option.
            Example: True
        @type value: boolean
        @return: nothing
        """
        Option.__init__(self, label, value)
        
#-------------------------------------------------------------------------
#
# EnumeratedListOption class
#
#-------------------------------------------------------------------------
class EnumeratedListOption(Option):
    """
    This class describes an option that provides a finite number of values.
    Each possible value is assigned a value and a description.
    """
    
    __signals__ = { 'options-changed' : None }
    
    def __init__(self, label, value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Paper Size"
        @type label: string
        @param value: An initial value for this option.
            Example: 5
        @type value: int
        @return: nothing
        """
        Option.__init__(self, label, value)
        self.__items = []

    def add_item(self, value, description):
        """
        Add an item to the list of possible values.
        
        @param value: The value that corresponds to this item.
            Example: 5
        @type value: int
        @param description: A description of this value.
            Example: "8.5 x 11"
        @type description: string
        @return: nothing
        """
        self.__items.append((value, description))
        self.emit('options-changed')
        
    def set_items(self, items):
        """
        Add a list of items to the list of possible values.
        
        @param items: A list of tuples containing value, description pairs.
            Example: [ (5,"8.5 x 11"), (6,"11 x 17")]
        @type items: array
        @return: nothing
        """
        self.__items = items
        self.emit('options-changed')
        
    def get_items(self):
        """
        Get all the possible values for this option.
        
        @return: an array of tuples containing (value,description) pairs.
        """
        return self.__items
    
    def clear(self):
        """
        Clear all possible values from this option.
        
        @return: nothing.
        """
        self.__items = []
        self.emit('options-changed')

#-------------------------------------------------------------------------
#
# FilterOption class
#
#-------------------------------------------------------------------------
class FilterOption(EnumeratedListOption):
    """
    This class describes an option that provides a list of person filters.
    Each possible value represents one of the possible filters.
    """
    def __init__(self, label, value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Filter"
        @type label: string
        @param value: A default value for the option.
            Example: 1
        @type label: int
        @return: nothing
        """
        EnumeratedListOption.__init__(self, label, value)
        self.__filters = []
            
    def set_filters(self, filter_list):
        """
        Set the list of filters available to be chosen from.
        
        @param filter_list: An array of person filters.
        @type filter_list: array
        @return: nothing
        """
        items = []
        curval = self.get_value()
        
        value = 0
        for filt in filter_list:
            items.append((value, filt.get_name()))
            value += 1
            
        self.__filters = filter_list
        self.clear()
        self.set_items( items )
        
        self.set_value(curval)
    
    def get_filter(self):
        """
        Return the currently selected filter object.
        
        @return: A filter object.
        """
        return self.__filters[self.get_value()]
    
#-------------------------------------------------------------------------
#
# PersonOption class
#
#-------------------------------------------------------------------------
class PersonOption(StringOption):
    """
    This class describes an option that allows a person from the 
    database to be selected.
    """
    def __init__(self, label):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Center Person"
        @type label: string
        @param value: A Gramps ID of a person for this option.
            Example: "p11"
        @type value: string
        @return: nothing
        """
        StringOption.__init__(self, label, "")

#-------------------------------------------------------------------------
#
# FamilyOption class
#
#-------------------------------------------------------------------------
class FamilyOption(StringOption):
    """
    This class describes an option that allows a family from the 
    database to be selected.
    """
    def __init__(self, label):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Center Family"
        @type label: string
        @param value: A Gramps ID of a family for this option.
            Example: "f11"
        @type value: string
        @return: nothing
        """
        StringOption.__init__(self, label, "")
        
#-------------------------------------------------------------------------
#
# NoteOption class
#
#-------------------------------------------------------------------------
class NoteOption(StringOption):
    """
    This class describes an option that allows a note from the 
    database to be selected.
    """
    def __init__(self, label):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Title Note"
        @type label: string
        @param value: A Gramps ID of a note for this option.
            Example: "n11"
        @type value: string
        @return: nothing
        """
        StringOption.__init__(self, label, "")
        
#-------------------------------------------------------------------------
#
# MediaOption class
#
#-------------------------------------------------------------------------
class MediaOption(StringOption):
    """
    This class describes an option that allows a media object from the 
    database to be selected.
    """
    def __init__(self, label):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Image"
        @type label: string
        @param value: A Gramps ID of a media object for this option.
            Example: "m11"
        @type value: string
        @return: nothing
        """
        StringOption.__init__(self, label, "")

#-------------------------------------------------------------------------
#
# PersonListOption class
#
#-------------------------------------------------------------------------
class PersonListOption(Option):
    """
    This class describes a widget that allows multiple people from the 
    database to be selected.
    """
    def __init__(self, label):
        """
        @param label: A friendly label to be applied to this option.
            Example: "People of interest"
        @type label: string
        @param value: A set of GIDs as initial values for this option.
            Example: "111 222 333 444"
        @type value: string
        @return: nothing
        """
        Option.__init__(self, label, "")

#-------------------------------------------------------------------------
#
# SurnameColourOption class
#
#-------------------------------------------------------------------------
class SurnameColourOption(Option):
    """
    This class describes a widget that allows multiple surnames to be
    selected from the database, and to assign a colour (not necessarily
    unique) to each one.
    """
    def __init__(self, label):
        """
        @param label: A friendly label to be applied to this option.
            Example: "Family lines"
        @type label: string
        @param value: A set of surnames and colours.
            Example: "surname1 colour1 surname2 colour2"
        @type value: string
        @return: nothing
        """
        Option.__init__(self, label, "")

#-------------------------------------------------------------------------
#
# DestinationOption class
#
#-------------------------------------------------------------------------
class DestinationOption(StringOption):
    """
    This class describes an option that specifies a destination file or path.
    The destination can be a directory or a file. If the destination is a file,
    the extension can be specified.
    """
    
    __signals__ = { 'options-changed' : None }
    
    def __init__(self, label, value):
        """
        @param label: A friendly label to be applied to this option.
            Example: "File Name"
        @type label: string
        @param value: A default destination for this option.
            Example: "/home/username/Desktop/"
            Example: "/home/username/Desktop/report.pdf"
        @type value: string
        @param is_directory: Specifies whether the destination is a directory 
        or a file.
        @type value: bool
        @return: nothing
        """
        StringOption.__init__(self, label, value)
        self.__is_directory = False
        self.__extension = ""
        
    def set_directory_entry(self, is_directory):
        """
        @param is_directory: Specifies whether the destination is a directory 
        or a file.
        @type value: bool
        @return: nothing
        """
        self.__is_directory = is_directory
        self.emit('options-changed')
        
    def get_directory_entry(self):
        """
        @return: True if the destination is a directory. False if the 
        destination is a file.
        """
        return self.__is_directory

    def set_extension(self, extension):
        """
        @param extension: Specifies the extension for the destination file. 
        @type value: str
        @return: nothing
        """
        self.__extension = extension
        
    def get_extension(self):
        """
        @return: The extension for the destination file.
        """
        return self.__extension
        
#-------------------------------------------------------------------------
#
# Menu class
#
#-------------------------------------------------------------------------
class Menu:
    """
    Introduction
    ============
    A Menu is used to maintain a collection of options that need to be 
    represented to the user in a non-implementation specific way. The options
    can be described using the various option classes. A menu contains many
    options and associates them with a unique name and category.
    
    Usage
    =====
    Menus are used in the following way.

      1. Create a option object and configure all the attributes of the option.
      2. Add the option to the menu by specifying the option, name and category.
      3. Add as many options as necessary.
      4. When all the options are added, the menu can be stored and passed to
         the part of the system that will actually represent the menu to 
         the user.
    """
    def __init__(self):
        # __options holds all the options by their category
        self.__options = {}
        # __categories holds the order of all categories
        self.__categories = []
    
    def add_option(self, category, name, option):
        """
        Add an option to the menu.
        
        @param category: A label that describes the category that the option 
            belongs to. 
            Example: "Report Options"
        @type category: string
        @param name: A name that is unique to this option.
            Example: "generations"
        @type name: string
        @param option: The option instance to be added to this menu.
        @type option: Option
        @return: nothing
        """
        if not self.__options.has_key(category):
            self.__categories.append(category)
            self.__options[category] = []
        self.__options[category].append((name, option))
        
    def get_categories(self):
        """
        Get a list of categories in this menu.
        
        @return: a list of strings
        """
        return self.__categories
    
    def get_option_names(self, category):
        """
        Get a list of option names for the specified category.
        
        @return: a list of strings
        """
        names = []
        for (name, option) in self.__options[category]:
            names.append(name)
        return names
    
    def get_option(self, category, name):
        """
        Get an option with the specified category and name.
        
        @return: an Option instance or None on failure.
        """
        for (oname, option) in self.__options[category]:
            if oname == name:
                return option
        return None
    
    def get_all_option_names(self):
        """
        Get a list of all the option names in this menu.
        
        @return: a list of strings
        """
        names = []
        for category in self.__options:
            for (name, option) in self.__options[category]:
                names.append(name)
        return names
    
    def get_option_by_name(self, name):
        """
        Get an option with the specified name.
        
        @return: an Option instance or None on failure.
        """
        for category in self.__options.keys():
            for (oname, option) in self.__options[category]:
                if oname == name:
                    return option
        return None
