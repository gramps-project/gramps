#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004  Donald N. Allingham
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

# Written by Alex Roitman

"""
Report option handling, including saving and parsing.
"""

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
import os
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# SAX interface
#
#-------------------------------------------------------------------------
try:
    from xml.sax import make_parser,handler,SAXParseException
except:
    from _xmlplus.sax import make_parser,handler,SAXParseException

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import GrampsGconfKeys
import Utils
import BaseDoc

#-------------------------------------------------------------------------
#
# List of options for a single report
#
#-------------------------------------------------------------------------
class OptionList:
    """
    Implements a set of options to parse and store for a given report.
    """

    def __init__(self):
        self.options = {}
        self.style_name = None
        self.paper_name = None
        self.orientation = None
        self.template_name = None
        self.format_name = None
    
    def set_options(self,options):
        """
        Sets the whole bunch of options for the OptionList.
        
        options:    list of options to set.
        """
        self.options = options

    def get_options(self):
        """
        Returns the whole bunch of  options for the OptionList.
        """
        return self.options

    def set_option(self,name,value):
        """
        Sets a particular option in the OptionList.
        
        name:    name of the option to set.
        value:   value of the option to set.
        """
        self.options[name] = value

    def remove_option(self,name):
        """
        Removes a particular option from the OptionList.
        
        name:    name of the option to remove.
        """
        if self.options.has_key(name):
            del self.options[name]

    def get_option(self,name):
        """
        Returns the value of a particular option in the OptionList.
        """
        return self.options.get(name,None)

    def set_style_name(self,style_name):
        """
        Sets the style name for the OptionList.
        
        style_name: name of the style to set.
        """
        self.style_name = style_name

    def get_style_name(self):
        """
        Returns the style name of the OptionList.
        """
        return self.style_name

    def set_paper_name(self,paper_name):
        """
        Sets the paper name for the OptionList.
        
        style_name: name of the paper to set.
        """
        self.paper_name = paper_name

    def get_paper_name(self):
        """
        Returns the paper name of the OptionList.
        """
        return self.paper_name

    def set_orientation(self,orientation):
        """
        Sets the orientation for the OptionList.
        
        orientation: orientation to set.
        """
        self.orientation = orientation

    def get_orientation(self):
        """
        Returns the orientation for the OptionList.
        """
        return self.orientation

    def set_template_name(self,template_name):
        """
        Sets the template name for the OptionList.
        
        template_name: name of the template to set.
        """
        self.template_name = template_name

    def get_template_name(self):
        """
        Returns the template name of the OptionList.
        """
        return self.template_name

    def set_format_name(self,format_name):
        """
        Sets the format name for the OptionList.
        
        format_name: name of the format to set.
        """
        self.format_name = format_name

    def get_format_name(self):
        """
        Returns the format name of the OptionList.
        """
        return self.format_name

#-------------------------------------------------------------------------
#
# Collection of option lists
#
#-------------------------------------------------------------------------
class OptionListCollection:

    # Default values for common options
    default_style_name = "default"
    default_paper_name = GrampsGconfKeys.get_paper_preference()
    default_template_name = ""
    default_orientation = BaseDoc.PAPER_PORTRAIT
    default_format_name = _('Print...')
    
    def __init__(self,filename=None):
        """
        Creates an OptionListCollection instance from the list defined
        in the specified file.

        filename:   XML file that contains option definitions
        """

        if not filename or not os.path.isfile(filename):
            filename = const.report_options
        self.file = os.path.expanduser(filename)

        self.last_paper_name = self.default_paper_name
        self.last_orientation = self.default_orientation
        self.last_template_name = self.default_template_name
        self.last_format_name = self.default_format_name
        self.option_list_map = {}

        self.parse()
    
    def get_option_list_map(self):
        """
        Returns the map of reports names to option lists.
        """
        return self.option_list_map

    def get_option_list(self,name):
        """
        Returns the option_list associated with the report name

        name:   name associated with the desired report.
        """
        return self.option_list_map.get(name,None)

    def get_report_names(self):
        "Returns a list of all the report names in the OptionListCollection"
        return self.option_list_map.keys()

    def set_option_list(self,name,option_list):
        """
        Adds or replaces an option_list in the OptionListCollection. 

        name:           name assocated with the report to add or replace.
        option_list:    option_list
        """
        self.option_list_map[name] = option_list

    def set_last_paper_name(self,paper_name):
        """
        Sets the last paper name used for the any report in this collection.
        
        paper_name: name of the paper to set.
        """
        self.last_paper_name = paper_name

    def get_last_paper_name(self):
        """
        Returns the last paper name used for the any report in this collection.
        """
        return self.last_paper_name

    def set_last_orientation(self,orientation):
        """
        Sets the last orientation used for the any report in this collection.
        
        orientation: orientation to set.
        """
        self.last_orientation = orientation

    def get_last_orientation(self):
        """
        Returns the last orientation used for the any report in this collection.
        """
        return self.last_orientation

    def set_last_template_name(self,template_name):
        """
        Sets the last template used for the any report in this collection.
        
        template_name: name of the style to set.
        """
        self.last_template_name = template_name

    def get_last_template_name(self):
        """
        Returns the last template used for the any report in this collection.
        """
        return self.last_template_name

    def set_last_format_name(self,format_name):
        """
        Sets the last format used for the any report in this collection.
        
        format_name: name of the format to set.
        """
        self.last_format_name = format_name

    def get_last_format_name(self):
        """
        Returns the last format used for the any report in this collection.
        """
        return self.last_format_name

    def save(self):
        """
        Saves the current OptionListCollection to the associated file.
        """
        f = open(self.file,"w")
        f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        f.write('<reportoptions>\n')

        f.write('<last-common>\n')
        if self.get_last_paper_name() != self.default_paper_name:
            f.write('  <paper name="%s"/>\n' % self.get_last_paper_name() )
        if self.get_last_template_name() != self.default_template_name:
            f.write('  <template name="%s"/>\n' % self.get_last_template_name() )
        if self.get_last_format_name() != self.default_format_name:
            f.write('  <format name="%s"/>\n' % self.get_last_format_name() )
        if self.get_last_orientation() != self.default_orientation:
            f.write('  <orientation value="%d"/>\n' % self.get_last_orientation() )
        f.write('</last-common>\n')
        
        for report_name in self.get_report_names():
            option_list = self.get_option_list(report_name)
            f.write('<report name="%s">\n' % report_name)
            options = option_list.get_options()
            for option_name in options.keys():
                if type(options[option_name]) in (type(list()),type(tuple())):
                    f.write('  <option name="%s" value="" length="%d">\n' % (
                                option_name, len(options[option_name]) ) )
                    for list_index in range(len(options[option_name])):
                        f.write('    <listitem number="%d" value="%s"/>\n' % (
                                list_index, options[option_name][list_index]) )
                    f.write('  </option>\n')
                else:
                    f.write('  <option name="%s" value="%s"/>\n' % (
                            option_name,options[option_name]) )
            if option_list.get_style_name() \
                    and option_list.get_style_name() != self.default_style_name:
                f.write('  <style name="%s"/>\n' % option_list.get_style_name() )
            if option_list.get_paper_name() \
                    and option_list.get_paper_name() != self.default_paper_name:
                f.write('  <paper name="%s"/>\n' % option_list.get_paper_name() )
            if option_list.get_template_name() \
                    and option_list.get_template_name() != self.default_template_name:
                f.write('  <template name="%s"/>\n' % option_list.get_template_name() )
            if option_list.get_format_name() \
                    and option_list.get_format_name() != self.default_format_name:
                f.write('  <format name="%s"/>\n' % option_list.get_format_name() )
            if option_list.get_orientation() \
                    and option_list.get_orientation() != self.default_orientation:
                f.write('  <orientation value="%d"/>\n' % option_list.get_orientation() )
            f.write('</report>\n')

        f.write('</reportoptions>\n')
        f.close()
    
    def parse(self):
        """
        Loads the OptionList from the associated file, if it exists.
        """
        try:
            p = make_parser()
            p.setContentHandler(OptionParser(self))
            p.parse('file://' + self.file)
        except (IOError,OSError,SAXParseException):
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
    
    def __init__(self,collection):
        """
        Creates a OptionParser class that populates the passed collection.

        collection:   BookList to be loaded from the file.
        """
        handler.ContentHandler.__init__(self)
        self.collection = collection
    
        self.rname = None
        self.option_list = None
        self.oname = None
        self.o = None
        self.an_o = None
        self.common = False

    def startElement(self,tag,attrs):
        """
        Overridden class that handles the start of a XML element
        """
        if tag == "report":
            self.rname = attrs['name']
            self.option_list = OptionList()
            self.o = {}
        elif tag == "last-common":
            self.common = True
        elif tag == "option":
            self.oname = attrs['name']
            if attrs.has_key('length'):
                self.an_o = []
            else:
                self.an_o = attrs['value']
        elif tag == "listitem":
            self.an_o.append(attrs['value'])
        elif tag == "style":
            self.option_list.set_style_name(attrs['name'])
        elif tag == "paper":
            if self.common:
                self.collection.set_last_paper_name(attrs['name'])
            else:
                self.option_list.set_paper_name(attrs['name'])
        elif tag == "template":
            if self.common:
                self.collection.set_last_template_name(attrs['name'])
            else:
                self.option_list.set_template_name(attrs['name'])
        elif tag == "format":
            if self.common:
                self.collection.set_last_format_name(attrs['name'])
            else:
                self.option_list.set_format_name(attrs['name'])
        elif tag == "orientation":
            if self.common:
                self.collection.set_last_orientation(int(attrs['value']))
            else:
                self.option_list.set_orientation(int(attrs['value']))

    def endElement(self,tag):
        "Overridden class that handles the end of a XML element"
        if tag == "option":
            self.o[self.oname] = self.an_o
        elif tag == "report":
            self.option_list.set_options(self.o)
            self.collection.set_option_list(self.rname,self.option_list)
        elif tag == "last-common":
            self.common = False

#-------------------------------------------------------------------------
#
# Class handling options for plugins 
#
#-------------------------------------------------------------------------
class OptionHandler:
    """
    Implements handling of the options for the plugins.
    """

    def __init__(self,report_name,options_dict,person_id=None):
        self.report_name = report_name
        self.default_options_dict = options_dict.copy()
        self.options_dict = options_dict

        # These are needed for running reports.
        # We will not need to save/retreive them, just keep around.
        self.doc = None
        self.output = None
        self.newpage = False

        # Retrieve our options from whole collection
        self.option_list_collection = OptionListCollection()
        self.style_name = self.option_list_collection.default_style_name
        self.paper_name = self.option_list_collection.get_last_paper_name()
        self.orientation = self.option_list_collection.get_last_orientation()
        self.template_name = self.option_list_collection.get_last_template_name()
        self.format_name = self.option_list_collection.get_last_format_name()
        self.saved_option_list = self.option_list_collection.get_option_list(report_name)
        self.person_id = person_id

        # Whatever was found should override the defaults
        if self.saved_option_list:
            self.set_options()
        else:
            # If nothing was found, set up the option list 
            self.saved_option_list = OptionList()
            self.option_list_collection.set_option_list(report_name,self.saved_option_list)

    def set_options(self):
        """
        Sets options to be used in this plugin according to the passed
        options dictionary.
        
        Dictionary values are all strings, since they were read from XML.
        Here we need to convert them to the needed types. We use default
        values to determine the type.
        """
        # First we set options_dict values based on the saved options
        options = self.saved_option_list.get_options()
        for option_name in options.keys():
            try:
                converter = Utils.get_type_converter(self.options_dict[option_name])
                self.options_dict[option_name] = converter(options[option_name])
            except ValueError:
                pass

        # Then we set common options from whatever was found
        if self.saved_option_list.get_style_name():
            self.style_name = self.saved_option_list.get_style_name()
        if self.saved_option_list.get_orientation():
            self.orientation = self.saved_option_list.get_orientation()
        if self.saved_option_list.get_template_name():
            self.template_name = self.saved_option_list.get_template_name()
        if self.saved_option_list.get_paper_name():
            self.paper_name = self.saved_option_list.get_paper_name()
        if self.saved_option_list.get_format_name():
            self.format_name = self.saved_option_list.get_format_name()

    def save_options(self):
        """
        Saves options to file.
        
        We need to only store non-default options. Therefore, we remove all
        options whose values are the defaults prior to saving. Also, we save
        the present common options as the last-common for this collection.
        """

        # First we save options from options_dict
        for option_name in self.options_dict.keys():
            if self.options_dict[option_name] == self.default_options_dict[option_name]:
                self.saved_option_list.remove_option(option_name)
            else:
                self.saved_option_list.set_option(option_name,self.options_dict[option_name])

        # Then we save common options
        self.saved_option_list.set_style_name(self.style_name)
        self.saved_option_list.set_orientation(self.orientation)
        self.saved_option_list.set_template_name(self.template_name)
        self.saved_option_list.set_paper_name(self.paper_name)
        self.saved_option_list.set_format_name(self.format_name)
        self.option_list_collection.set_option_list(self.report_name,self.saved_option_list)

        # Then save last-common options from the current selection
        self.option_list_collection.set_last_orientation(self.orientation)
        self.option_list_collection.set_last_template_name(self.template_name)
        self.option_list_collection.set_last_paper_name(self.paper_name)
        self.option_list_collection.set_last_format_name(self.format_name)

        # Finally, save the whole collection into file
        self.option_list_collection.save()

    def get_report_generations(self):
        if self.default_options_dict.has_key('gen'):
            max_gen = self.options_dict.get('gen',
                        self.default_options_dict['gen'])
            page_breaks = self.options_dict.get('pagebbg',
                        self.default_options_dict['pagebbg'])
            return (max_gen,page_breaks)
        else:
            return (0,0)

    def set_report_generations(self,max_gen,page_breaks):
        self.options_dict['gen'] = max_gen
        self.options_dict['pagebbg'] = page_breaks

    def get_stylesheet_savefile(self):
        """Where to save user defined styles for this report."""
        return "%s.xml" % self.report_name

    def get_default_stylesheet_name(self):
        return self.style_name

    def set_default_stylesheet_name(self,style_name):
        self.style_name = style_name

    def get_filter_number(self):
        try:
            return self.options_dict.get('filter',
                    self.default_options_dict['filter'])
        except KeyError:
            return None

    def set_filter_number(self,val):
        self.options_dict['filter'] = val

    def get_format_name(self):
        return self.format_name

    def set_format_name(self,format_name):
        self.format_name = format_name

    def get_paper_name(self):
        return self.paper_name

    def set_paper_name(self,paper_name):
        self.paper_name = paper_name

    def get_template_name(self):
        return self.template_name

    def set_template_name(self,template_name):
        self.template_name = template_name

    def get_orientation(self):
        return self.orientation

    def set_orientation(self,orientation):
        self.orientation = orientation

    def get_person_id(self):
        return self.person_id

    def set_person_id(self,val):
        self.person_id = val

#------------------------------------------------------------------------
#
# Base Options class
#
#------------------------------------------------------------------------
class ReportOptions:

    """
    Defines options and provides handling interface.
    
    This is a base Options class for the reports. All reports' options
    classes should derive from it.
    """

    def __init__(self,name,person_id=None):
        """
        Initializes the class, performing usual house-keeping tasks.
        Subclasses MUST call this in their __init__() method.
        """
        self.set_new_options()
        self.enable_options()

        if self.enable_dict:
            self.options_dict.update(self.enable_dict)
        self.handler = OptionHandler(name,self.options_dict,person_id)

    def set_new_options(self):
        """
        Sets options specific for this report. 
        
        Reports that need custom options need to override this method.
        Two dictionaries MUST be defined here: 

            self.options_dict
                This is a dictionary whose keys are option names
                and values are the default option values.

            self.options_help
                This is a dictionary whose keys are option names
                and values are 3- or 4- lists or tuples:
                    ('=example","Short description",VALUES,DO_PREPEND)
                The VALUES is either a single string (in that case
                the DO_PREPEND does not matter) or a list/tuple of
                strings to list. In that case, if DO_PREPEND evaluates
                as True then each string will be preneded with the ordinal
                number when help is printed on the command line.

        NOTE:   Both dictionaries must have identical keys.

        NOTE:   If a particular report does not use custom options,
                then it should not override this method. 
        """
        self.options_dict = {}
        self.options_help = {}

    def enable_options(self):
        """
        Enables semi-common options for this report.
        
        The semi-common option is the option which GRAMPS is aware of,
        but not common enough to be present in all reports. Here's the list
        of possible keys for semi-commons:
        
            'filter'    - Filter number, selected among filters
                          available for this report. If defined,
                          get_report_filters() method must be defined
                          which returns the list of available filters.

            'gen'       - Maximum number of generations to consider.
            'pagebbg'   - Whether or not make page breaks between generations.
        

        A self.enable_dict dictionary MUST be defined here, whose keys
        are the valid semi-common keys above, and whose values are the
        desired default values for semi-commons.

        NOTE:   If a particular report does not use semi-common options,
                then it should not override this method. 
        """
        self.enable_dict = {}

    def make_default_style(self,default_style):
        """
        Defines default style for this report.
        
        This method MUST be overridden by reports that use the
        user-adjustable paragraph styles.

        NOTE:   Unique names MUST be used for all style names, otherwise the
                styles will collide when making a book with duplicate style
                names. A rule of safety is to prepend style name with the
                acronym based on report name. The following acronyms are
                already taken:
                    AC-     Ancestor Chart
                    AC2-    Ancestor Chart 2 (Wall Chart)
                    AHN-    Ahnentafel Report
                    AR-     Comprehensive Ancestors report
                    CBT-    Custom Book Text
                    DG-     Descendant Graph
                    DR-     Descendant Report
                    DAR-    Detailed Ancestral Report
                    DDR-    Detailed Descendant Report
                    FGR-    Family Group Report
                    FC-     Fan Chart
                    FTA-    FTM Style Ancestral report
                    FTD-    FTM Style Descendant report
                    IDS-    Individual Complete Report
                    IVS-    Individual Summary Report
                    SBT-    Simple Boot Title
                    TLG-    Timeline Graph
        """
        pass

    def add_user_options(self,dialog):
        """
        Sets up UI controls (widgets) for the options specific for this report.

        This method MUST be overridden by reports that define new options.
        The single argument 'dialog' is the Report.BareReportDialog instance.
        Any attribute of the dialog is available.
        
        After the widgets are defined, they MUST be added to the dialog
        using the following call:
                dialog.add_options(LABEL,widget)
        
        NOTE:   To really have any effect besides looking pretty, each widget
                set up here must be also parsed in the parse_user_options()
                method below.
        """
        pass

    def parse_user_options(self,dialog):
        """
        Parses UI controls (widgets) for the options specific for this report.

        This method MUST be overridden by reports that define new options.
        The single argument 'dialog' is the Report.BareReportDialog instance.
        Any attribute of the dialog is available.
        
        After obtaining values from the widgets, they MUST be used to set the
        appropriate options_dict values. Otherwise the values will not have
        any user-visible effect.
        
        NOTE:   Any widget parsed here MUST be defined and added to the dialog
                in the add_user_options() method above.
        """
        pass
    
    def get_document(self):
        """
        Return document instance.
        
        This method MUST NOT be overridden by subclasses.
        """
        return self.handler.doc

    def set_document(self,val):
        """
        Set document to a given instance.
        
        This method MUST NOT be overridden by subclasses.
        """
        self.handler.doc = val

    def get_output(self):
        """
        Return document output destination.
        
        This method MUST NOT be overridden by subclasses.
        """
        return self.handler.output

    def set_output(self,val):
        """
        Set output destination to a given string.
        
        This method MUST NOT be overridden by subclasses.
        """
        self.handler.output = val

    def get_newpage(self):
        """
        Return value of whether or not insert new page before the report.
        
        This method MUST NOT be overridden by subclasses.
        """
        return self.handler.newpage

    def set_newpage(self,val):
        """
        Set newpage to a given value.
        
        This method MUST NOT be overridden by subclasses.
        """
        self.handler.newpage = val

    def get_report_generations(self):
        """
        Return (max_generations,page_breaks) tuple.
        
        This method MUST NOT be overridden by subclasses.
        """
        return self.handler.get_report_generations()

    def get_filter_number(self):
        """
        Return number of a filter to use.
        
        This method MUST NOT be overridden by subclasses.
        """
        return self.handler.get_filter_number()
