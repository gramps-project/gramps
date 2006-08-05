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
from Filters.Rules.Family import *

GenericFamilyFilter = GenericFilterFactory('Family')
#-------------------------------------------------------------------------
#
# PersonSidebarFilter class
#
#-------------------------------------------------------------------------
class FamilySidebarFilter(SidebarFilter):

    def __init__(self, clicked):
        SidebarFilter.__init__(self)
        self.clicked_func = clicked

    def create_widget(self):
        self.filter_id = gtk.Entry()
        self.filter_father = gtk.Entry()
        self.filter_mother = gtk.Entry()
        self.filter_child = gtk.Entry()
        
        self.filter_event = RelLib.Event()
        self.filter_event.set_type((RelLib.EventType.CUSTOM,''))
        self.etype = gtk.ComboBoxEntry()

        self.family_stub = RelLib.Family()
        self.family_stub.set_relationship((RelLib.FamilyRelType.CUSTOM,''))
        self.rtype = gtk.ComboBoxEntry()
        
        self.event_menu = GrampsWidgets.MonitoredDataType(
            self.etype,
            self.filter_event.set_type,
            self.filter_event.get_type)

        self.rel_menu = GrampsWidgets.MonitoredDataType(
            self.rtype,
            self.family_stub.set_relationship,
            self.family_stub.get_relationship)
        
        self.filter_note = gtk.Entry()
            
        self.filter_regex = gtk.CheckButton(_('Use regular expressions'))

        all = GenericFamilyFilter()
        all.set_name(_("None"))
        all.add_rule(Rules.Family.AllFamilies([]))

	self.generic = gtk.ComboBox()
	cell = gtk.CellRendererText()
	self.generic.pack_start(cell, True)
	self.generic.add_attribute(cell, 'text', 0)
	self.generic.set_model(build_filter_model('Family', [all]))
	self.generic.set_active(0)

        self.add_text_entry(_('ID'), self.filter_id)
        self.add_text_entry(_('Father'), self.filter_father)
        self.add_text_entry(_('Mother'), self.filter_mother)
        self.add_text_entry(_('Child'), self.filter_child)
        self.add_entry(_('Relationship'), self.rtype)
        self.add_entry(_('Family Event'), self.etype)
        self.add_text_entry(_('Family Note'), self.filter_note)
        self.add_entry(_('Custom filter'), self.generic)
        self.add_entry(None, self.filter_regex)

    def clear(self, obj):
        self.filter_id.set_text('')
        self.filter_father.set_text('')
        self.filter_mother.set_text('')
        self.filter_child.set_text('')
        self.filter_note.set_text('')
        self.etype.child.set_text('')
        self.rtype.child.set_text('')
        self.generic.set_active(0)

    def clicked(self, obj):
        self.clicked_func()

    def get_filter(self):
        gid = unicode(self.filter_id.get_text()).strip()
        father = unicode(self.filter_father.get_text()).strip()
        mother = unicode(self.filter_mother.get_text()).strip()
        child = unicode(self.filter_child.get_text()).strip()
        note = unicode(self.filter_note.get_text()).strip()
        etype = self.filter_event.get_type().xml_str()
        rtype = self.family_stub.get_relationship().xml_str()
        regex = self.filter_regex.get_active()
	gen = self.generic.get_active() > 0

        empty = not (gid or father or mother or child or note
                     or regex or etype or rtype or gen)
        if empty:
            generic_filter = None
        else:
            generic_filter = GenericFamilyFilter()
            if gid:
                if regex:
                    rule = RegExpIdOf([gid])
                else:
                    rule = HasIdOf([gid])
                generic_filter.add_rule(rule)

            if father:
                rule = SearchFatherName([father])
                generic_filter.add_rule(rule)

            if mother:
                rule = SearchMotherName([mother])
                generic_filter.add_rule(rule)

            if child:
                rule = SearchChildName([child])
                generic_filter.add_rule(rule)

            if etype:
                rule = HasEvent([etype, '', '', ''])
                generic_filter.add_rule(rule)

            if rtype:
                rule = HasRelType([rtype])
                generic_filter.add_rule(rule)
                
            if note:
                if regex:
                    rule = HasNoteRegexp([note])
                else:
                    rule = HasNoteMatchingSubstringOf([note])
                generic_filter.add_rule(rule)

	    if self.generic.get_active() != 0:
		model = self.generic.get_model()
		iter = self.generic.get_active_iter()
		obj = model.get_value(iter, 0)
		rule = MatchesFilter([obj])
		generic_filter.add_rule(rule)

        return generic_filter

