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

# Written by Alex Roitman

"""
Report option handling, including saving and parsing.
"""

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
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
import Config
import Utils
import BaseDoc
import _Options

#-------------------------------------------------------------------------
#
# List of options for a single report
#
#-------------------------------------------------------------------------
class OptionList(_Options.OptionList):
    """
    Implements a set of options to parse and store for a given report.
    """

    def __init__(self):
        _Options.OptionList.__init__(self)
        self.style_name = None
        self.paper_name = None
        self.orientation = None
        self.template_name = None
        self.format_name = None
    
    def set_style_name(self,style_name):
        """
        Sets the style name for the OptionList.
        @param style_name: name of the style to set.
        @type style_name: str
        """
        self.style_name = style_name

    def get_style_name(self):
        """
        Returns the style name of the OptionList.
        @returns: string representing the style name
        @rtype: str
        """
        return self.style_name

    def set_paper_name(self,paper_name):
        """
        Sets the paper name for the OptionList.
        @param paper_name: name of the paper to set.
        @type paper_name: str
        """
        self.paper_name = paper_name

    def get_paper_name(self):
        """
        Returns the paper name of the OptionList.
        @returns: returns the paper name
        @rtype: str
        """
        return self.paper_name

    def set_orientation(self,orientation):
        """
        Sets the orientation for the OptionList.
        @param orientation: orientation to set. Possible values are
            BaseDoc.PAPER_LANDSCAPE or BaseDoc.PAPER_PORTRAIT
        @type orientation: int
        """
        self.orientation = orientation

    def get_orientation(self):
        """
        Returns the orientation for the OptionList.
        @returns: returns the selected orientation. Valid values are
            BaseDoc.PAPER_LANDSCAPE or BaseDoc.PAPER_PORTRAIT
        @rtype: int
        """
        return self.orientation

    def set_template_name(self,template_name):
        """
        Sets the template name for the OptionList.
        @param template_name: name of the template to set.
        @type template_name: str
        """
        self.template_name = template_name

    def get_template_name(self):
        """
        Returns the template name of the OptionList.
        @returns: template name
        @rtype: str
        """
        return self.template_name

    def set_format_name(self,format_name):
        """
        Sets the format name for the OptionList.
        @param format_name: name of the format to set.
        @type format_name: str
        """
        self.format_name = format_name

    def get_format_name(self):
        """
        Returns the format name of the OptionList.
        @returns: returns the format name
        @rtype: str
        """
        return self.format_name

#-------------------------------------------------------------------------
#
# Collection of option lists
#
#-------------------------------------------------------------------------
class OptionListCollection(_Options.OptionListCollection):
    """
    Implements a collection of option lists.
    """
    def __init__(self,filename):
        _Options.OptionListCollection.__init__(self,filename)

    def init_common(self):
        # Default values for common options
        self.default_style_name = "default"
        self.default_paper_name = Config.get_paper_preference()
        self.default_template_name = ""
        self.default_orientation = BaseDoc.PAPER_PORTRAIT
        self.default_format_name = 'print'

        self.last_paper_name = self.default_paper_name
        self.last_orientation = self.default_orientation
        self.last_template_name = self.default_template_name
        self.last_format_name = self.default_format_name
        self.option_list_map = {}

    def set_last_paper_name(self,paper_name):
        """
        Sets the last paper name used for the any report in this collection.
        @param paper_name: name of the paper to set.
        @type paper_name: str
        """
        self.last_paper_name = paper_name

    def get_last_paper_name(self):
        """
        Returns the last paper name used for the any report in this collection.
        @returns: returns the name of the paper
        @rtype: str
        """
        return self.last_paper_name

    def set_last_orientation(self,orientation):
        """
        Sets the last orientation used for the any report in this collection.
        @param orientation: orientation to set.
        @type orientation: int
        """
        self.last_orientation = orientation

    def get_last_orientation(self):
        """
        Returns the last orientation used for the any report in this
        collection.
        @returns: last orientation used
        @rtype: int
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

    def write_common(self,f):
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

    def write_module_common(self,f,option_list):
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

    def parse(self):
        """
        Loads the OptionList from the associated file, if it exists.
        """
        try:
            p = make_parser()
            p.setContentHandler(OptionParser(self))
            p.parse('file://' + self.filename)
        except (IOError,OSError,SAXParseException):
            pass

#-------------------------------------------------------------------------
#
# OptionParser
#
#-------------------------------------------------------------------------
class OptionParser(_Options.OptionParser):
    """
    SAX parsing class for the OptionListCollection XML file.
    """
    
    def __init__(self,collection):
        """
        Creates a OptionParser class that populates the passed collection.

        collection:   BookList to be loaded from the file.
        """
        _Options.OptionParser.__init__(self,collection)
        self.common = False
        self.list_class = OptionList

    def startElement(self,tag,attrs):
        """
        Overridden class that handles the start of a XML element
        """
        # First we try report-specific tags
        if tag == "last-common":
            self.common = True
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
        else:
            # Tag is not report-specific, so we let the base class handle it.
            OptionParser.startElement(self,tag,attrs)

    def endElement(self,tag):
        "Overridden class that handles the end of a XML element"
        # First we try report-specific tags
        if tag == "last-common":
            self.common = False
        else:
            # Tag is not report-specific, so we let the base class handle it.
            OptionParser.endElement(self,tag)

#-------------------------------------------------------------------------
#
# Class handling options for plugins 
#
#-------------------------------------------------------------------------
class OptionHandler(_Options.OptionHandler):
    """
    Implements handling of the options for the plugins.
    """
    def __init__(self,module_name,options_dict,person_id=None):
        _Options.OptionHandler.__init__(self,module_name,options_dict,person_id)

    def init_subclass(self):
        self.collection_class = OptionListCollection
        self.list_class = OptionList
        self.filename = const.report_options

    def init_common(self):
        """
        Specific initialization for reports.
        """
        # These are needed for running reports.
        # We will not need to save/retreive them, just keep around.
        self.doc = None
        self.output = None
        self.newpage = False

        # Retrieve our options from whole collection
        self.style_name = self.option_list_collection.default_style_name
        self.paper_name = self.option_list_collection.get_last_paper_name()
        self.orientation = self.option_list_collection.get_last_orientation()
        self.template_name = self.option_list_collection.get_last_template_name()
        self.format_name = self.option_list_collection.get_last_format_name()

    def set_common_options(self):
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

    def save_common_options(self):
        # First we save common options
        self.saved_option_list.set_style_name(self.style_name)
        self.saved_option_list.set_orientation(self.orientation)
        self.saved_option_list.set_template_name(self.template_name)
        self.saved_option_list.set_paper_name(self.paper_name)
        self.saved_option_list.set_format_name(self.format_name)
        self.option_list_collection.set_option_list(self.module_name,
                                                    self.saved_option_list)

        # Then save last-common options from the current selection
        self.option_list_collection.set_last_orientation(self.orientation)
        self.option_list_collection.set_last_template_name(self.template_name)
        self.option_list_collection.set_last_paper_name(self.paper_name)
        self.option_list_collection.set_last_format_name(self.format_name)

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
        return "%s.xml" % self.module_name

    def get_default_stylesheet_name(self):
        return self.style_name

    def set_default_stylesheet_name(self,style_name):
        self.style_name = style_name

    def get_display_format(self):
        if self.default_options_dict.has_key('dispf'):
            return self.options_dict.get('dispf',
                    self.default_options_dict['dispf'])
        else:
            return []

    def set_display_format(self,val):
        if type(val) != list:
            val = val.split('\n')
        self.options_dict['dispf'] = val

    def get_format_name(self):
        return self.format_name

    def set_format_name(self,format_name):
        self.format_name = format_name

    def get_paper_name(self):
        return self.paper_name

    def set_paper_name(self,paper_name):
        self.paper_name = paper_name

    def get_paper(self):
        """
        This method is for temporary storage, not for saving/restoring.
        """
        return self.paper

    def set_paper(self,paper):
        """
        This method is for temporary storage, not for saving/restoring.
        """
        self.paper = paper

    def get_template_name(self):
        return self.template_name

    def set_template_name(self,template_name):
        self.template_name = template_name

    def get_orientation(self):
        return self.orientation

    def set_orientation(self,orientation):
        self.orientation = orientation

#------------------------------------------------------------------------
#
# Base Options class
#
#------------------------------------------------------------------------
class ReportOptions(_Options.Options):

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

    def get_display_format(self):
        """
        Return display format for the option box of graphical report.
        
        This method MUST NOT be overridden by subclasses.
        """
        return self.handler.get_display_format()
