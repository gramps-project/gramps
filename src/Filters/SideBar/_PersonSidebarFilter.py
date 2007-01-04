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
from Filters.Rules.Person import *
from Filters import GenericFilter, build_filter_model, Rules

#-------------------------------------------------------------------------
#
# PersonSidebarFilter class
#
#-------------------------------------------------------------------------
class PersonSidebarFilter(SidebarFilter):

    def __init__(self,uistate,clicked):
        SidebarFilter.__init__(self,uistate)
        self.clicked_func = clicked

    def create_widget(self):
        self.filter_name = gtk.Entry()
        self.filter_id = gtk.Entry()
        self.filter_birth = gtk.Entry()
        self.filter_death = gtk.Entry()
        self.filter_event = RelLib.Event()
        self.filter_event.set_type((RelLib.EventType.CUSTOM,''))
        self.etype = gtk.ComboBoxEntry()
        self.event_menu = GrampsWidgets.MonitoredDataType(
            self.etype,
            self.filter_event.set_type,
            self.filter_event.get_type)

        self.filter_marker = RelLib.Person()
        self.filter_marker.set_marker((RelLib.MarkerType.CUSTOM,''))
        self.mtype = gtk.ComboBoxEntry()
        self.marker_menu = GrampsWidgets.MonitoredDataType(
            self.mtype,
            self.filter_marker.set_marker,
            self.filter_marker.get_marker)

        self.filter_note = gtk.Entry()
        self.filter_gender = gtk.combo_box_new_text()
        for i in [ _('any'), _('male'), _('female'), _('unknown') ]:
            self.filter_gender.append_text(i)
        self.filter_gender.set_active(0)
            
        self.filter_regex = gtk.CheckButton(_('Use regular expressions'))

        self.generic = gtk.ComboBox()
        cell = gtk.CellRendererText()
        self.generic.pack_start(cell, True)
        self.generic.add_attribute(cell, 'text', 0)
        self.on_filters_changed('Person')

        self.add_text_entry(_('Name'), self.filter_name)
        self.add_text_entry(_('ID'), self.filter_id)
        self.add_entry(_('Gender'), self.filter_gender)
        self.add_text_entry(_('Birth date'), self.filter_birth)
        self.add_text_entry(_('Death date'), self.filter_death)
        self.add_entry(_('Event'), self.etype)
        self.add_entry(_('Marker'), self.mtype)
        self.add_text_entry(_('Note'), self.filter_note)
        self.add_entry(_('Custom filter'), self.generic)
        self.add_entry(None, self.filter_regex)

    def clear(self, obj):
        self.filter_name.set_text('')
        self.filter_id.set_text('')
        self.filter_birth.set_text('')
        self.filter_death.set_text('')
        self.filter_note.set_text('')
        self.filter_gender.set_active(0)
        self.etype.child.set_text('')
        self.mtype.child.set_text('')
        self.generic.set_active(0)

    def get_filter(self):
        name = unicode(self.filter_name.get_text()).strip()
        gid = unicode(self.filter_id.get_text()).strip()
        birth = unicode(self.filter_birth.get_text()).strip()
        death = unicode(self.filter_death.get_text()).strip()
        etype = self.filter_event.get_type().xml_str()
        mtype = self.filter_marker.get_marker().xml_str()
        note = unicode(self.filter_note.get_text()).strip()
        gender = self.filter_gender.get_active()
        regex = self.filter_regex.get_active()
        gen = self.generic.get_active() > 0

        empty = not (name or gid or birth or death or etype or mtype 
                     or note or gender or regex or gen)
        if empty:
            generic_filter = None
        else:
            generic_filter = GenericFilter()
            if name:
                if regex:
                    rule = RegExpName([name])
                else:
                    rule = SearchName([name])
                generic_filter.add_rule(rule)
            if gid:
                if regex:
                    rule = RegExpIdOf([gid])
                else:
                    rule = MatchIdOf([gid])
                generic_filter.add_rule(rule)

            if gender > 0:
                if gender == 1:
                    generic_filter.add_rule(IsMale([]))
                elif gender == 2:
                    generic_filter.add_rule(IsFemale([]))
                else:
                    generic_filter.add_rule(HasUnknownGender([]))

            if mtype:
                rule = HasMarkerOf([mtype])
                generic_filter.add_rule(rule)
                
            if etype:
                rule = HasEvent([etype, '', '', ''])
                generic_filter.add_rule(rule)
                
            if birth:
                rule = HasBirth([birth,'',''])
                generic_filter.add_rule(rule)
            if death:
                rule = HasDeath([death,'',''])
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
        if name_space == 'Person':
            all = GenericFilter()
            all.set_name(_("None"))
            all.add_rule(Rules.Person.Everyone([]))
            self.generic.set_model(build_filter_model('Person', [all]))
            self.generic.set_active(0)
