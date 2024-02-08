#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2004-2007  Donald N. Allingham
# Copyright (C) 2008,2011  Gary Burton
# Copyright (C) 2010       Jakim Friant
# Copyright (C) 2011-2012  Paul Franklin
# Copyright (C) 2012       Brian G. Matherly
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
Report option handling, including saving and parsing.
"""

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
import os
import copy

# -------------------------------------------------------------------------
#
# SAX interface
#
# -------------------------------------------------------------------------
from xml.sax import make_parser, SAXParseException
from xml.sax.saxutils import escape

# ------------------------------------------------------------------------
#
# Set up logging
#
# ------------------------------------------------------------------------
import logging

LOG = logging.getLogger(".plug.report.options")

# -------------------------------------------------------------------------
#
# gramps modules
#
# (do not import anything from 'gui' as this is in 'gen')
#
# -------------------------------------------------------------------------
from ...const import USER_DATA, REPORT_OPTIONS
from ...config import config
from ..docgen import PAPER_PORTRAIT
from .. import _options
from .. import MenuOptions
from ...utils.cast import get_type_converter


def escxml(word):
    return escape(word, {'"': "&quot;"})


# -------------------------------------------------------------------------
#
# List of options for a single report
#
# -------------------------------------------------------------------------
class OptionList(_options.OptionList):
    """
    Implements a set of options to parse and store for a given report.
    """

    def __init__(self):
        _options.OptionList.__init__(self)
        self.style_name = None
        self.paper_metric = None
        self.paper_name = None
        self.orientation = None
        self.custom_paper_size = [29.7, 21.0]
        self.margins = [2.54, 2.54, 2.54, 2.54]
        self.format_name = None
        self.css_filename = None
        self.output = None

    def set_style_name(self, style_name):
        """
        Set the style name for the OptionList.

        :param style_name: name of the style to set.
        :type style_name: str
        """
        self.style_name = style_name

    def get_style_name(self):
        """
        Return the style name of the OptionList.

        :returns: string representing the style name
        :rtype: str
        """
        return self.style_name

    def set_paper_metric(self, paper_metric):
        """
        Set the paper metric for the OptionList.

        :param paper_metric: whether to use metric.
        :type paper_name: boolean
        """
        self.paper_metric = paper_metric

    def get_paper_metric(self):
        """
        Return the paper metric of the OptionList.

        :returns: returns whether to use metric
        :rtype: boolean
        """
        return self.paper_metric

    def set_paper_name(self, paper_name):
        """
        Set the paper name for the OptionList.

        :param paper_name: name of the paper to set.
        :type paper_name: str
        """
        self.paper_name = paper_name

    def get_paper_name(self):
        """
        Return the paper name of the OptionList.

        :returns: returns the paper name
        :rtype: str
        """
        return self.paper_name

    def set_orientation(self, orientation):
        """
        Set the orientation for the OptionList.

        :param orientation: orientation to set. Possible values are
                            PAPER_LANDSCAPE or PAPER_PORTRAIT
        :type orientation: int
        """
        self.orientation = orientation

    def get_orientation(self):
        """
        Return the orientation for the OptionList.

        :returns: returns the selected orientation. Valid values are
                  PAPER_LANDSCAPE or PAPER_PORTRAIT
        :rtype: int
        """
        return self.orientation

    def set_custom_paper_size(self, paper_size):
        """
        Set the custom paper size for the OptionList.

        :param paper_size: paper size to set in cm.
        :type paper_size: [float, float]
        """
        self.custom_paper_size = paper_size

    def get_custom_paper_size(self):
        """
        Return the custom paper size for the OptionList.

        :returns: returns the custom paper size in cm
        :rtype: [float, float]
        """
        return self.custom_paper_size

    def set_margins(self, margins):
        """
        Set the margins for the OptionList.

        :param margins: margins to set. Possible values are floats in cm
        :type margins: [float, float, float, float]
        """
        self.margins = copy.copy(margins)

    def get_margins(self):
        """
        Return the margins for the OptionList.

        :returns margins: returns the margins, floats in cm
        :rtype margins: [float, float, float, float]
        """
        return copy.copy(self.margins)

    def set_margin(self, pos, value):
        """
        Set a margin for the OptionList.

        :param pos: Position of margin [left, right, top, bottom]
        :type pos: int
        :param value: floating point in cm
        :type value: float
        """
        self.margins[pos] = value

    def get_margin(self, pos):
        """
        Return a margin for the OptionList.

        :param pos: Position of margin [left, right, top, bottom]
        :type pos: int
        :returns: float cm of margin
        :rtype: float
        """
        return self.margins[pos]

    def set_css_filename(self, css_filename):
        """
        Set the template name for the OptionList.

        :param template_name: name of the template to set.
        :type template_name: str
        """
        self.css_filename = css_filename

    def get_css_filename(self):
        """
        Return the template name of the OptionList.

        :returns: template name
        :rtype: str
        """
        return self.css_filename

    def set_format_name(self, format_name):
        """
        Set the format name for the OptionList.

        :param format_name: name of the format to set.
        :type format_name: str
        """
        self.format_name = format_name

    def get_format_name(self):
        """
        Return the format name of the OptionList.

        :returns: returns the format name
        :rtype: str
        """
        return self.format_name

    def set_output(self, output):
        """
        Set the output for the OptionList.

        :param output: name of the output to set.
        :type output: str
        """
        self.output = output

    def get_output(self):
        """
        Return the output of the OptionList.

        :returns: returns the output name
        :rtype: str
        """
        return self.output


# -------------------------------------------------------------------------
#
# Collection of option lists
#
# -------------------------------------------------------------------------
class OptionListCollection(_options.OptionListCollection):
    """
    Implements a collection of option lists.
    """

    def __init__(self, filename):
        _options.OptionListCollection.__init__(self, filename)

    def init_common(self):
        # Default values for common options
        self.default_style_name = "default"
        self.default_paper_metric = config.get("preferences.paper-metric")
        self.default_paper_name = config.get("preferences.paper-preference")
        self.default_orientation = PAPER_PORTRAIT
        self.default_css_filename = ""
        self.default_custom_paper_size = [29.7, 21.0]
        self.default_margins = [2.54, 2.54, 2.54, 2.54]
        self.default_format_name = "print"

        self.last_paper_metric = self.default_paper_metric
        self.last_paper_name = self.default_paper_name
        self.last_orientation = self.default_orientation
        self.last_custom_paper_size = copy.copy(self.default_custom_paper_size)
        self.last_margins = copy.copy(self.default_margins)
        self.last_css_filename = self.default_css_filename
        self.last_format_name = self.default_format_name
        self.option_list_map = {}

    def set_last_paper_metric(self, paper_metric):
        """
        Set the last paper metric used for any report in this collection.

        :param paper_metric: whether to use metric.
        :type paper_name: boolean
        """
        self.last_paper_metric = paper_metric

    def get_last_paper_metric(self):
        """
        Return the last paper metric used for any report in this collection.

        :returns: returns whether or not to use metric
        :rtype: boolean
        """
        return self.last_paper_metric

    def set_last_paper_name(self, paper_name):
        """
        Set the last paper name used for any report in this collection.

        :param paper_name: name of the paper to set.
        :type paper_name: str
        """
        self.last_paper_name = paper_name

    def get_last_paper_name(self):
        """
        Return the last paper name used for any report in this collection.

        :returns: returns the name of the paper
        :rtype: str
        """
        return self.last_paper_name

    def set_last_orientation(self, orientation):
        """
        Set the last orientation used for any report in this collection.

        :param orientation: orientation to set.
        :type orientation: int
        """
        self.last_orientation = orientation

    def get_last_orientation(self):
        """
        Return the last orientation used for any report in this collection.

        :returns: last orientation used
        :rtype: int
        """
        return self.last_orientation

    def set_last_custom_paper_size(self, custom_paper_size):
        """
        Set the last custom paper size used for any report in this collection.

        :param custom_paper_size: size to set in cm (width, height)
        :type custom_paper_size: [float, float]
        """
        self.last_custom_paper_size = copy.copy(custom_paper_size)

    def get_last_custom_paper_size(self):
        """
        Return the last custom paper size used for any report in this
        collection.

        :returns: list of last custom paper size used in cm (width, height)
        :rtype: [float, float]
        """
        return copy.copy(self.last_custom_paper_size)

    def set_last_margins(self, margins):
        """
        Set the last margins used for any report in this collection.

        :param margins: margins to set in cm (left, right, top, bottom)
        :type margins: [float, float, float, float]
        """
        self.last_margins = copy.copy(margins)

    def get_last_margins(self):
        """
        Return the last margins used for any report in this
        collection.

        :returns: list of last margins used in cm (left, right, top, bottom)
        :rtype: [float, float, float, float]
        """
        return copy.copy(self.last_margins)

    def set_last_margin(self, pos, value):
        """
        Set the last margin used for any report in this collection.

        :param pos: pos to set (0-4) (left, right, top, bottom)
        :type pos: int
        :param value: value to set the margin to in cm
        :type value: float
        """
        self.last_margins[pos] = value

    def get_last_margin(self, pos):
        """
        Return the last margins used for any report in this collection.

        :param pos: position in margins list
        :type pos: int
        :returns: last margin used in pos
        :rtype: float
        """
        return self.last_margins[pos]

    def set_last_css_filename(self, css_filename):
        """
        Set the last css used for any report in this collection.

        :param css_filename: name of the style to set.
        """
        self.last_css_name = css_filename

    def get_last_css_filename(self):
        """
        Return the last template used for any report in this collection.
        """
        return self.last_css_filename

    def set_last_format_name(self, format_name):
        """
        Set the last format used for any report in this collection.

        :param format_name: name of the format to set.
        """
        self.last_format_name = format_name

    def get_last_format_name(self):
        """
        Return the last format used for any report in this collection.
        """
        return self.last_format_name

    def write_common(self, file):
        file.write("<last-common>\n")
        if self.get_last_paper_metric() != self.default_paper_metric:
            file.write('  <metric value="%d"/>\n' % self.get_last_paper_metric())
        if self.get_last_custom_paper_size() != self.default_custom_paper_size:
            size = self.get_last_custom_paper_size()
            file.write('  <size value="%f %f"/>\n' % (size[0], size[1]))
        if self.get_last_paper_name() != self.default_paper_name:
            file.write('  <paper name="%s"/>\n' % escxml(self.get_last_paper_name()))
        if self.get_last_css_filename() != self.default_css_filename:
            file.write('  <css name="%s"/>\n' % escxml(self.get_last_css_filename()))
        if self.get_last_format_name() != self.default_format_name:
            file.write('  <format name="%s"/>\n' % escxml(self.get_last_format_name()))
        if self.get_last_orientation() != self.default_orientation:
            file.write('  <orientation value="%d"/>\n' % self.get_last_orientation())
        file.write("</last-common>\n")

    def write_module_common(self, file, option_list):
        if option_list.get_format_name():
            file.write(
                '  <format name="%s"/>\n' % escxml(option_list.get_format_name())
            )
            if option_list.get_format_name() == "html":
                if option_list.get_css_filename():
                    file.write(
                        '  <css name="%s"/>\n' % escxml(option_list.get_css_filename())
                    )
            else:  # not HTML format, therefore it's paper
                if option_list.get_paper_name():
                    file.write(
                        '  <paper name="%s"/>\n' % escxml(option_list.get_paper_name())
                    )
                if option_list.get_orientation() is not None:  # 0 is legal
                    file.write(
                        '  <orientation value="%d"/>\n' % option_list.get_orientation()
                    )
                if option_list.get_paper_metric() is not None:  # 0 is legal
                    file.write(
                        '  <metric value="%d"/>\n' % option_list.get_paper_metric()
                    )
                if option_list.get_custom_paper_size():
                    size = option_list.get_custom_paper_size()
                    file.write('  <size value="%f %f"/>\n' % (size[0], size[1]))
                if option_list.get_margins():
                    margins = option_list.get_margins()
                    for pos, margin in enumerate(margins):
                        file.write(
                            '  <margin number="%s" value="%f"/>\n' % (pos, margin)
                        )

        if option_list.get_style_name():
            file.write('  <style name="%s"/>\n' % escxml(option_list.get_style_name()))
        if option_list.get_output():
            file.write(
                '  <output name="%s"/>\n'
                % escxml(os.path.basename(option_list.get_output()))
            )

    def parse(self):
        """
        Loads the :class:`OptionList` from the associated file, if it exists.
        """
        try:
            if os.path.isfile(self.filename):
                parser = make_parser()
                parser.setContentHandler(OptionParser(self))
                with open(self.filename, encoding="utf-8") as the_file:
                    parser.parse(the_file)
        except (IOError, OSError, SAXParseException):
            pass


# -------------------------------------------------------------------------
#
# OptionParser
#
# -------------------------------------------------------------------------
class OptionParser(_options.OptionParser):
    """
    SAX parsing class for the OptionListCollection XML file.
    """

    def __init__(self, collection):
        """
        Create a OptionParser class that populates the passed collection.

        collection: OptionListCollection to be loaded from the file.
        """
        _options.OptionParser.__init__(self, collection)
        self.common = False
        self.list_class = OptionList

    def startElement(self, tag, attrs):
        """
        Overridden class that handles the start of a XML element
        """
        # First we try report-specific tags
        if tag == "last-common":
            self.common = True
        elif tag == "docgen-option":
            if not self.common:
                self.oname = attrs["name"]
                self.an_o = [attrs["docgen"], attrs["value"]]
        elif tag == "style":
            self.option_list.set_style_name(attrs["name"])
        elif tag == "paper":
            if self.common:
                self.collection.set_last_paper_name(attrs["name"])
            else:
                self.option_list.set_paper_name(attrs["name"])
        elif tag == "css":
            if self.common:
                self.collection.set_last_css_filename(attrs["name"])
            else:
                self.option_list.set_css_filename(attrs["name"])
        elif tag == "format":
            if self.common:
                self.collection.set_last_format_name(attrs["name"])
            else:
                self.option_list.set_format_name(attrs["name"])
        elif tag == "orientation":
            if self.common:
                self.collection.set_last_orientation(int(attrs["value"]))
            else:
                self.option_list.set_orientation(int(attrs["value"]))
        elif tag == "metric":
            if self.common:
                self.collection.set_last_paper_metric(int(attrs["value"]))
            else:
                self.option_list.set_paper_metric(int(attrs["value"]))
        elif tag == "size":
            width, height = attrs["value"].split()
            width = float(width)
            height = float(height)
            if self.common:
                self.collection.set_last_custom_paper_size([width, height])
            else:
                self.option_list.set_custom_paper_size([width, height])

        elif tag == "margin":
            pos, value = int(attrs["number"]), float(attrs["value"])
            if self.common:
                self.collection.set_last_margin(pos, value)
            else:
                self.option_list.set_margin(pos, value)
        elif tag == "output":
            if not self.common:
                self.option_list.set_output(attrs["name"])
        else:
            # Tag is not report-specific, so we let the base class handle it.
            _options.OptionParser.startElement(self, tag, attrs)

    def endElement(self, tag):
        "Overridden class that handles the end of a XML element"
        # First we try report-specific tags
        if tag == "last-common":
            self.common = False
        elif tag == "docgen-option":
            self.odict[self.oname] = self.an_o
        else:
            # Tag is not report-specific, so we let the base class handle it.
            _options.OptionParser.endElement(self, tag)


# ------------------------------------------------------------------------
#
# Empty class to keep the BaseDoc-targeted format happy
# Yes, this is a hack. Find some other way to pass around documents so that
# we don't have to handle them for reports that don't use documents (web)
#
# ------------------------------------------------------------------------
class EmptyDoc:
    def init(self):
        pass

    def set_creator(self, creator):
        pass

    def set_rtl_doc(self, value):  # crock!
        pass

    def open(self, filename):
        pass

    def close(self):
        pass


# -------------------------------------------------------------------------
#
# Class handling options for plugins
#
# -------------------------------------------------------------------------
class OptionHandler(_options.OptionHandler):
    """
    Implements handling of the options for the plugins.
    """

    def __init__(self, module_name, options_dict):
        _options.OptionHandler.__init__(self, module_name, options_dict, None)

    def init_subclass(self):
        self.collection_class = OptionListCollection
        self.list_class = OptionList
        self.filename = REPORT_OPTIONS

    def init_common(self):
        """
        Specific initialization for reports.
        """
        # These are needed for running reports.
        # We will not need to save/retrieve them, just keep around.
        self.doc = EmptyDoc()  # Nasty hack. Text reports replace this
        self.output = None

        # Retrieve our options from whole collection
        self.style_name = self.option_list_collection.default_style_name
        self.paper_metric = self.option_list_collection.get_last_paper_metric()
        self.paper_name = self.option_list_collection.get_last_paper_name()
        self.orientation = self.option_list_collection.get_last_orientation()
        self.custom_paper_size = (
            self.option_list_collection.get_last_custom_paper_size()
        )
        self.css_filename = self.option_list_collection.get_last_css_filename()
        self.margins = self.option_list_collection.get_last_margins()
        self.format_name = self.option_list_collection.get_last_format_name()

    def set_common_options(self):
        if self.saved_option_list.get_style_name():
            self.style_name = self.saved_option_list.get_style_name()
        if self.saved_option_list.get_orientation() is not None:  # 0 is legal
            self.orientation = self.saved_option_list.get_orientation()
        if self.saved_option_list.get_custom_paper_size():
            self.custom_paper_size = self.saved_option_list.get_custom_paper_size()
        if self.saved_option_list.get_margins():
            self.margins = self.saved_option_list.get_margins()
        if self.saved_option_list.get_css_filename():
            self.css_filename = self.saved_option_list.get_css_filename()
        if self.saved_option_list.get_paper_metric() is not None:  # 0 is legal
            self.paper_metric = self.saved_option_list.get_paper_metric()
        if self.saved_option_list.get_paper_name():
            self.paper_name = self.saved_option_list.get_paper_name()
        if self.saved_option_list.get_format_name():
            self.format_name = self.saved_option_list.get_format_name()
        if self.saved_option_list.get_output():
            self.output = self.saved_option_list.get_output()

    def save_options(self):
        """
        Saves options to file.

        """

        # First we save options from options_dict
        for option_name, option_data in self.options_dict.items():
            self.saved_option_list.set_option(
                option_name, self.options_dict[option_name]
            )

        # Handle common options
        self.save_common_options()

        # Finally, save the whole collection into file
        self.option_list_collection.save()

    def save_common_options(self):
        # First we save common options
        self.saved_option_list.set_style_name(self.style_name)
        self.saved_option_list.set_output(self.output)
        self.saved_option_list.set_orientation(self.orientation)
        self.saved_option_list.set_custom_paper_size(self.custom_paper_size)
        self.saved_option_list.set_margins(self.margins)
        self.saved_option_list.set_paper_metric(self.paper_metric)
        self.saved_option_list.set_paper_name(self.paper_name)
        self.saved_option_list.set_css_filename(self.css_filename)
        self.saved_option_list.set_format_name(self.format_name)
        self.option_list_collection.set_option_list(
            self.module_name, self.saved_option_list
        )

        # Then save last-common options from the current selection
        self.option_list_collection.set_last_orientation(self.orientation)
        self.option_list_collection.set_last_custom_paper_size(self.custom_paper_size)
        self.option_list_collection.set_last_margins(self.margins)
        self.option_list_collection.set_last_paper_metric(self.paper_metric)
        self.option_list_collection.set_last_paper_name(self.paper_name)
        self.option_list_collection.set_last_css_filename(self.css_filename)
        self.option_list_collection.set_last_format_name(self.format_name)

    def get_stylesheet_savefile(self):
        """Where to save user defined styles for this report."""
        # Get the first part of name, if it contains a comma:
        # (will just be module_name, if no comma)
        filename = "%s.xml" % self.module_name.split(",")[0]
        return os.path.join(USER_DATA, filename)

    def get_default_stylesheet_name(self):
        """get the default stylesheet name"""
        return self.style_name

    def set_default_stylesheet_name(self, style_name):
        """set the default stylesheet name"""
        self.style_name = style_name

    def get_format_name(self):
        """get the format name"""
        return self.format_name

    def set_format_name(self, format_name):
        """set the format name"""
        self.format_name = format_name

    def get_paper_metric(self):
        """get the paper metric"""
        return self.paper_metric

    def set_paper_metric(self, paper_metric):
        """set the paper metric"""
        self.paper_metric = paper_metric

    def get_paper_name(self):
        """get the paper name"""
        return self.paper_name

    def set_paper_name(self, paper_name):
        """set the paper name"""
        self.paper_name = paper_name

    def get_paper(self):
        """
        This method is for temporary storage, not for saving/restoring.
        """
        return self.paper

    def set_paper(self, paper):
        """
        This method is for temporary storage, not for saving/restoring.
        """
        self.paper = paper

    def get_css_filename(self):
        """get the CSS filename"""
        return self.css_filename

    def set_css_filename(self, css_filename):
        """set the CSS filename"""
        self.css_filename = css_filename

    def get_orientation(self):
        """get the paper's orientation"""
        return self.orientation

    def set_orientation(self, orientation):
        """set the paper's orientation"""
        self.orientation = orientation

    def get_custom_paper_size(self):
        """get the paper's custom paper size, if any"""
        return copy.copy(self.custom_paper_size)

    def set_custom_paper_size(self, custom_paper_size):
        """set the paper's custom paper size"""
        self.custom_paper_size = copy.copy(custom_paper_size)

    def get_margins(self):
        """get the paper's margin sizes"""
        return copy.copy(self.margins)

    def set_margins(self, margins):
        """set the paper's margin sizes"""
        self.margins = copy.copy(margins)


# ------------------------------------------------------------------------
#
# Base Options class
#
# ------------------------------------------------------------------------
class ReportOptions(_options.Options):
    """
    Defines options and provides handling interface.

    This is a base Options class for the reports. All reports, options
    classes should derive from it.
    """

    def __init__(self, name, dbase):
        """
        Initialize the class, performing usual house-keeping tasks.
        Subclasses MUST call this in their :meth:`__init__` method.
        """
        self.name = name
        self.options_dict = {}
        self.options_help = {}
        self.handler = None

    def load_previous_values(self):
        self.handler = OptionHandler(self.name, self.options_dict)

    def make_default_style(self, default_style):
        """
        Defines default style for this report.

        This method MUST be overridden by reports that use the
        user-adjustable paragraph styles.

        .. note:: Unique names MUST be used for all style names, otherwise the
                  styles will collide when making a book with duplicate style
                  names. A rule of safety is to prepend style name with the
                  acronym based on report name.

        The following acronyms are already taken:

        ====    ================================
        Code    Report
        ====    ================================
        AC      Ancestor Chart
        AC2     Ancestor Chart 2 (Wall Chart)
        AHN     Ahnentafel Report
        AR      Comprehensive Ancestors report
        CBT     Custom Book Text
        DG      Descendant Graph
        DR      Descendant Report
        DAR     Detailed Ancestral Report
        DDR     Detailed Descendant Report
        FGR     Family Group Report
        FC      Fan Chart
        FTA     FTM Style Ancestral report
        FTD     FTM Style Descendant report
        IDS     Individual Complete Report
        IDX     Alphabetical Index
        IVS     Individual Summary Report
        PLC     Place Report
        SBT     Simple Book Title
        TLG     Timeline Graph
        TOC     Table Of Contents
        ====    ================================
        """
        pass

    def get_document(self):
        """
        Return document instance.

        .. warning:: This method MUST NOT be overridden by subclasses.
        """
        return self.handler.doc

    def set_document(self, val):
        """
        Set document to a given instance.

        .. warning:: This method MUST NOT be overridden by subclasses.
        """
        self.handler.doc = val

    def get_output(self):
        """
        Return document output destination.

        .. warning:: This method MUST NOT be overridden by subclasses.
        """
        return self.handler.output

    def set_output(self, val):
        """
        Set output destination to a given string.

        .. warning:: This method MUST NOT be overridden by subclasses.
        """
        self.handler.output = val


# -------------------------------------------------------------------------
#
# MenuReportOptions
#
# -------------------------------------------------------------------------
class MenuReportOptions(MenuOptions, ReportOptions):
    """

    The MenuReportOptions class implements the :class:`ReportOptions`
    functionality in a generic way so that the user does not need to
    be concerned with the actual representation of the options.

    The user should inherit the MenuReportOptions class and override the
    add_menu_options function. The user can add options to the menu and the
    MenuReportOptions class will worry about setting up the UI.

    """

    def __init__(self, name, dbase):
        ReportOptions.__init__(self, name, dbase)
        MenuOptions.__init__(self)

    def load_previous_values(self):
        ReportOptions.load_previous_values(self)
        # Pass the loaded values to the menu options so they will be displayed
        # properly.
        for optname in self.options_dict:
            menu_option = self.menu.get_option_by_name(optname)
            if menu_option:
                menu_option.set_value(self.options_dict[optname])

    def get_subject(self):
        """
        Return a string that describes the subject of the report.

        This method MUST be overridden by subclasses.
        """
        LOG.warning("get_subject not implemented for %s" % self.name)
        return ""


# -------------------------------------------------------------------------
#
# DocOptionHandler class
#
# -------------------------------------------------------------------------
class DocOptionHandler(_options.OptionHandler):
    """
    Implements handling of the docgen options for the plugins.
    """

    def __init__(self, module_name, options_dict):
        _options.OptionHandler.__init__(self, module_name, options_dict)

    def init_subclass(self):
        self.collection_class = DocOptionListCollection
        self.list_class = OptionList
        self.filename = REPORT_OPTIONS

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
        docgen_names = self.option_list_collection.docgen_names
        for option_name, option_data in options.items():
            if (
                option_name in self.options_dict
                and isinstance(option_data, list)
                and option_data
                and option_data[0] in docgen_names
            ):
                try:
                    converter = get_type_converter(self.options_dict[option_name])
                    self.options_dict[option_name] = converter(option_data[1])
                except (TypeError, ValueError):
                    pass


# ------------------------------------------------------------------------
#
# DocOptions class
#
# ------------------------------------------------------------------------
class DocOptions(MenuOptions):
    """
    Defines options and provides handling interface.
    """

    def __init__(self, name):
        """
        Initialize the class, performing usual house-keeping tasks.
        Subclasses MUST call this in their :meth:`__init__` method.
        """
        self.name = name
        MenuOptions.__init__(self)

    def load_previous_values(self):
        self.handler = DocOptionHandler(self.name, self.options_dict)


# -------------------------------------------------------------------------
#
# DocOptionListCollection class
#
# -------------------------------------------------------------------------
class DocOptionListCollection(_options.OptionListCollection):
    """
    Implements a collection of option lists.
    """

    def __init__(self, filename):
        _options.OptionListCollection.__init__(self, filename)

    def init_common(self):
        pass

    def parse(self):
        """
        Loads the :class:`OptionList` from the associated file, if it exists.
        """
        try:
            if os.path.isfile(self.filename):
                parser = make_parser()
                parser.setContentHandler(DocOptionParser(self))
                with open(self.filename, encoding="utf-8") as the_file:
                    parser.parse(the_file)
        except (IOError, OSError, SAXParseException):
            pass


# ------------------------------------------------------------------------
#
# DocOptionParser class
#
# ------------------------------------------------------------------------
class DocOptionParser(_options.OptionParser):
    """
    SAX parsing class for the DocOptionListCollection XML file.
    """

    def __init__(self, collection):
        """
        Create a DocOptionParser class that populates the passed collection.

        collection:   DocOptionListCollection to be loaded from the file.
        """
        _options.OptionParser.__init__(self, collection)
        self.list_class = OptionList

    def startElement(self, tag, attrs):
        "Overridden class that handles the start of a XML element"
        if tag == "docgen-option":
            self.oname = attrs["name"]
            self.an_o = [attrs["docgen"], attrs["value"]]
        else:
            _options.OptionParser.startElement(self, tag, attrs)

    def endElement(self, tag):
        "Overridden class that handles the end of a XML element"
        if tag == "docgen-option":
            self.odict[self.oname] = self.an_o
        else:
            _options.OptionParser.endElement(self, tag)
