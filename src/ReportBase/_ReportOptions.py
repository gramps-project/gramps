#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007  Donald N. Allingham
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
import copy
from xml.sax.saxutils import escape

def escxml(d):
    return escape(d, { '"' : '&quot;' } )

#-------------------------------------------------------------------------
#
# SAX interface
#
#-------------------------------------------------------------------------
try:
    from xml.sax import make_parser, SAXParseException
except:
    from _xmlplus.sax import make_parser, SAXParseException

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import const
import Config
import BaseDoc
from PluginUtils import _Options, MenuOptions

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
        self.paper_metric = None
        self.paper_name = None
        self.orientation = None
        self.custom_paper_size = [29.7, 21.0]
        self.margins = [2.54, 2.54, 2.54, 2.54]
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

    def set_paper_metric(self,paper_metric):
        """
        Sets the paper metric for the OptionList.
        @param paper_metric: whether to use metric.
        @type paper_name: boolean
        """
        self.paper_metric = paper_metric

    def get_paper_metric(self):
        """
        Returns the paper metric of the OptionList.
        @returns: returns whether to use metric
        @rtype: boolean
        """
        return self.paper_metric

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

    def set_custom_paper_size(self,paper_size):
        """
        Sets the custom paper size for the OptionList.
        @param paper_size: paper size to set in cm.
        @type paper_size: [float, float]
        """
        self.custom_paper_size = paper_size

    def get_custom_paper_size(self):
        """
        Returns the custom paper size for the OptionList.
        @returns: returns the custom paper size in cm
        @rtype: [float, float]
        """
        return self.custom_paper_size

    def set_margins(self,margins):
        """
        Sets the margins for the OptionList.
        @param margins: margins to set. Possible values are floats in cm
        @type margins: [float, float, float, float]
        """
        self.margins = copy.copy(margins)

    def get_margins(self):
        """
        Returns the margins for the OptionList.
        @returns margins: returns the margins, floats in cm
        @rtype margins: [float, float, float, float]
        """
        return copy.copy(self.margins)

    def set_margin(self,pos,value):
        """
        Sets a margin for the OptionList.
        @param pos: Position of margin [left, right, top, bottom]
        @param value: floating point in cm
        @type pos: int
        @type value: float
        """
        self.margins[pos] = value

    def get_margin(self,pos):
        """
        Returns a margin for the OptionList.
        @param pos: Position of margin [left, right, top, bottom]
        @type pos: int
        @returns: float cm of margin
        @rtype: float
        """
        return self.margins[pos]

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
        self.default_paper_metric = Config.get(Config.PAPER_METRIC)
        self.default_paper_name = Config.get(Config.PAPER_PREFERENCE)
        self.default_template_name = ""
        self.default_orientation = BaseDoc.PAPER_PORTRAIT
        self.default_custom_paper_size = [29.7, 21.0]
        self.default_margins = [2.54, 2.54, 2.54, 2.54]
        self.default_format_name = 'print'

        self.last_paper_metric = self.default_paper_metric
        self.last_paper_name = self.default_paper_name
        self.last_orientation = self.default_orientation
        self.last_custom_paper_size = copy.copy(self.default_custom_paper_size)
        self.last_margins = copy.copy(self.default_margins)
        self.last_template_name = self.default_template_name
        self.last_format_name = self.default_format_name
        self.option_list_map = {}

    def set_last_paper_metric(self,paper_metric):
        """
        Sets the last paper metric used for the any report in this collection.
        @param paper_metric: whether to use metric.
        @type paper_name: boolean
        """
        self.last_paper_metric = paper_metric

    def get_last_paper_metric(self):
        """
        Returns the last paper metric used for the any report in this collection.
        @returns: returns whether or not to use metric
        @rtype: boolean
        """
        return self.last_paper_metric

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

    def set_last_custom_paper_size(self,custom_paper_size):
        """
        Sets the last custom paper size used for the any report in this collection.
        @param custom_paper_size: size to set in cm (width, height)
        @type margins: [float, float]
        """
        self.last_custom_paper_size = copy.copy(custom_paper_size)

    def get_last_custom_paper_size(self):
        """
        Returns the last custom paper size used for the any report in this
        collection.
        @returns: list of last custom paper size used in cm (width, height)
        @rtype: [float, float]
        """
        return copy.copy(self.last_custom_paper_size)

    def set_last_margins(self,margins):
        """
        Sets the last margins used for the any report in this collection.
        @param margins: margins to set in cm (left, right, top, bottom)
        @type margins: [float, float, float, float]
        """
        self.last_margins = copy.copy(margins)

    def get_last_margins(self):
        """
        Returns the last margins used for the any report in this
        collection.
        @returns: list of last margins used in cm (left, right, top, bottom)
        @rtype: [float, float, float, float]
        """
        return copy.copy(self.last_margins)

    def set_last_margin(self,pos,value):
        """
        Sets the last margin used for the any report in this collection.
        @param pos: pos to set (0-4) (left, right, top, bottom)
        @type pos: int
        @param value: value to set the margin to in cm
        @type value: float
        """
        self.last_margins[pos] = value

    def get_last_margin(self,pos):
        """
        Returns the last margins used for the any report in this
        collection.
        @param pos: position in margins list
        @type pos: int
        @returns: last margin used in pos
        @rtype: float
        """
        return self.last_margins[pos]

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
        if self.get_last_paper_metric() != self.default_paper_metric:
            f.write('  <metric value="%d"/>\n' % self.get_last_paper_metric() )
        if self.get_last_custom_paper_size() != self.default_custom_paper_size:
            size = self.get_last_custom_paper_size()
            f.write('  <size value="%f %f"/>\n' % (size[0], size[1]) )
        if self.get_last_paper_name() != self.default_paper_name:
            f.write('  <paper name="%s"/>\n' % escxml(self.get_last_paper_name()) )
        if self.get_last_template_name() != self.default_template_name:
            f.write('  <template name="%s"/>\n' % escxml(self.get_last_template_name()) )
        if self.get_last_format_name() != self.default_format_name:
            f.write('  <format name="%s"/>\n' % escxml(self.get_last_format_name()) )
        if self.get_last_orientation() != self.default_orientation:
            f.write('  <orientation value="%d"/>\n' % self.get_last_orientation() )
        f.write('</last-common>\n')

    def write_module_common(self,f,option_list):
        if option_list.get_style_name() \
               and option_list.get_style_name() != self.default_style_name:
            f.write('  <style name="%s"/>\n' % escxml(option_list.get_style_name()) )
        if option_list.get_paper_metric() \
               and option_list.get_paper_metric() != self.default_paper_metric:
            f.write('  <metric value="%d"/>\n' % option_list.get_paper_metric() )
        if option_list.get_custom_paper_size() \
                and option_list.get_custom_paper_size() != self.default_custom_paper_size:
            size = self.get_last_custom_paper_size()
            f.write('  <size value="%f %f"/>\n' % (size[0], size[1]) )
        if option_list.get_paper_name() \
               and option_list.get_paper_name() != self.default_paper_name:
            f.write('  <paper name="%s"/>\n' % escxml(option_list.get_paper_name()) )
        if option_list.get_template_name() \
               and option_list.get_template_name() != self.default_template_name:
            f.write('  <template name="%s"/>\n' % escxml(option_list.get_template_name()) )
        if option_list.get_format_name() \
               and option_list.get_format_name() != self.default_format_name:
            f.write('  <format name="%s"/>\n' % escxml(option_list.get_format_name()) )
        if option_list.get_orientation() \
               and option_list.get_orientation() != self.default_orientation:
            f.write('  <orientation value="%d"/>\n' % option_list.get_orientation() )
        if option_list.get_margins() \
               and option_list.get_margins() != self.default_margins:
            margins = option_list.get_margins()
            for pos in range(len(margins)): 
                f.write('  <margin number="%s" value="%f"/>\n' % (pos, margins[pos]))

    def parse(self):
        """
        Loads the OptionList from the associated file, if it exists.
        """
        try:
            if os.path.isfile(self.filename):
                p = make_parser()
                p.setContentHandler(OptionParser(self))
                the_file = open(self.filename)
                p.parse(the_file)
                the_file.close()
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
        elif tag == "metric":
            if self.common:
                self.collection.set_last_paper_metric(int(attrs['value']))
            else:
                self.option_list.set_paper_metric(int(attrs['value']))
        elif tag == "size":
            width, height = attrs['value'].split()
            width = float(width)
            height = float(height)
            if self.common:
                self.collection.set_last_custom_paper_size([width, height])
            else:
                self.option_list.set_custom_paper_size([width, height])

        elif tag == "margin":
            pos, value = int(attrs['number']), float(attrs['value'])
            if self.common:
                self.collection.set_last_margin(pos, value)
            else:
                self.option_list.set_margin(pos, value)
        else:
            # Tag is not report-specific, so we let the base class handle it.
            _Options.OptionParser.startElement(self,tag,attrs)

    def endElement(self,tag):
        "Overridden class that handles the end of a XML element"
        # First we try report-specific tags
        if tag == "last-common":
            self.common = False
        else:
            # Tag is not report-specific, so we let the base class handle it.
            _Options.OptionParser.endElement(self,tag)

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
        self.filename = const.REPORT_OPTIONS

    def init_common(self):
        """
        Specific initialization for reports.
        """
        # These are needed for running reports.
        # We will not need to save/retreive them, just keep around.
        self.doc = None
        self.output = None

        # Retrieve our options from whole collection
        self.style_name = self.option_list_collection.default_style_name
        self.paper_metric = self.option_list_collection.get_last_paper_metric()
        self.paper_name = self.option_list_collection.get_last_paper_name()
        self.orientation = self.option_list_collection.get_last_orientation()
        self.custom_paper_size = self.option_list_collection.get_last_custom_paper_size()
        self.margins = self.option_list_collection.get_last_margins()
        self.template_name = self.option_list_collection.get_last_template_name()
        self.format_name = self.option_list_collection.get_last_format_name()

    def set_common_options(self):
        if self.saved_option_list.get_style_name():
            self.style_name = self.saved_option_list.get_style_name()
        if self.saved_option_list.get_orientation():
            self.orientation = self.saved_option_list.get_orientation()
        if self.saved_option_list.get_custom_paper_size():
            self.custom_paper_size = self.saved_option_list.get_custom_paper_size()
        if self.saved_option_list.get_margins():
            self.margins = self.saved_option_list.get_margins()
        if self.saved_option_list.get_template_name():
            self.template_name = self.saved_option_list.get_template_name()
        if self.saved_option_list.get_paper_metric():
            self.paper_metric = self.saved_option_list.get_paper_metric()
        if self.saved_option_list.get_paper_name():
            self.paper_name = self.saved_option_list.get_paper_name()
        if self.saved_option_list.get_format_name():
            self.format_name = self.saved_option_list.get_format_name()

    def save_common_options(self):
        # First we save common options
        self.saved_option_list.set_style_name(self.style_name)
        self.saved_option_list.set_orientation(self.orientation)
        self.saved_option_list.set_custom_paper_size(self.custom_paper_size)
        self.saved_option_list.set_margins(self.margins)
        self.saved_option_list.set_template_name(self.template_name)
        self.saved_option_list.set_paper_metric(self.paper_metric)
        self.saved_option_list.set_paper_name(self.paper_name)
        self.saved_option_list.set_format_name(self.format_name)
        self.option_list_collection.set_option_list(self.module_name,
                                                    self.saved_option_list)

        # Then save last-common options from the current selection
        self.option_list_collection.set_last_orientation(self.orientation)
        self.option_list_collection.set_last_custom_paper_size(self.custom_paper_size)
        self.option_list_collection.set_last_margins(self.margins)
        self.option_list_collection.set_last_template_name(self.template_name)
        self.option_list_collection.set_last_paper_metric(self.paper_metric)
        self.option_list_collection.set_last_paper_name(self.paper_name)
        self.option_list_collection.set_last_format_name(self.format_name)

    def get_stylesheet_savefile(self):
        """Where to save user defined styles for this report."""
        return "%s.xml" % self.module_name

    def get_default_stylesheet_name(self):
        return self.style_name

    def set_default_stylesheet_name(self,style_name):
        self.style_name = style_name

    def get_format_name(self):
        return self.format_name

    def set_format_name(self,format_name):
        self.format_name = format_name

    def get_paper_metric(self):
        return self.paper_metric

    def set_paper_metric(self,paper_metric):
        self.paper_metric = paper_metric

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

    def get_custom_paper_size(self):
        return copy.copy(self.custom_paper_size)

    def set_custom_paper_size(self,custom_paper_size):
        self.custom_paper_size = copy.copy(custom_paper_size)

    def get_margins(self):
        return copy.copy(self.margins)

    def set_margins(self,margins):
        self.margins = copy.copy(margins)

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
        self.name = name
        self.person_id = person_id
        self.options_dict = {}
        self.options_help = {}
        self.handler = None
        
    def load_previous_values(self):
        self.handler = OptionHandler(self.name,self.options_dict,self.person_id)

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

#-------------------------------------------------------------------------
#
# MenuReportOptions
#
#-------------------------------------------------------------------------
class MenuReportOptions(MenuOptions,ReportOptions):
    """

    The MenuReportOptions class implementes the ReportOptions
    functionality in a generic way so that the user does not need to
    be concerned with the graphical representation of the options.
    
    The user should inherit the MenuReportOptions class and override the 
    add_menu_options function. The user can add options to the menu and the 
    MenuReportOptions class will worry about setting up the GUI.

    """
    def __init__(self,name,dbstate=None):
        if dbstate:
            active_person = dbstate.get_active_person().get_gramps_id()
        else:
            active_person = None
        ReportOptions.__init__(self,name,active_person)
        MenuOptions.__init__(self,dbstate)
        
    def load_previous_values(self):
        ReportOptions.load_previous_values(self)
        # Pass the loaded values to the menu options so they will be displayed properly.
        for optname in self.options_dict:
            menu_option = self.menu.get_option_by_name(optname)
            menu_option.set_value(self.options_dict[optname])

