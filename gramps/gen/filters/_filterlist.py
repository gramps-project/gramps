#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2007  Donald N. Allingham
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

""" Container class for managing the generic filters """

# -------------------------------------------------------------------------
#
# Standard Python modules
#
# -------------------------------------------------------------------------
from xml.sax import make_parser, SAXParseException
import os
from collections import abc

# -------------------------------------------------------------------------
#
# Gramps modules
#
# -------------------------------------------------------------------------
from ._filterparser import FilterParser
from ..plug import BasePluginManager
from ..const import GRAMPS_LOCALE as glocale

PLUGMAN = BasePluginManager.get_instance()


# -------------------------------------------------------------------------
#
# FilterList
#
# -------------------------------------------------------------------------
class FilterList:
    """
    Container class for managing the generic filters.
    It stores, saves, and loads the filters.
    """

    def __init__(self, file):
        self.filter_namespaces = {}
        self.file = os.path.expanduser(file)
        self._cached = {}

    def get_filters_dict(self, namespace="generic"):
        """
        This runs every for every item to be matched!
        """
        if self._cached.get(namespace, None) is None:
            filters = self.get_filters(namespace)
            self._cached[namespace] = dict([(filt.name, filt) for filt in filters])
        return self._cached[namespace]

    def get_filters(self, namespace="generic"):
        """
        This runs every for every item to be matched!
        """
        if namespace in self.filter_namespaces:
            filters = self.filter_namespaces[namespace]
        else:
            filters = []
        plugins = PLUGMAN.process_plugin_data("Filters")
        if plugins:
            plugin_filters = []
            try:
                for plug in plugins:
                    if isinstance(plug, abc.Callable):
                        plug = plug(namespace)
                    if plug:
                        if isinstance(plug, (list, tuple)):
                            for subplug in plug:
                                plugin_filters.append(subplug)
                        else:
                            plugin_filters.append(plug)
            except:
                import traceback

                traceback.print_exc()
            filters += plugin_filters
        return filters

    def add(self, namespace, filt):
        """add a custom filter"""
        assert isinstance(namespace, str)

        if namespace not in self.filter_namespaces:
            self.filter_namespaces[namespace] = []
        self.filter_namespaces[namespace].append(filt)

    def load(self):
        """load a custom filter"""
        try:
            if os.path.isfile(self.file):
                parser = make_parser()
                parser.setContentHandler(FilterParser(self))
                with open(self.file, "r", encoding="utf8") as the_file:
                    parser.parse(the_file)
        except (IOError, OSError):
            print("IO/OSError in _filterlist.py")
        except SAXParseException:
            print("Parser error")

    def fix(self, line):
        """sanitize the custom filter name, if needed"""
        new_line = line.strip()
        new_line = new_line.replace("&", "&amp;")
        new_line = new_line.replace(">", "&gt;")
        new_line = new_line.replace("<", "&lt;")
        return new_line.replace('"', "&quot;")

    def save(self):
        """save the list of custom filters"""
        with open(self.file, "w", encoding="utf8") as file:
            file.write('<?xml version="1.0" encoding="utf-8"?>\n')
            file.write("<filters>\n")
            for namespace in self.filter_namespaces:
                file.write('  <object type="%s">\n' % namespace)
                filter_list = self.filter_namespaces[namespace]
                sorted_filters = sorted(
                    [(filter.get_name(), filter) for filter in filter_list],
                    key=lambda x: glocale.sort_key(x[0]),
                )
                for name, the_filter in sorted_filters:  # enable a diff
                    file.write('    <filter name="%s"' % self.fix(name))
                    file.write(' function="%s"' % the_filter.get_logical_op())
                    if the_filter.invert:
                        file.write(' invert="1"')
                    comment = the_filter.get_comment()
                    if comment:
                        file.write(' comment="%s"' % self.fix(comment))
                    file.write(">\n")
                    for rule in the_filter.get_rules():
                        file.write(
                            '      <rule class="%s" use_regex="%s" use_case="%s">'
                            "\n"
                            % (rule.__class__.__name__, rule.use_regex, rule.use_case)
                        )
                        for value in list(rule.values()):
                            file.write(
                                '        <arg value="%s"/>' "\n" % self.fix(value)
                            )
                        file.write("      </rule>\n")
                    file.write("    </filter>\n")
                file.write("  </object>\n")
            file.write("</filters>\n")
