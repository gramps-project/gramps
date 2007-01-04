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
import RelLib

from _SidebarFilter import SidebarFilter
from Filters import GenericFilterFactory, build_filter_model, Rules
from Filters.Rules.Event import *

GenericEventFilter = GenericFilterFactory('Event')
#-------------------------------------------------------------------------
#
# PersonSidebarFilter class
#
#-------------------------------------------------------------------------
class EventSidebarFilter(SidebarFilter):

    def __init__(self,uistate, clicked):
        SidebarFilter.__init__(self,uistate)
        self.clicked_func = clicked

    def create_widget(self):
        self.filter_id = gtk.Entry()
        self.filter_desc = gtk.Entry()       
        self.filter_event = RelLib.Event()
        self.filter_event.set_type((RelLib.EventType.CUSTOM,''))
        self.etype = gtk.ComboBoxEntry()
       
        self.event_menu = GrampsWidgets.MonitoredDataType(
            self.etype,
            self.filter_event.set_type,
            self.filter_event.get_type)

        self.filter_date = gtk.Entry()
        self.filter_place = gtk.Entry()
        self.filter_note = gtk.Entry()

        self.filter_regex = gtk.CheckButton(_('Use regular expressions'))

	self.generic = gtk.ComboBox()
	cell = gtk.CellRendererText()
	self.generic.pack_start(cell, True)
	self.generic.add_attribute(cell, 'text', 0)
        self.on_filters_changed('Event')

        self.add_text_entry(_('ID'), self.filter_id)
        self.add_text_entry(_('Description'), self.filter_desc)
        self.add_entry(_('Type'), self.etype)
        self.add_text_entry(_('Date'), self.filter_date)
        self.add_text_entry(_('Place'), self.filter_place)
        self.add_text_entry(_('Note'), self.filter_note)
        self.add_entry(_('Custom filter'), self.generic)
        self.add_entry(None, self.filter_regex)

    def clear(self, obj):
        self.filter_id.set_text('')
        self.filter_desc.set_text('')
        self.filter_date.set_text('')
        self.filter_place.set_text('')
        self.filter_note.set_text('')
        self.etype.child.set_text('')
        self.generic.set_active(0)

    def get_filter(self):
        gid = unicode(self.filter_id.get_text()).strip()
        desc = unicode(self.filter_desc.get_text()).strip()
        date = unicode(self.filter_date.get_text()).strip()
        place = unicode(self.filter_place.get_text()).strip()
        note = unicode(self.filter_note.get_text()).strip()
        regex = self.filter_regex.get_active()
	gen = self.generic.get_active() > 0
        etype = self.filter_event.get_type().xml_str()

        empty = not (gid or desc or date or place or note
                     or etype or regex or gen)
        if empty:
            generic_filter = None
        else:
            generic_filter = GenericEventFilter()
            if gid:
                if regex:
                    rule = RegExpIdOf([gid])
                else:
                    rule = HasIdOf([gid])
                generic_filter.add_rule(rule)

            rule = HasEvent([etype,date,place,desc])
            generic_filter.add_rule(rule)
                
            if note:
                if regex:
                    rule = HasNoteRegexp([note])
                else:
                    rule = HasNoteMatchingSubstringOf([note])
                generic_filter.add_rule(rule)

	    if self.generic.get_active() != 0:
		model = self.generic.get_model()
		node = self.generic.get_active_iter()
		obj = model.get_value(node, 0)
		rule = MatchesFilter([obj])
		generic_filter.add_rule(rule)

        return generic_filter

    def on_filters_changed(self,name_space):
        if name_space == 'Event':
            all = GenericEventFilter()
            all.set_name(_("None"))
            all.add_rule(Rules.Event.AllEvents([]))
            self.generic.set_model(build_filter_model('Event', [all]))
            self.generic.set_active(0)
