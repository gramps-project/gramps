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
from gramps.gen.ggettext import gettext as _

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
from gramps.gui.filters import build_filter_model
from gramps.gui.filters.sidebar import SidebarFilter
from gramps.gen.filters import GenericFilterFactory, rules
from gramps.gen.filters.rules.media import (RegExpIdOf, HasIdOf, HasMedia, HasTag, 
                                     HasNoteRegexp, MatchesFilter, 
                                     HasNoteMatchingSubstringOf)

GenericMediaFilter = GenericFilterFactory('Media')
#-------------------------------------------------------------------------
#
# MediaSidebarFilter class
#
#-------------------------------------------------------------------------
class MediaSidebarFilter(SidebarFilter):

    def __init__(self, dbstate, uistate, clicked):
        self.clicked_func = clicked
        self.filter_id = widgets.BasicEntry()
        self.filter_title = widgets.BasicEntry()
        self.filter_type = widgets.BasicEntry()
        self.filter_path = widgets.BasicEntry()
        self.filter_date = widgets.BasicEntry()
        self.filter_note = widgets.BasicEntry()

        self.filter_regex = Gtk.CheckButton(_('Use regular expressions'))

        self.tag = Gtk.ComboBox()
        self.generic = Gtk.ComboBox()

        SidebarFilter.__init__(self, dbstate, uistate, "Media")

    def create_widget(self):
        cell = Gtk.CellRendererText()
        cell.set_property('width', self._FILTER_WIDTH)
        cell.set_property('ellipsize', self._FILTER_ELLIPSIZE)
        self.generic.pack_start(cell, True)
        self.generic.add_attribute(cell, 'text', 0)
        self.on_filters_changed('Media')

        cell = Gtk.CellRendererText()
        cell.set_property('width', self._FILTER_WIDTH)
        cell.set_property('ellipsize', self._FILTER_ELLIPSIZE)
        self.tag.pack_start(cell, True)
        self.tag.add_attribute(cell, 'text', 0)

        self.add_text_entry(_('ID'), self.filter_id)
        self.add_text_entry(_('Title'), self.filter_title)
        self.add_text_entry(_('Type'), self.filter_type)
        self.add_text_entry(_('Path'), self.filter_path)
        self.add_text_entry(_('Date'), self.filter_date)
        self.add_text_entry(_('Note'), self.filter_note)
        self.add_entry(_('Tag'), self.tag)
        self.add_filter_entry(_('Custom filter'), self.generic)
        self.add_regex_entry(self.filter_regex)

    def clear(self, obj):
        self.filter_id.set_text('')
        self.filter_title.set_text('')
        self.filter_type.set_text('')
        self.filter_path.set_text('')
        self.filter_date.set_text('')
        self.filter_note.set_text('')
        self.tag.set_active(0)
        self.generic.set_active(0)

    def get_filter(self):
        gid = unicode(self.filter_id.get_text()).strip()
        title = unicode(self.filter_title.get_text()).strip()
        mime = unicode(self.filter_type.get_text()).strip()
        path = unicode(self.filter_path.get_text()).strip()
        date = unicode(self.filter_date.get_text()).strip()
        note = unicode(self.filter_note.get_text()).strip()
        regex = self.filter_regex.get_active()
        tag = self.tag.get_active() > 0
        gen = self.generic.get_active() > 0

        empty = not (gid or title or mime or path or date
                     or note or regex or tag or gen)
        if empty:
            generic_filter = None
        else:
            generic_filter = GenericMediaFilter()
            if gid:
                if regex:
                    rule = RegExpIdOf([gid])
                else:
                    rule = HasIdOf([gid])
                generic_filter.add_rule(rule)

            rule = HasMedia([title, mime, path, date], use_regex=regex)
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
        if name_space == 'Media':
            all_filter = GenericMediaFilter()
            all_filter.set_name(_("None"))
            all_filter.add_rule(rules.media.AllMedia([]))
            self.generic.set_model(build_filter_model('Media', [all_filter]))
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
