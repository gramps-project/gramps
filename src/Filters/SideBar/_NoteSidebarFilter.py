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

# $Id: _RepoSidebarFilter.py 7866 2007-01-04 05:09:41Z dallingham $

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# gtk
#
#-------------------------------------------------------------------------
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
import GrampsWidgets
from RelLib import Note, NoteType

from _SidebarFilter import SidebarFilter
from Filters import GenericFilterFactory, build_filter_model, Rules
from Filters.Rules.Note import *

GenericNoteFilter = GenericFilterFactory('Note')
#-------------------------------------------------------------------------
#
# PersonSidebarFilter class
#
#-------------------------------------------------------------------------
class NoteSidebarFilter(SidebarFilter):

    def __init__(self, dbstate, uistate, clicked):
        SidebarFilter.__init__(self, dbstate, uistate)
        self.clicked_func = clicked

    def create_widget(self):
        self.filter_id = gtk.Entry()
        self.filter_text = gtk.Entry()

        self.note = Note()
        self.note.set_type((NoteType.CUSTOM,''))
        self.ntype = gtk.ComboBoxEntry()
        self.event_menu = GrampsWidgets.MonitoredDataType(
            self.ntype,
            self.note.set_type,
            self.note.get_type)

        self.filter_regex = gtk.CheckButton(_('Use regular expressions'))

	self.generic = gtk.ComboBox()
	cell = gtk.CellRendererText()
	self.generic.pack_start(cell, True)
	self.generic.add_attribute(cell, 'text', 0)
        self.on_filters_changed('Note')

        self.add_text_entry(_('ID'), self.filter_id)
        self.add_text_entry(_('Text'), self.filter_text)
        self.add_entry(_('Type'), self.ntype)
        self.add_entry(_('Custom filter'), self.generic)
        self.add_entry(None, self.filter_regex)

    def clear(self, obj):
        self.filter_id.set_text('')
        self.filter_text.set_text('')
        self.ntype.child.set_text('')
        self.generic.set_active(0)

    def get_filter(self):
        gid = unicode(self.filter_id.get_text()).strip()
        text = unicode(self.filter_text.get_text()).strip()
        ntype = self.note.get_type().xml_str()
        regex = self.filter_regex.get_active()
        gen = self.generic.get_active() > 0

        empty = not (gid or text or ntype or regex or gen)
        if empty:
            generic_filter = None
        else:
            generic_filter = GenericNoteFilter()
            if gid:
                if regex:
                    rule = RegExpIdOf([gid])
                else:
                    rule = HasIdOf([gid])
                generic_filter.add_rule(rule)

            rule = HasNote([text,ntype])
            generic_filter.add_rule(rule)
                

            if self.generic.get_active() != 0:
                model = self.generic.get_model()
                node = self.generic.get_active_iter()
                obj = model.get_value(node, 0)
                rule = MatchesFilter([obj])
                generic_filter.add_rule(rule)

        return generic_filter
        
    def on_filters_changed(self,name_space):
        if name_space == 'Note':
            all = GenericNoteFilter()
            all.set_name(_("None"))
            all.add_rule(Rules.Note.AllNotes([]))
            self.generic.set_model(build_filter_model('Note', [all]))
            self.generic.set_active(0)
