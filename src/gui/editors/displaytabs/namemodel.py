#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2007  Donald N. Allingham
#               2009       Benny Malengier
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
# python libraries
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK libraries
#
#-------------------------------------------------------------------------
import gtk
from pango import WEIGHT_NORMAL, WEIGHT_BOLD

#-------------------------------------------------------------------------
#
# GRAMPS classes
#
#-------------------------------------------------------------------------
from gen.display.name import displayer as name_displayer

#-------------------------------------------------------------------------
#
# NameModel
#
#-------------------------------------------------------------------------

YES = _('Yes')
NO = _('No')

class NameModel(gtk.TreeStore):
    #tree groups defined
    DEFINDEX = 0
    DEFNAME = _('Preferred name')
    ALTINDEX = 1
    ALTNAME = _('Alternative names')
    
    _GROUPSTRING = _('%(groupname)s - %(groupnumber)d')
    
    COL_NAME = (0, str)
    COL_TYPE = (1, str)
    COL_DATA = (2, object)
    COL_FONTWEIGHT = (3, int)
    COL_GROUPAS = (4, str)
    COL_HASSOURCE = (5, str)
    COL_NOTEPREVIEW = (6, str)
    
    COLS = (COL_NAME, COL_TYPE, COL_DATA, COL_FONTWEIGHT, COL_GROUPAS,
            COL_HASSOURCE, COL_NOTEPREVIEW)

    def __init__(self, obj_list, db, groups):
        """
        @param obj_list: A list of lists, every entry is a group, the entries
            in a group are the data that needs to be shown subordinate to the 
            group
        @param db: a database objects that can be used to obtain info
        @param groups: a list of (key, name) tuples. key is a key for the group
            that might be used. name is the name for the group.
        """
        typeobjs = (x[1] for x in self.COLS)
        gtk.TreeStore.__init__(self, *typeobjs)
        self.db = db
        self.groups = groups
        for index, group in enumerate(obj_list):
            parentiter = self.append(None, row=self.row_group(index, group))
            for obj in group:
                self.append(parentiter, row = self.row(index, obj))

    def row_group(self, index, group):
        name = self.namegroup(index, len(group))
        return [name, '', (index, None), WEIGHT_NORMAL, '', '', '']

    def row(self, index, name):
        """
        Returns the row of the model in group index, and name as a 
        list
        """
        return [name_displayer.display_name(name), 
                str(name.get_type()),
                (index, name), 
                self.colweight(index),
                name.get_group_as(),
                self.hassource(name),
                self.notepreview(name)
               ]
    def colweight(self, index):
        if index == self.DEFINDEX:
            return WEIGHT_BOLD
        else:
            return WEIGHT_NORMAL

    def namegroup(self, groupindex, length):
        if groupindex == self.DEFINDEX:
            return self.DEFNAME
        return self._GROUPSTRING % {'groupname': self.ALTNAME,
                                    'groupnumber': length}
    
    def update_defname(self, defname):
        """
        callback if change to the preferred name happens
        """
        #default name is path (0,0)
        self.remove(self.get_iter((self.DEFINDEX, 0)))
        self.insert(self.get_iter(self.DEFINDEX), 0, 
                    row=self.row(self.DEFINDEX, defname))

    def hassource(self, name):
        if len(name.get_source_references()):
            return YES
        return NO

    def notepreview(self, name):
        nlist = name.get_note_list()
        if nlist:
            note = self.db.get_note_from_handle(nlist[0])
            text = unicode(note.get().replace('\n', ' '))
            if len(text) > 80:
                text = text[:80]+"..."
            return text
        else:
            return ''
