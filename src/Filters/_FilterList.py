#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
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

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from xml.sax import make_parser,SAXParseException
import os

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from _FilterParser import FilterParser

#-------------------------------------------------------------------------
#
# FilterList
#
#-------------------------------------------------------------------------
class FilterList:
    """
    Container class for managing the generic filters.
    It stores, saves, and loads the filters.
    """
    
    def __init__(self,file):
        self.filter_namespaces = {}
        self.file = os.path.expanduser(file)

    def get_filters(self,namespace='generic'):
        try:
            return self.filter_namespaces[namespace]
        except KeyError:
            return []

    def add(self,namespace,filt):
        if namespace not in self.filter_namespaces.keys():
            self.filter_namespaces[namespace] = []
        self.filter_namespaces[namespace].append(filt)

    def load(self):
       try:
           if os.path.isfile(self.file):
               parser = make_parser()
               parser.setContentHandler(FilterParser(self))
               parser.parse(self.file)
       except (IOError,OSError):
           pass
       except SAXParseException:
           print "Parser error"

    def fix(self,line):
        l = line.strip()
        l = l.replace('&','&amp;')
        l = l.replace('>','&gt;')
        l = l.replace('<','&lt;')
        return l.replace('"','&quot;')

    def save(self):
        f = open(self.file.encode('utf-8'),'w')
        
        f.write("<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        f.write('<filters>\n')
        for namespace in self.filter_namespaces.keys():
            f.write('<object type="%s">\n' % namespace)
            filter_list = self.filter_namespaces[namespace]
            for the_filter in filter_list:
                f.write('  <filter name="%s"' %self.fix(the_filter.get_name()))
                f.write(' function="%s"' % the_filter.get_logical_op())
                comment = the_filter.get_comment()
                if comment:
                    f.write(' comment="%s"' % self.fix(comment))
                f.write('>\n')
                for rule in the_filter.get_rules():
                    f.write('    <rule class="%s">\n'
                            % rule.__class__.__name__)
                    for v in rule.values():
                        f.write('      <arg value="%s"/>\n' % self.fix(v))
                    f.write('    </rule>\n')
                f.write('  </filter>\n')
            f.write('</object>\n')
        f.write('</filters>\n')
        f.close()
