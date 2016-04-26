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

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from xml.sax import make_parser, SAXParseException
import os
import sys
import collections

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ._filterparser import FilterParser
from ..plug import BasePluginManager
from ..const import GRAMPS_LOCALE as glocale

PLUGMAN = BasePluginManager.get_instance()
#-------------------------------------------------------------------------
#
# FilterList
#
#-------------------------------------------------------------------------
class FilterList(object):
    """
    Container class for managing the generic filters.
    It stores, saves, and loads the filters.
    """

    def __init__(self, file):
        self.filter_namespaces = {}
        self.file = os.path.expanduser(file)
        self._cached = {}

    def get_filters_dict(self, namespace='generic'):
        """
        This runs every for every item to be matched!
        """
        if self._cached.get(namespace, None) is None:
            filters = self.get_filters(namespace)
            self._cached[namespace] = dict([(filt.name, filt) for filt
                                            in filters])
        return self._cached[namespace]

    def get_filters(self, namespace='generic'):
        """
        This runs every for every item to be matched!
        """
        if namespace in self.filter_namespaces:
            filters = self.filter_namespaces[namespace]
        else:
            filters = []
        plugins = PLUGMAN.process_plugin_data('Filters')
        if plugins:
            plugin_filters = []
            try:
                for plug in plugins:
                    if isinstance(plug, collections.Callable):
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
        assert(isinstance(namespace, str))

        if namespace not in self.filter_namespaces:
            self.filter_namespaces[namespace] = []
        self.filter_namespaces[namespace].append(filt)

    def load(self):
        try:
            if os.path.isfile(self.file):
                parser = make_parser()
                parser.setContentHandler(FilterParser(self))
                with open(self.file, 'r', encoding='utf8') as the_file:
                    parser.parse(the_file)
        except (IOError, OSError):
            print("IO/OSError in _filterlist.py")
        except SAXParseException:
            print("Parser error")

    def fix(self, line):
        l = line.strip()
        l = l.replace('&', '&amp;')
        l = l.replace('>', '&gt;')
        l = l.replace('<', '&lt;')
        return l.replace('"', '&quot;')

    def save(self):
        with open(self.file, 'w', encoding='utf8') as f:
            f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
            f.write('<filters>\n')
            for namespace in self.filter_namespaces:
                f.write('<object type="%s">\n' % namespace)
                filter_list = self.filter_namespaces[namespace]
                for the_filter in filter_list:
                    f.write('  <filter name="%s"' %self.fix(the_filter.get_name()))
                    f.write(' function="%s"' % the_filter.get_logical_op())
                    if the_filter.invert:
                        f.write(' invert="1"')
                    comment = the_filter.get_comment()
                    if comment:
                        f.write(' comment="%s"' % self.fix(comment))
                    f.write('>\n')
                    for rule in the_filter.get_rules():
                        f.write('    <rule class="%s" use_regex="%s">\n'
                                % (rule.__class__.__name__, rule.use_regex))
                        for value in list(rule.values()):
                            f.write('      <arg value="%s"/>\n' % self.fix(value))
                        f.write('    </rule>\n')
                    f.write('  </filter>\n')
                f.write('</object>\n')
            f.write('</filters>\n')
