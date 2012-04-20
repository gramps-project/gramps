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
import gtk

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gui import widgets
import gen.lib

from Filters.SideBar import SidebarFilter
from Filters import GenericFilterFactory, build_filter_model, Rules
from Filters.Rules.Family import (RegExpIdOf, HasIdOf, RegExpFatherName, 
                                  SearchFatherName, RegExpMotherName, 
                                  SearchMotherName, RegExpChildName, 
                                  SearchChildName, HasEvent, HasRelType, 
                                  HasTag, HasNoteRegexp, 
                                  HasNoteMatchingSubstringOf, MatchesFilter)

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
        
        self.filter_event = gen.lib.Event()
        self.filter_event.set_type((gen.lib.EventType.CUSTOM, u''))
        self.etype = gtk.ComboBoxEntry()

        self.family_stub = gen.lib.Family()
        self.family_stub.set_relationship((gen.lib.FamilyRelType.CUSTOM, u''))
        self.rtype = gtk.ComboBoxEntry()
        
        self.event_menu = widgets.MonitoredDataType(
            self.etype,
            self.filter_event.set_type,
            self.filter_event.get_type)

        self.rel_menu = widgets.MonitoredDataType(
            self.rtype,
            self.family_stub.set_relationship,
            self.family_stub.get_relationship)
        
        self.filter_note = widgets.BasicEntry()

        self.filter_regex = gtk.CheckButton(_('Use regular expressions'))

        self.tag = gtk.ComboBox()
        self.generic = gtk.ComboBox()

        SidebarFilter.__init__(self, dbstate, uistate, "Family")

    def create_widget(self):
        cell = gtk.CellRendererText()
        cell.set_property('width', self._FILTER_WIDTH)
        cell.set_property('ellipsize', self._FILTER_ELLIPSIZE)
        self.generic.pack_start(cell, True)
        self.generic.add_attribute(cell, 'text', 0)
        self.on_filters_changed('Family')

        cell = gtk.CellRendererText()
        cell.set_property('width', self._FILTER_WIDTH)
        cell.set_property('ellipsize', self._FILTER_ELLIPSIZE)
        self.tag.pack_start(cell, True)
        self.tag.add_attribute(cell, 'text', 0)

        self.etype.child.set_width_chars(5)
        self.rtype.child.set_width_chars(5)

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
        self.filter_id.set_text(u'')
        self.filter_father.set_text(u'')
        self.filter_mother.set_text(u'')
        self.filter_child.set_text(u'')
        self.filter_note.set_text(u'')
        self.etype.child.set_text(u'')
        self.rtype.child.set_text(u'')
        self.tag.set_active(0)
        self.generic.set_active(0)

    def get_filter(self):
        gid = unicode(self.filter_id.get_text()).strip()
        father = unicode(self.filter_father.get_text()).strip()
        mother = unicode(self.filter_mother.get_text()).strip()
        child = unicode(self.filter_child.get_text()).strip()
        note = unicode(self.filter_note.get_text()).strip()
        etype = self.filter_event.get_type().xml_str()
        rtype = self.family_stub.get_relationship().xml_str()
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
                if regex:
                    rule = RegExpIdOf([gid])
                else:
                    rule = HasIdOf([gid])
                generic_filter.add_rule(rule)

            if father:
                if regex:
                    rule = RegExpFatherName([father])
                else:
                    rule = SearchFatherName([father])
                generic_filter.add_rule(rule)

            if mother:
                if regex:
                    rule = RegExpMotherName([mother])
                else:
                    rule = SearchMotherName([mother])
                generic_filter.add_rule(rule)

            if child:
                if regex:
                    rule = RegExpChildName([child])
                else:
                    rule = SearchChildName([child])
                generic_filter.add_rule(rule)

            if etype:
                rule = HasEvent([etype, u'', u'', u'', u''], use_regex=regex)
                generic_filter.add_rule(rule)

            if rtype:
                rule = HasRelType([rtype], use_regex=regex)
                generic_filter.add_rule(rule)
                
            if note:
                if regex:
                    rule = HasNoteRegexp([note])
                else:
                    rule = HasNoteMatchingSubstringOf([note])
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
            obj = unicode(model.get_value(node, 0))
            rule = MatchesFilter([obj])
            generic_filter.add_rule(rule)

        return generic_filter

    def on_filters_changed(self, name_space):
        if name_space == 'Family':
            all_filter = GenericFamilyFilter()
            all_filter.set_name(_("None"))
            all_filter.add_rule(Rules.Family.AllFamilies([]))
            self.generic.set_model(build_filter_model('Family', [all_filter]))
            self.generic.set_active(0)

    def on_tags_changed(self, tag_list):
        """
        Update the list of tags in the tag filter.
        """
        model = gtk.ListStore(str)
        model.append(('',))
        for tag_name in tag_list:
            model.append((tag_name,))
        self.tag.set_model(model)
        self.tag.set_active(0)
