#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2005  Donald N. Allingham
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011       Paul Franklin
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

# Written by Alex Roitman

"""
General option handling, including saving and parsing.
"""

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import os
import sys

#-------------------------------------------------------------------------
#
# SAX interface
#
#-------------------------------------------------------------------------
from xml.sax import make_parser, handler, SAXParseException
from xml.sax.saxutils import quoteattr

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
from ..utils.cast import get_type_converter
from .menu import Menu
from ..plug import BasePluginManager
PLUGMAN = BasePluginManager.get_instance()
from ..const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
#-------------------------------------------------------------------------
#
# List of options for a single module
#
#-------------------------------------------------------------------------
class OptionList:
    """
    Implements a set of options to parse and store for a given module.
    """

    def __init__(self):
        self.options = {}

    def set_options(self, options):
        """
        Set the whole bunch of options for the OptionList.

        :param options: list of options to set.
        :type options: list
        """
        self.options = options

    def get_options(self):
        """
        Return the whole bunch of  options for the OptionList.

        :returns: list of options
        :rtype: list
        """
        return self.options

    def set_option(self, name, value):
        """
        Set a particular option in the OptionList.

        :param name: name of the option to set.
        :type name: str
        :param value: value of the option to set.
        :type value: str
        """
        self.options[name] = value

    def remove_option(self, name):
        """
        Remove a particular option from the OptionList.

        :param name: name of the option to remove.
        :type name: str
        """
        if name in self.options:
            del self.options[name]

    def get_option(self, name):
        """
        Return the value of a particular option in the OptionList.

        :param name: name of the option to retrieve
        :type name: str
        :returns: value associated with the passed option
        :rtype: str
        """
        return self.options.get(name, None)

#-------------------------------------------------------------------------
#
# Collection of option lists
#
#-------------------------------------------------------------------------
class OptionListCollection:
    """
    Implements a collection of option lists.
    """

    def __init__(self, filename):
        """
        Create an OptionListCollection instance from the list defined
        in the specified file.

        :param filename: XML file that contains option definitions
        :type filename: str
        """

        self.filename = os.path.expanduser(filename)
        self.option_list_map = {}
        self.docgen_names = PLUGMAN.get_docgen_names()
        self.init_common()
        self.parse()

    def init_common(self):
        pass

    def get_option_list_map(self):
        """
        Return the map of module names to option lists.

        :returns: Returns the map of module names to option lists.
        :rtype: dictionary
        """
        return self.option_list_map

    def get_option_list(self, name):
        """
        Return the option_list associated with the module name

        :param name: name associated with the desired module.
        :type name: str
        :returns: returns the option list associated with the name,
                  or None of no such option exists
        :rtype: str
        """
        return self.option_list_map.get(name, None)

    def get_module_names(self):
        """
        Return a list of all the module names in the OptionListCollection

        :returns: returns the list of module names
        :rtype: list
        """
        return list(self.option_list_map.keys())

    def set_option_list(self, name, option_list):
        """
        Add or replaces an option_list in the OptionListCollection.

        :param name: name associated with the module to add or replace.
        :type name: str
        :param option_list: list of options
        :type option_list: OptionList
        """
        self.option_list_map[name] = option_list

    def write_common(self, filename):
        """
        Stub function for common options. Overridden by reports.
        """
        pass

    def write_module_common(self, filename, option_list):
        """
        Stub function for common options. Overridden by reports.
        """
        pass

    def save(self):
        """
        Saves the current OptionListCollection to the associated file.
        """
        with open(self.filename, "w", encoding="utf-8") as file:
            file.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
            file.write('<options>\n')

            self.write_common(file)

            for module_name in sorted(self.get_module_names()): # enable a diff
                option_list = self.get_option_list(module_name)
                module_docgen_opts = {}
                for docgen_name in self.docgen_names:
                    module_docgen_opts[docgen_name] = []
                file.write('<module name=%s>\n' % quoteattr(module_name))
                options = option_list.get_options()
                for option_name in sorted(options.keys()): # enable a diff
                    option_data = options[option_name]
                    if isinstance(option_data, (list, tuple)):
                        if option_data and option_data[0] in self.docgen_names:
                            module_docgen_opts[option_data[0]].append(
                                (option_name, option_data[1]))
                        else:
                            file.write('  <option name=%s '
                                       'value="" length="%d">\n'
                                       % (quoteattr(option_name),
                                          len(option_data)))
                            for list_index, list_data in enumerate(option_data):
                                file.write('    <listitem '
                                           'number="%d" value=%s/>\n'
                                           % (list_index,
                                              quoteattr(str(list_data))))
                            file.write('  </option>\n')
                    else:
                        file.write('  <option name=%s value=%s/>\n'
                                   % (quoteattr(option_name),
                                      quoteattr(str(option_data))))
                for docgen_name in self.docgen_names:
                    if module_docgen_opts[docgen_name]:
                        for idx, data in enumerate(
                                module_docgen_opts[docgen_name]):
                            file.write('  <docgen-option docgen=%s '
                                       'name=%s value=%s/>\n'
                                       % (quoteattr(docgen_name),
                                          quoteattr(data[0]),
                                          quoteattr(str(data[1]))))
                self.write_module_common(file, option_list)

                file.write('</module>\n')

            file.write('</options>\n')

    def parse(self):
        """
        Loads the OptionList from the associated file, if it exists.
        """
        try:
            if os.path.isfile(self.filename):
                parser = make_parser()
                parser.setContentHandler(OptionParser(self))
                parser.parse(self.filename)
        except (IOError, OSError, SAXParseException):
            pass

#-------------------------------------------------------------------------
#
# OptionParser
#
#-------------------------------------------------------------------------
class OptionParser(handler.ContentHandler):
    """
    SAX parsing class for the OptionListCollection XML file.
    """

    def __init__(self, collection):
        """
        Create a OptionParser class that populates the passed collection.

        collection:   OptionListCollection to be loaded from the file.
        """
        handler.ContentHandler.__init__(self)
        self.collection = collection

        self.mname = None
        self.option_list = None
        self.oname = None
        self.odict = None
        self.an_o = None
        self.list_class = OptionList

    def startElement(self, tag, attrs):
        """
        Overridden class that handles the start of a XML element
        """
        if tag in ("report", "module"):
            self.mname = attrs['name']
            self.option_list = self.list_class()
            self.odict = {}
        elif tag == "option":
            self.oname = attrs['name']
            if 'length' in attrs:
                self.an_o = []
            else:
                self.an_o = attrs['value']
        elif tag == "listitem":
            self.an_o.append(attrs['value'])

    def endElement(self, tag):
        "Overridden class that handles the end of a XML element"
        if tag == "option":
            self.odict[self.oname] = self.an_o
        elif tag in ("report", "module"):
            self.option_list.set_options(self.odict)
            self.collection.set_option_list(self.mname, self.option_list)

#-------------------------------------------------------------------------
#
# Class handling options for plugins
#
#-------------------------------------------------------------------------
class OptionHandler:
    """
    Implements handling of the options for the plugins.
    """

    def __init__(self, module_name, options_dict, person_id=None):
        self.module_name = module_name
        self.default_options_dict = options_dict.copy()
        self.options_dict = options_dict

        # Retrieve our options from whole collection
        self.init_subclass()
        self.option_list_collection = self.collection_class(self.filename)
        self.init_common()
        self.saved_option_list = self.option_list_collection.get_option_list(
            module_name)
        self.person_id = person_id

        # Whatever was found should override the defaults
        if self.saved_option_list:
            self.set_options()
        else:
            # If nothing was found, set up the option list
            self.saved_option_list = self.list_class()
            self.option_list_collection.set_option_list(module_name,
                                                        self.saved_option_list)

    def init_subclass(self):
        self.collection_class = OptionListCollection
        self.list_class = OptionList
        self.filename = None

    def init_common(self):
        pass

    def set_options(self):
        """
        Set options to be used in this plugin according to the passed
        options dictionary.

        Dictionary values are all strings, since they were read from XML.
        Here we need to convert them to the needed types. We use default
        values to determine the type.
        """
        # First we set options_dict values based on the saved options
        options = self.saved_option_list.get_options()
        bad_opts = []
        for option_name, option_data in options.items():
            if option_name not in self.options_dict:
                bad_opts.append(option_name)
                continue
            try:
                converter = get_type_converter(self.options_dict[option_name])
                self.options_dict[option_name] = converter(option_data)
            except ValueError:
                pass
            except TypeError:
                pass

        docgen_names = self.option_list_collection.docgen_names
        for option_name in bad_opts:
            option_data = options[option_name]
            if not (isinstance(option_data, list)
                    and option_data
                    and option_data[0] in docgen_names):
                print(_("Option '%(opt_name)s' is present in %(file)s\n"
                        "  but is not known to the module.  Ignoring..."
                       ) % {'opt_name' : option_name,
                            'file'     : self.option_list_collection.filename},
                      file=sys.stderr)
            options.pop(option_name)

        # Then we set common options from whatever was found
        self.set_common_options()

    def set_common_options(self):
        pass

    def save_options(self):
        """
        Saves options to file.

        We need to only store non-default options. Therefore, we remove all
        options whose values are the defaults prior to saving.
        """

        # First we save options from options_dict
        for option_name, option_data in self.options_dict.items():
            if option_data == self.default_options_dict[option_name]:
                self.saved_option_list.remove_option(option_name)
            else:
                self.saved_option_list.set_option(
                    option_name, self.options_dict[option_name])

        # Handle common options
        self.save_common_options()

        # Finally, save the whole collection into file
        self.option_list_collection.save()

    def save_common_options(self):
        pass

    def get_person_id(self):
        return self.person_id

    def set_person_id(self, val):
        self.person_id = val

#------------------------------------------------------------------------
#
# Base Options class
#
#------------------------------------------------------------------------
class Options:

    """
    Defines options and provides handling interface.

    This is a base Options class for the modules. All modules, options
    classes should derive from it.
    """

    def __init__(self, name, person_id=None):
        """
        Initialize the class, performing usual house-keeping tasks.
        Subclasses MUST call this in their __init__() method.

        Modules that need custom options need to override this method.
        Two dictionaries allow the addition of custom options:

            self.options_dict
                This is a dictionary whose keys are option names
                and values are the default option values.

            self.options_help
                This is a dictionary whose keys are option names
                and values are 3- or 4- lists or tuples:
                    ('=example','Short description',VALUES,DO_PREPEND)
                The VALUES is either a single string (in that case
                the DO_PREPEND does not matter) or a list/tuple of
                strings to list. In that case, if DO_PREPEND evaluates
                as True then each string will be preneded with the ordinal
                number when help is printed on the command line.

        .. note:: Both dictionaries must have identical keys.
        """
        self.name = name
        self.person_id = person_id
        self.options_dict = {}
        self.options_help = {}
        self.handler = None

    def load_previous_values(self):
        """
        Modifies all options to have the value they were last used as.
        Call this function after all options have been added.
        """
        self.handler = OptionHandler(
            self.name, self.options_dict, self.person_id)

    def add_user_options(self):
        """
        Set up UI controls (widgets) for the options specific for this module.

        This method MUST be overridden by modules that define new options.

        .. note:: To really have any effect besides looking pretty, each widget
                  set up here must be also parsed in the
                  :meth:`parse_user_options` method below.
        """
        pass

    def parse_user_options(self):
        """
        Parses UI controls (widgets) for the options specific for this module.

        This method MUST be overridden by modules that define new options.

        After obtaining values from the widgets, they MUST be used to set the
        appropriate options_dict values. Otherwise the values will not have
        any user-visible effect.

        .. note:: Any widget parsed here MUST be defined and added to the dialog
                  in the :meth:`add_user_options` method above.
        """
        pass

#------------------------------------------------------------------------
#
# MenuOptions class
#
#------------------------------------------------------------------------
class MenuOptions:
    """
    **Introduction**

    A MenuOptions is used to implement the necessary functions for adding
    options to a menu.
    """
    def __init__(self):
        self.menu = Menu()

        # Fill options_dict with report/tool defaults:
        self.options_dict = {}
        self.options_help = {}
        self.add_menu_options(self.menu)
        for name in self.menu.get_all_option_names():
            option = self.menu.get_option_by_name(name)
            self.options_dict[name] = option.get_value()
            self.options_help[name] = ["", option.get_help()]

    def make_default_style(self, default_style):
        """
        This function is currently required by some reports.
        """
        pass

    def add_menu_options(self, menu):
        """
        Add the user defined options to the menu.

        :param menu: A menu class for the options to belong to.
        :type menu: Menu
        :return: nothing
        """
        raise NotImplementedError

    def add_menu_option(self, category, name, option):
        """
        Add a single option to the menu.
        """
        self.menu.add_option(category, name, option)
        self.options_dict[name] = option.get_value()
        self.options_help[name] = ["", option.get_help()]

    def add_user_options(self):
        """
        Generic method to add user options to the menu.
        """
        for category in self.menu.get_categories():
            for name in self.menu.get_option_names(category):
                option = self.menu.get_option(category, name)

                # override option default with xml-saved value:
                if name in self.options_dict:
                    option.set_value(self.options_dict[name])

    def parse_user_options(self):
        """
        Load the changed values into the saved options.
        """
        for name in self.menu.get_all_option_names():
            option = self.menu.get_option_by_name(name)
            self.options_dict[name] = option.get_value()
