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
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# gtk
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gui import widgets
import gen.lib
from gui.filters import build_filter_model
from gui.filters.sidebar import SidebarFilter
from gen.filters import GenericFilterFactory, rules
from gen.filters.rules.event import (RegExpIdOf, HasIdOf, HasNoteRegexp, 
                                     HasNoteMatchingSubstringOf, MatchesFilter, 
                                     HasEvent)

GenericEventFilter = GenericFilterFactory('Event')
#-------------------------------------------------------------------------
#
# EventSidebarFilter class
#
#-------------------------------------------------------------------------
class EventSidebarFilter(SidebarFilter):

    def __init__(self, dbstate, uistate, clicked):
        self.clicked_func = clicked
        self.filter_id = widgets.BasicEntry()
        self.filter_desc = widgets.BasicEntry()
        self.filter_event = gen.lib.Event()
        self.filter_event.set_type((gen.lib.EventType.CUSTOM, u''))
        self.etype = Gtk.ComboBox(has_entry=True)
       
        self.event_menu = widgets.MonitoredDataType(
            self.etype,
            self.filter_event.set_type,
            self.filter_event.get_type)
        
        self.filter_mainparts = widgets.BasicEntry()
        self.filter_date = widgets.BasicEntry()
        self.filter_place = widgets.BasicEntry()
        self.filter_note = widgets.BasicEntry()
        
        self.filter_regex = Gtk.CheckButton(_('Use regular expressions'))

        self.generic = Gtk.ComboBox()

        SidebarFilter.__init__(self, dbstate, uistate, "Event")

    def create_widget(self):
        cell = Gtk.CellRendererText()
        cell.set_property('width', self._FILTER_WIDTH)
        cell.set_property('ellipsize', self._FILTER_ELLIPSIZE)
        self.generic.pack_start(cell, True)
        self.generic.add_attribute(cell, 'text', 0)
        self.on_filters_changed('Event')

        self.etype.get_child().set_width_chars(5)

        self.add_text_entry(_('ID'), self.filter_id)
        self.add_text_entry(_('Description'), self.filter_desc)
        self.add_entry(_('Type'), self.etype)
        self.add_text_entry(_('Participants'), self.filter_mainparts)
        self.add_text_entry(_('Date'), self.filter_date)
        self.add_text_entry(_('Place'), self.filter_place)
        self.add_text_entry(_('Note'), self.filter_note)
        self.add_filter_entry(_('Custom filter'), self.generic)
        self.add_regex_entry(self.filter_regex)

    def clear(self, obj):
        self.filter_id.set_text(u'')
        self.filter_desc.set_text(u'')
        self.filter_mainparts.set_text(u'')
        self.filter_date.set_text(u'')
        self.filter_place.set_text(u'')
        self.filter_note.set_text(u'')
        self.etype.get_child().set_text(u'')
        self.generic.set_active(0)

    def get_filter(self):
        gid = unicode(self.filter_id.get_text()).strip()
        desc = unicode(self.filter_desc.get_text()).strip()
        mainparts = unicode(self.filter_mainparts.get_text()).strip()
        date = unicode(self.filter_date.get_text()).strip()
        place = unicode(self.filter_place.get_text()).strip()
        note = unicode(self.filter_note.get_text()).strip()
        regex = self.filter_regex.get_active()
        generic = self.generic.get_active() > 0
        etype = self.filter_event.get_type().xml_str()

        empty = not (gid or desc or mainparts or date or place or note
                     or etype or regex or generic)
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

            rule = HasEvent([etype, date, place, desc, mainparts],
                            use_regex=regex)
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
            obj = unicode(model.get_value(node, 0))
            rule = MatchesFilter([obj])
            generic_filter.add_rule(rule)

        return generic_filter

    def on_filters_changed(self, name_space):
        if name_space == 'Event':
            all_filter = GenericEventFilter()
            all_filter.set_name(_("None"))
            all_filter.add_rule(rules.event.AllEvents([]))
            self.generic.set_model(build_filter_model('Event', [all_filter]))
            self.generic.set_active(0)
