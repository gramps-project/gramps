#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000  Donald N. Allingham
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

import RelLib
import WriteXML
import ReadXML
import const

class GrampsXML(RelLib.GrampsDB):

    def get_base(self):
        return const.xmlFile

    def get_type(self):
        return 'GrampsXML'

    def new(self):
        RelLib.GrampsDB.new(self)
        
    def save(self,name,callback):
        WriteXML.exportData(self,name,callback)
        
    def load(self,name,callback):
        ReadXML.loadData(self,name,callback)
#         for key in self.person_map.keys():
#             data = self.person_map[key]
#             name = data[2]
#             print key,data
#             self.add_surname(name.get_surname())
        
        return 1
