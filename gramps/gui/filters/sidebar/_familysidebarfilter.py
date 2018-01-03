#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2010       Nick Hall
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
# Python modules
#
#-------------------------------------------------------------------------
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

#-------------------------------------------------------------------------
#
# gtk
#
#-------------------------------------------------------------------------
from gi.repository import Gtk

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from ... import widgets
from gramps.gen.lib import Event, EventType, Family, FamilyRelType
from .. import build_filter_model
from . import SidebarFilter
from gramps.gen.filters import GenericFilterFactory, rules
from gramps.gen.filters.rules.family import (RegExpIdOf, RegExpFatherName,
                                             RegExpMotherName, RegExpChildName,
                                             HasEvent, HasRelType, HasTag,
                                             HasNoteRegexp, MatchesFilter)

GenericFamilyFilter = GenericFilterFactory('Family')
#-------------------------------------------------------------------------
#
# FamilySidebarFilter class
#
#-------------------------------------------------------------------------
class FamilySidebarFilter(SidebarFilter):

    def __init__(self, dbstate, uistate, clicked):
        self.clicked_func = clicked
        self.filter_id = widgets.BasicEntry()
        self.filter_father = widgets.BasicEntry()
        self.filter_mother = widgets.BasicEntry()
        self.filter_child = widgets.BasicEntry()

        self.filter_event = Event()
        self.filter_event.set_type((EventType.CUSTOM, ''))
        self.etype = Gtk.ComboBox(has_entry=True)
        if dbstate.is_open():
            self.custom_types = dbstate.db.get_event_types()
        else:
            self.custom_types = []

        self.event_menu = widgets.MonitoredDataType(
            self.etype,
            self.filter_event.set_type,
            self.filter_event.get_type,
            custom_values=self.custom_types)

        self.filter_family = Family()
        self.filter_family.set_relationship((FamilyRelType.CUSTOM, ''))
        self.rtype = Gtk.ComboBox(has_entry=True)
        if dbstate.is_open():
            self.custom_types = dbstate.db.get_family_relation_types()
        else:
            self.custom_types = []

        self.rel_menu = widgets.MonitoredDataType(
            self.rtype,
            self.filter_family.set_relationship,
            self.filter_family.get_relationship,
            custom_values=self.custom_types)

        self.filter_note = widgets.BasicEntry()

        self.filter_regex = Gtk.CheckButton(label=_('Use regular expressions'))

        self.tag = Gtk.ComboBox()
        self.generic = Gtk.ComboBox()

        SidebarFilter.__init__(self, dbstate, uistate, "Family")

    def create_widget(self):
        cell = Gtk.CellRendererText()
        cell.set_property('width', self._FILTER_WIDTH)
        cell.set_property('ellipsize', self._FILTER_ELLIPSIZE)
        self.generic.pack_start(cell, True)
        self.generic.add_attribute(cell, 'text', 0)
        self.on_filters_changed('Family')

        cell = Gtk.CellRendererText()
        cell.set_property('width', self._FILTER_WIDTH)
        cell.set_property('ellipsize', self._FILTER_ELLIPSIZE)
        self.tag.pack_start(cell, True)
        self.tag.add_attribute(cell, 'text', 0)

        self.etype.get_child().set_width_chars(5)
        self.rtype.get_child().set_width_chars(5)

        self.add_text_entry(_('ID'), self.filter_id)
        self.add_text_entry(_('Father'), self.filter_father)
        self.add_text_entry(_('Mother'), self.filter_mother)
        self.add_text_entry(_('Child'), self.filter_child)
        self.add_entry(_('Relationship'), self.rtype)
        self.add_entry(_('Family Event'), self.etype)
        self.add_text_entry(_('Family Note'), self.filter_note)
        self.add_entry(_('Tag'), self.tag)
        self.add_filter_entry(_('Custom filter'), self.generic)
        self.add_regex_entry(self.filter_regex)

    def clear(self, obj):
        self.filter_id.set_text('')
        self.filter_father.set_text('')
        self.filter_mother.set_text('')
        self.filter_child.set_text('')
        self.filter_note.set_text('')
        self.etype.get_child().set_text('')
        self.rtype.get_child().set_text('')
        self.tag.set_active(0)
        self.generic.set_active(0)

    def get_filter(self):
        gid = str(self.filter_id.get_text()).strip()
        father = str(self.filter_father.get_text()).strip()
        mother = str(self.filter_mother.get_text()).strip()
        child = str(self.filter_child.get_text()).strip()
        note = str(self.filter_note.get_text()).strip()
        etype = self.filter_event.get_type().xml_str()
        rtype = self.filter_family.get_relationship().xml_str()
        regex = self.filter_regex.get_active()
        tag = self.tag.get_active() > 0
        generic = self.generic.get_active() > 0

        empty = not (gid or father or mother or child or note
                     or regex or etype or rtype or tag or generic)
        if empty:
            generic_filter = None
        else:
            generic_filter = GenericFamilyFilter()
            if gid:
                rule = RegExpIdOf([gid], use_regex=regex)
                generic_filter.add_rule(rule)

            if father:
                rule = RegExpFatherName([father], use_regex=regex)
                generic_filter.add_rule(rule)

            if mother:
                rule = RegExpMotherName([mother], use_regex=regex)
                generic_filter.add_rule(rule)

            if child:
                rule = RegExpChildName([child], use_regex=regex)
                generic_filter.add_rule(rule)

            if etype:
                rule = HasEvent([etype, '', '', '', ''], use_regex=regex)
                generic_filter.add_rule(rule)

            if rtype:
                rule = HasRelType([rtype], use_regex=regex)
                generic_filter.add_rule(rule)

            if note:
                rule = HasNoteRegexp([note], use_regex=regex)
                generic_filter.add_rule(rule)

            # check the Tag
            if tag:
                model = self.tag.get_model()
                node = self.tag.get_active_iter()
                attr = model.get_value(node, 0)
                rule = HasTag([attr])
                generic_filter.add_rule(rule)

        if self.generic.get_active() != 0:
            model = self.generic.get_model()
            node = self.generic.get_active_iter()
            obj = str(model.get_value(node, 0))
            rule = MatchesFilter([obj])
            generic_filter.add_rule(rule)

        return generic_filter

    def on_filters_changed(self, name_space):
        if name_space == 'Family':
            all_filter = GenericFamilyFilter()
            all_filter.set_name(_("None"))
            all_filter.add_rule(rules.family.AllFamilies([]))
            self.generic.set_model(build_filter_model('Family', [all_filter]))
            self.generic.set_active(0)

    def on_tags_changed(self, tag_list):
        """
        Update the list of tags in the tag filter.
        """
        model = Gtk.ListStore(str)
        model.append(('',))
        for tag_name in tag_list:
            model.append((tag_name,))
        self.tag.set_model(model)
        self.tag.set_active(0)
